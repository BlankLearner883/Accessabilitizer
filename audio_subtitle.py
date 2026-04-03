"""
Offline subtitle burner: transcribe video with faster-whisper and burn SRT into the video via FFmpeg.
Output: next to input as <basename>_subtitled.<ext>.
"""

from __future__ import annotations

import os
import sys
import subprocess
import shutil
import time
import math
import tempfile
import pathlib
import argparse
import json
import logging
import re
from typing import List, Tuple, Optional

import progress_bar_util

# --- Try faster-whisper import ---
try:
    from faster_whisper import WhisperModel
except Exception as e:
    print("Missing dependency: faster-whisper (pip install faster-whisper)")
    print("Error:", e)
    input("Press Enter to exit...")
    sys.exit(1)



def human_time(seconds: Optional[float]) -> str:
    if seconds is None or (isinstance(seconds, float) and math.isnan(seconds)):
        return "--:--"
    seconds = int(round(seconds))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


# ----------------------------
# Logging
# ----------------------------
def setup_logging(log_file: Optional[str] = None, level=logging.INFO):
    root = logging.getLogger()
    root.setLevel(level)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    handle = logging.StreamHandler(sys.stdout)
    handle.setFormatter(fmt)
    root.addHandler(handle)
    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(fmt)
        root.addHandler(fh)


# ----------------------------
# Video duration (replaces ffprobe)
# ----------------------------
def get_video_duration_seconds(filename: str) -> Optional[float]:
    """
    Get video duration in seconds using PyAV. Return None if unknown or on error.
    Requires: pip install av
    """
    try:
        import av
    except ImportError:
        return None
    try:
        with av.open(filename) as container:
            # Prefer first video stream duration (matches former ffprobe v:0 behavior)
            if container.streams.video:
                stream = container.streams.video[0]
                if stream.duration is not None and stream.time_base:
                    return float(stream.duration * stream.time_base)
            # Fallback to container duration (often in microseconds)
            if container.duration is not None:
                try:
                    tb = float(container.time_base) if container.time_base else 1e-6
                except Exception:
                    tb = 1e-6
                return float(container.duration) * tb
    except Exception:
        return None
    return None


# ----------------------------
# FFmpeg helpers
# ----------------------------
def find_executable_bundled_or_system(name: str) -> Optional[str]:
    """
    Prefer bundled ./ffmpeg/bin/<name> (or <name>.exe on Windows), else fallback to PATH.
    """
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    exe_name = name + (".exe" if os.name == "nt" else "")
    local = os.path.join(base_dir, "ffmpeg", "bin", exe_name)
    if os.path.isfile(local):
        return local
    which = shutil.which(name)
    return which


def require_executable(name: str) -> str:
    p = find_executable_bundled_or_system(name)
    if not p:
        logging.error("%s not found. Place it in ./ffmpeg/bin/ or install to PATH.", name)
        input("Press Enter to exit...")
        sys.exit(1)
    return p


# ----------------------------
# FFmpeg filter path escaping
# ----------------------------
def ffmpeg_escape_path_for_subtitles(path: str) -> str:
    p = str(pathlib.Path(path).resolve())
    if os.name == "nt":
        # double backslashes and escape colon
        return p.replace("\\", "\\\\").replace(":", "\\:")
    else:
        # escape single quotes for ffmpeg filter, will wrap in single quotes
        return p.replace("'", r"\'")


# ----------------------------
# Parsing ffmpeg progress (stderr)
# ----------------------------
_time_re = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")  # matches time=HH:MM:SS.xx


def ffmpeg_time_to_seconds(h: str, m: str, s: str) -> float:
    return int(h) * 3600 + int(m) * 60 + float(s)


def parse_ffmpeg_progress_time(line: str) -> Optional[float]:
    m = _time_re.search(line)
    if m:
        return ffmpeg_time_to_seconds(m.group(1), m.group(2), m.group(3))
    return None


# ----------------------------
# SRT writing
# ----------------------------
def srt_timestamp(seconds: float) -> str:
    ms = int((seconds - int(seconds)) * 1000)
    ss = int(seconds)
    hh = ss // 3600
    mm = (ss % 3600) // 60
    sec = ss % 60
    return f"{hh:02}:{mm:02}:{sec:02},{ms:03}"


def write_srt(segments: List, srt_path: str):
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            try:
                start = float(seg.start)
                end = float(seg.end)
                text = seg.text.strip()
            except Exception:
                # defensive fallback if segment fields differ
                start = float(getattr(seg, "start", 0.0))
                end = float(getattr(seg, "end", 0.0))
                text = str(getattr(seg, "text", "")).strip()
            f.write(f"{i}\n{srt_timestamp(start)} --> {srt_timestamp(end)}\n{text}\n\n")


# ----------------------------
# Build ASS force_style string for ffmpeg subtitles filter
# ----------------------------
def build_force_style_from_args(args) -> str:
    parts = []
    if args.font:
        parts.append(f"Fontname={args.font}")
    parts.append(f"Fontsize={args.font_size}")
    if args.font_color:
        # Accept names or #RRGGBB
        parts.append(f"PrimaryColour={args.font_color}")
    parts.append(f"Outline={args.outline}")
    parts.append(f"Shadow={args.shadow}")
    if args.box:
        parts.append(f"BackColour={args.box_color}")
    if args.margin is not None:
        parts.append(f"MarginV={args.margin}")
    return ",".join(parts)


# ----------------------------
# Transcription function (faster-whisper)
# ----------------------------
def transcribe_with_progress(video_path: str, model_name: str, device: str, compute_type: str,
                             progress_bar: Optional[progress_bar_util.ProgressBar]) -> Tuple[List, dict]:
    """
    Transcribe video using faster-whisper. Returns (segments_list, info_dict).
    Video duration (from get_video_duration_seconds) is used for progress bar when available.
    """
    logging.info("Transcription: loading model '%s' (device=%s, compute_type=%s)", model_name, device, compute_type)
    try:
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
    except Exception as e:
        logging.warning("Failed to load model with compute_type=%s: %s", compute_type, e)
        # if we tried float16 on CUDA and failed, auto-fallback to float32
        if device == "cuda" and compute_type and "16" in compute_type:
            logging.info("Retrying with compute_type=float32")
            model = WhisperModel(model_name, device=device, compute_type="float32")
        else:
            raise

    # attempt to get duration (seconds) for progress estimation
    duration = get_video_duration_seconds(video_path)
    if duration is not None:
        logging.info("Detected video duration: %s", human_time(duration))

    logging.info("Beginning transcription (this may take a while)...")
    start_time = time.time()

    segments_iter, info = model.transcribe(video_path, beam_size=5)
    segments = []
    last_time_reported = 0.0

    for seg in segments_iter:
        segments.append(seg)
        # faster-whisper provides seg.start, seg.end as floats (seconds)
        end_time = getattr(seg, "end", None)
        if end_time is None:
            continue
        # update progress bar based on time fraction if duration known
        if progress_bar and duration:
            frac = min(1.0, float(end_time) / float(duration)) if duration else 0.0
            progress_bar.update(frac)
            last_time_reported = float(end_time)

    # finalize progress bar
    if progress_bar:
        progress_bar.end()

    elapsed = time.time() - start_time
    logging.info("Transcription finished in %s (segments: %d)", human_time(elapsed), len(segments))
    return segments, info


# ----------------------------
# Encode (burn-in) function
# ----------------------------
def burn_subtitles_with_ffmpeg(video_path: str, srt_path: str, out_path: str, ffmpeg_path: str,
                               force_style: str,
                               encoding_progress_bar: Optional[progress_bar_util.ProgressBar]) -> bool:
    """
    Run ffmpeg to burn subtitles into video using subtitles filter with force_style.
    Returns True on success.
    """
    escaped_srt = ffmpeg_escape_path_for_subtitles(srt_path)
    # protect single quotes inside force_style just in case
    fs_escaped = force_style.replace("'", r"\'")
    vf_arg = f"subtitles='{escaped_srt}':force_style='{fs_escaped}'"

    cmd = [
        ffmpeg_path,
        "-y",
        "-i", video_path,
        "-vf", vf_arg,
        "-c:a", "copy",
        out_path
    ]
    logging.info("Running ffmpeg burn-in (this may take a while).")
    logging.debug("FFmpeg cmd: %s", " ".join(cmd))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)

    duration = get_video_duration_seconds(video_path)

    last_time = 0.0
    try:
        # read stderr line-by-line and update progress
        while True:
            line = proc.stderr.readline()
            if line == "" and proc.poll() is not None:
                break
            if not line:
                continue
            cur = parse_ffmpeg_progress_time(line)
            if cur is not None and encoding_progress_bar and duration:
                frac = min(1.0, float(cur) / float(duration))
                encoding_progress_bar.update(frac)
                last_time = cur
            # optionally, log ffmpeg output at debug level
            logging.debug("ffmpeg: ", line.strip())
    except KeyboardInterrupt:
        proc.kill()
        logging.warning("Encoding canceled by user.")
        return False

    proc.wait()
    if encoding_progress_bar:
        encoding_progress_bar.end()

    if proc.returncode != 0:
        logging.error("FFmpeg returned non-zero exit code: %s", proc.returncode)
        return False

    logging.info("FFmpeg finished successfully.")
    return True


# ----------------------------
# Config handling
# ----------------------------
def load_json_config(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.warning("Failed to read config %s: %s", path, e)
        return {}


# ----------------------------
# CLI / main
# ----------------------------
def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="audio_subtitle_prod", description="Offline subtitle burner (faster-whisper + bundled ffmpeg)")
    p.add_argument("video", help="Input video file path")
    p.add_argument("--config", help="Optional JSON config file path with default styling")
    # styling options (YouTube-style defaults)
    p.add_argument("--font-size", type=int, default=24, help="Font size (default 24)")
    p.add_argument("--font-color", type=str, default="white", help="Font color name or #RRGGBB (default white)")
    p.add_argument("--outline", type=int, default=2, help="Outline thickness (default 2)")
    p.add_argument("--shadow", type=int, default=1, help="Shadow thickness (default 1)")
    p.add_argument("--font", type=str, default="Arial", help="Font name (default Arial)")
    p.add_argument("--box", action="store_true", help="Enable background box (default False unless set in config)")
    p.add_argument("--box-color", type=str, default="black", help="Box color (default black)")
    p.add_argument("--margin", type=int, default=20, help="Bottom margin (MarginV) in pixels (default 20)")
    p.add_argument("--model", type=str, default="medium", help="Whisper model (tiny, base, small, medium, large)")
    p.add_argument("--device", type=str, choices=["auto", "cpu", "cuda"], default="auto", help="Device to run on (auto/cpu/cuda)")
    p.add_argument("--compute-type", type=str, default=None, help="CTranslate2 compute_type override (float16/float32/auto)")
    p.add_argument("--bars", type=int, default=30, help="Progress bar granularity (number of blocks, default 30)")
    p.add_argument("--log-file", type=str, default=None, help="Optional log file path")
    p.add_argument("--no-pause", action="store_true", help="Don't wait for Enter at end")
    return p


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    setup_logging(args.log_file)

    video = args.video
    if not os.path.isfile(video):
        logging.error("Video file not found: %s", video)
        input("Press Enter to exit...")
        return

    # Config file overrides defaults if provided
    if args.config:
        cfg = load_json_config(args.config)
        # apply config keys if present and not specified via CLI (CLI takes precedence)
        for k, v in cfg.items():
            if getattr(args, k, None) in (None, False, ""):
                setattr(args, k, v)

    # find ffmpeg (duration is obtained via get_video_duration_seconds / PyAV)
    ffmpeg_path = require_executable("ffmpeg")

    # determine device
    device = "cpu"
    if args.device == "auto":
        # try torch detection first (if available)
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            # fall back to environment hint
            device = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
    else:
        device = args.device

    # compute type selection
    compute_type = args.compute_type
    if compute_type is None:
        compute_type = "float16" if device == "cuda" else "float32"

    # Prepare output paths
    base_name, ext = os.path.splitext(os.path.basename(video))
    out_path = os.path.join(os.path.dirname(video), f"{base_name}_subtitled{ext}")
    srt_path = os.path.join(tempfile.gettempdir(), f"{base_name}.srt")

    # Prepare progress bars
    transcription_bar = progress_bar_util.ProgressBar(total_segment_count=args.bars)
    encoding_bar = progress_bar_util.ProgressBar(total_segment_count=args.bars)

    # Transcribe
    try:
        segments, info = transcribe_with_progress(video, args.model, device, compute_type, transcription_bar)
    except Exception as e:
        logging.exception("Transcription failed: %s", e)
        return

    if not segments:
        logging.error("No transcription segments returned.")
        return

    # Write SRT
    try:
        write_srt(segments, srt_path)
        logging.info("SRT written to %s", srt_path)
    except Exception as e:
        logging.exception("Failed to write SRT: %s", e)
        return

    # Build force_style
    force_style = build_force_style_from_args(args)
    if args.box:
        # Append BackColour; note: opacity handling is complex, not all FFmpeg builds support alpha in BackColour
        force_style += f",BackColour={args.box_color}"

    # Burn subtitles with ffmpeg
    ok = burn_subtitles_with_ffmpeg(video, srt_path, out_path, ffmpeg_path, force_style, encoding_bar)
    if not ok:
        logging.error("Subtitle burn-in failed.")
        return

    logging.info("All done! Output: %s", out_path)
    print("\n✅ Finished — output file:", out_path)
    if not args.no_pause:
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
