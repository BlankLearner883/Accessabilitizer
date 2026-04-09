"""
Offline subtitle burner: transcribe video with faster-whisper and burn SRT into the video via FFmpeg.

Modes:
  - Video file:  python audio_subtitle.py video.mp4 [options]
  - HTML file:   python audio_subtitle.py page.html [options]
    Scans HTML for <video>/<source> tags, subtitles each video, and writes
    a new HTML file with the subtitled video paths substituted.

Output: next to input as <basename>_subtitled.<ext> (video) or <basename>_subtitled.html.
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
from html.parser import HTMLParser
from typing import List, Tuple, Optional, Dict

import progress_bar_util

# --- Try faster-whisper import ---
try:
    from faster_whisper import WhisperModel
except Exception as e:
    print("Missing dependency: faster-whisper (pip install faster-whisper)")
    print("Error:", e)
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



# Logging
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



# Video duration (replaces ffprobe)

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
            if container.streams.video:
                stream = container.streams.video[0]
                if stream.duration is not None and stream.time_base:
                    return float(stream.duration * stream.time_base)
            if container.duration is not None:
                try:
                    tb = float(container.time_base) if container.time_base else 1e-6
                except Exception:
                    tb = 1e-6
                return float(container.duration) * tb
    except Exception:
        return None
    return None



# FFmpeg helpers

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
        sys.exit(1)



# FFmpeg filter path escaping

def ffmpeg_escape_path_for_subtitles(path: str) -> str:
    p = str(pathlib.Path(path).resolve())
    if os.name == "nt":
        return p.replace("\\", "\\\\").replace(":", "\\:")
    else:
        return p.replace("'", r"\'")



# Parsing ffmpeg progress (stderr)

_time_re = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")


def ffmpeg_time_to_seconds(h: str, m: str, s: str) -> float:
    return int(h) * 3600 + int(m) * 60 + float(s)


def parse_ffmpeg_progress_time(line: str) -> Optional[float]:
    m = _time_re.search(line)
    if m:
        return ffmpeg_time_to_seconds(m.group(1), m.group(2), m.group(3))
    return None



# SRT writing

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
                start = float(getattr(seg, "start", 0.0))
                end = float(getattr(seg, "end", 0.0))
                text = str(getattr(seg, "text", "")).strip()
            f.write(f"{i}\n{srt_timestamp(start)} --> {srt_timestamp(end)}\n{text}\n\n")



# Build ASS force_style string for ffmpeg subtitles filter

def build_force_style_from_args(args) -> str:
    parts = []
    if args.font:
        parts.append(f"Fontname={args.font}")
    parts.append(f"Fontsize={args.font_size}")
    if args.font_color:
        parts.append(f"PrimaryColour={args.font_color}")
    parts.append(f"Outline={args.outline}")
    parts.append(f"Shadow={args.shadow}")
    if args.box:
        parts.append(f"BackColour={args.box_color}")
    if args.margin is not None:
        parts.append(f"MarginV={args.margin}")
    return ",".join(parts)



# Transcription function (faster-whisper)
def transcribe_with_progress(video_path: str, model_name: str, device: str, compute_type: str,
                             progress_bar: Optional[progress_bar_util.ProgressBar]) -> Tuple[List, dict]:
    logging.info("Transcription: loading model '%s' (device=%s, compute_type=%s)", model_name, device, compute_type)

    # Define model inside this function scope
    model = WhisperModel(model_name, device=device, compute_type=compute_type)

    # FIX: Extract audio to WAV first to prevent "IndexError: tuple index out of range"
    temp_audio = os.path.join(tempfile.gettempdir(), f"temp_{os.getpid()}.wav")
    ffmpeg_path = r"C:\Users\iniya\Documents\AuditoryNotifier\ffmpeg\bin\ffmpeg.exe"

    extract_cmd = [
        ffmpeg_path, "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        temp_audio
    ]
    subprocess.run(extract_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not os.path.exists(temp_audio) or os.path.getsize(temp_audio) == 0:
        logging.error("No audio track found or extraction failed for %s", video_path)
        return [], {}

    duration = get_video_duration_seconds(video_path)
    logging.info("Beginning transcription...")

    # Use the local 'model' variable to transcribe the extracted WAV file
    segments_iter, info = model.transcribe(temp_audio, beam_size=5)

    segments = []
    for seg in segments_iter:
        segments.append(seg)
        if progress_bar and duration:
            progress_bar.update(min(1.0, float(seg.end) / float(duration)))

    if progress_bar: progress_bar.end()

    # Clean up
    if os.path.exists(temp_audio): os.remove(temp_audio)

    return segments, info



# Encode (burn-in) function
def burn_subtitles_with_ffmpeg(video_path: str, srt_path: str, out_path: str, ffmpeg_path: str,
                               force_style: str,
                               encoding_progress_bar: Optional[progress_bar_util.ProgressBar]) -> bool:
    # ADD THIS CHECK:
    if ffmpeg_path is None:
        logging.error("FFmpeg path is None. Cannot proceed with subtitle burn-in.")
        return False

    escaped_srt = ffmpeg_escape_path_for_subtitles(srt_path)
    # ... rest of the function


# ----------------------------
# HTML video extraction and rewriting
# ----------------------------
class VideoSourceExtractor(HTMLParser):
    """Extract video source paths from <video> and <source> tags."""

    VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v", ".wmv", ".flv"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.video_sources: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() == "video":
            attr_map = {k.lower(): v for k, v in attrs}
            src = attr_map.get("src")
            if src:
                self.video_sources.append(src)
        elif tag.lower() == "source":
            attr_map = {k.lower(): v for k, v in attrs}
            src = attr_map.get("src")
            if src:
                self.video_sources.append(src)


def extract_video_sources(html_text: str) -> List[str]:
    parser = VideoSourceExtractor()
    parser.feed(html_text)
    return parser.video_sources


def resolve_video_path(html_file_path: str, src: str) -> Optional[str]:
    """Resolve a video src relative to the HTML file's directory."""
    html_dir = os.path.dirname(os.path.abspath(html_file_path))
    if os.path.isabs(src):
        return src if os.path.isfile(src) else None
    if src.startswith("/"):
        candidate = os.path.normpath(os.path.join(html_dir, src.lstrip("/")))
    else:
        candidate = os.path.normpath(os.path.join(html_dir, src))
    return candidate if os.path.isfile(candidate) else None


class VideoSrcRewriter(HTMLParser):
    """Rebuild HTML while replacing video source paths with subtitled versions."""

    def __init__(self, src_map: Dict[str, str]) -> None:
        """
        src_map: original src attribute value -> new src attribute value
        """
        super().__init__(convert_charrefs=True)
        self.src_map = src_map
        self.parts: List[str] = []

    def _attrs_to_string(self, attrs: List[Tuple[str, Optional[str]]]) -> str:
        out: List[str] = []
        for k, v in attrs:
            k_l = k.lower()
            if v is None:
                out.append(f" {k_l}")
            else:
                if k_l == "src" and v in self.src_map:
                    v = self.src_map[v]
                out.append(f' {k_l}="{self._escape_attr(v)}"')
        return "".join(out)

    @staticmethod
    def _escape_attr(value: str) -> str:
        return value.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        tag_l = tag.lower()
        self.parts.append(f"<{tag_l}{self._attrs_to_string(attrs)}>")

    def handle_startendtag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        tag_l = tag.lower()
        self.parts.append(f"<{tag_l}{self._attrs_to_string(attrs)} />")

    def handle_endtag(self, tag: str) -> None:
        self.parts.append(f"</{tag.lower()}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_comment(self, data: str) -> None:
        self.parts.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self.parts.append(f"<!{decl}>")

    def handle_pi(self, data: str) -> None:
        self.parts.append(f"<?{data}?>")

    def get_html(self) -> str:
        return "".join(self.parts)



# Config handling

def load_json_config(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.warning("Failed to read config %s: %s", path, e)
        return {}



# Process a single video file

def process_video(
    video_path: str,
    ffmpeg_path: str,
    device: str,
    compute_type: str,
    model_name: str,
    args,
) -> Optional[str]:
    """
    Transcribe and burn subtitles into a video.
    Returns the output path on success, None on failure.
    """
    base_name, ext = os.path.splitext(os.path.basename(video_path))
    out_path = os.path.join(os.path.dirname(video_path), f"{base_name}_subtitled{ext}")
    srt_path = os.path.join(tempfile.gettempdir(), f"{base_name}.srt")

    transcription_bar = progress_bar_util.ProgressBar(total_segment_count=args.bars)
    encoding_bar = progress_bar_util.ProgressBar(total_segment_count=args.bars)

    try:
        segments, info = transcribe_with_progress(video_path, model_name, device, compute_type, transcription_bar)
    except Exception as e:
        logging.exception("Transcription failed for %s: %s", video_path, e)
        return None

    if not segments:
        logging.warning("No transcription segments for %s, skipping.", video_path)
        return None

    try:
        write_srt(segments, srt_path)
        logging.info("SRT written to %s", srt_path)
    except Exception as e:
        logging.exception("Failed to write SRT for %s: %s", video_path, e)
        return None

    force_style = build_force_style_from_args(args)

    ok = burn_subtitles_with_ffmpeg(video_path, srt_path, out_path, ffmpeg_path, force_style, encoding_bar)
    if not ok:
        logging.error("Subtitle burn-in failed for %s.", video_path)
        return None

    logging.info("Subtitled video: %s", out_path)
    return out_path



# CLI / main

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="audio_subtitle",
        description="Offline subtitle burner (faster-whisper + bundled ffmpeg). Accepts a video file or an HTML file.",
    )
    p.add_argument("input", help="Input video file or HTML file path")
    p.add_argument("--config", help="Optional JSON config file path with default styling")
    p.add_argument("--font-size", type=int, default=24, help="Font size (default 24)")
    p.add_argument("--font-color", type=str, default="white", help="Font color name or #RRGGBB (default white)")
    p.add_argument("--outline", type=int, default=2, help="Outline thickness (default 2)")
    p.add_argument("--shadow", type=int, default=1, help="Shadow thickness (default 1)")
    p.add_argument("--font", type=str, default="Arial", help="Font name (default Arial)")
    p.add_argument("--box", action="store_true", help="Enable background box")
    p.add_argument("--box-color", type=str, default="black", help="Box color (default black)")
    p.add_argument("--margin", type=int, default=20, help="Bottom margin (MarginV) in pixels (default 20)")
    p.add_argument("--model", type=str, default="medium", help="Whisper model (tiny, base, small, medium, large)")
    p.add_argument("--device", type=str, choices=["auto", "cpu", "cuda"], default="auto", help="Device (auto/cpu/cuda)")
    p.add_argument("--compute-type", type=str, default=None, help="CTranslate2 compute_type override")
    p.add_argument("--bars", type=int, default=30, help="Progress bar granularity (default 30)")
    p.add_argument("--log-file", type=str, default=None, help="Optional log file path")
    p.add_argument("--no-pause", action="store_true", help="Don't wait for Enter at end")
    return p


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    setup_logging(args.log_file)

    input_path = args.input
    if not os.path.isfile(input_path):
        logging.error("File not found: %s", input_path)
        sys.exit(1)

    if args.config:
        cfg = load_json_config(args.config)
        for k, v in cfg.items():
            if getattr(args, k, None) in (None, False, ""):
                setattr(args, k, v)

    ffmpeg_path = require_executable("ffmpeg")

    device = "cpu"
    if args.device == "auto":
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            device = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
    else:
        device = args.device

    compute_type = args.compute_type
    if compute_type is None:
        compute_type = "float16" if device == "cuda" else "float32"

    _, ext = os.path.splitext(input_path)
    is_html = ext.lower() in (".html", ".htm")

    if is_html:
        # ---- HTML mode ----
        with open(input_path, "r", encoding="utf-8") as f:
            html_text = f.read()

        raw_sources = extract_video_sources(html_text)
        if not raw_sources:
            logging.warning("No video sources found in %s.", input_path)
            if not args.no_pause:
                input("\nPress Enter to exit...")
            return

        # Resolve and deduplicate
        src_to_real: Dict[str, str] = {}
        real_to_subtitled: Dict[str, str] = {}
        for src in raw_sources:
            real = resolve_video_path(input_path, src)
            if real is None:
                logging.warning("Video not found: %s (resolved from src=%r)", src, src)
                continue
            src_to_real[src] = real

        unique_videos = list(set(src_to_real.values()))
        logging.info("Found %d unique video(s) in HTML.", len(unique_videos))

        for video_path in unique_videos:
            subtitled = process_video(video_path, ffmpeg_path, device, compute_type, args.model, args)
            if subtitled:
                real_to_subtitled[video_path] = subtitled

        if not real_to_subtitled:
            logging.error("No videos were successfully subtitled.")
            if not args.no_pause:
                input("\nPress Enter to exit...")
            return

        # Build src -> subtitled_src map for HTML rewriting
        src_map: Dict[str, str] = {}
        for orig_src, real_path in src_to_real.items():
            if real_path in real_to_subtitled:
                subtitled_path = real_to_subtitled[real_path]
                # Use relative path from HTML file to subtitled video
                html_dir = os.path.dirname(os.path.abspath(input_path))
                try:
                    rel = os.path.relpath(subtitled_path, html_dir)
                except ValueError:
                    rel = subtitled_path
                src_map[orig_src] = rel

        rewriter = VideoSrcRewriter(src_map)
        rewriter.feed(html_text)
        out_html = rewriter.get_html()

        base, _ = os.path.splitext(input_path)
        output_html = base + "_subtitled.html"
        with open(output_html, "w", encoding="utf-8") as f:
            f.write(out_html)

        logging.info("HTML with subtitled videos written to %s", output_html)
    else:
        # ---- Single video mode ----
        result = process_video(input_path, ffmpeg_path, device, compute_type, args.model, args)
        if result:
            logging.info("All done! Output: %s", result)

    if not args.no_pause:
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
