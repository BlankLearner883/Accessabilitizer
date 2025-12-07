#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import tempfile
from faster_whisper import WhisperModel
from tqdm import tqdm

#Find FFmpeg
def find_ffmpeg():
    # Script folder or EXE folder
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    # Check bundled ffmpeg
    local_ffmpeg = os.path.join(base_dir, "ffmpeg", "bin", "ffmpeg.exe")
    if os.path.isfile(local_ffmpeg):
        return local_ffmpeg

    # Fallback: system FFmpeg
    if shutil.which("ffmpeg"):
        return "ffmpeg"

    print("\n FFmpeg not found. Please include:")
    print("   ffmpeg/bin/ffmpeg.exe")
    print("next to your auto_subtitle.py or auto_subtitle.exe\n")
    input("Press Enter to exit...")
    sys.exit(1)


# SRT timestamp formatting
def ts_format(seconds):
    millis = int((seconds % 1) * 1000)
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02},{millis:03}"


#Main
def main():
    if len(sys.argv) != 2:
        print("Usage: auto_subtitle.py path/to/video")
        input("\nPress Enter to exit...")
        return

    video_path = sys.argv[1]

    if not os.path.isfile(video_path):
        print(f"\nFile does not exist:\n{video_path}")
        input("\nPress Enter to exit...")
        return

    base_name, ext = os.path.splitext(os.path.basename(video_path))
    out_path = os.path.join(os.path.dirname(video_path), f"{base_name}_subtitled{ext}")

    # Temporary SRT file
    srt_path = os.path.join(tempfile.gettempdir(), f"{base_name}.srt")

    #GPU Detection
    print("\nDetecting GPU…")
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using {device.upper()}")
    except:
        device = "cpu"
        print("PyTorch not installed — using CPU")

    #Load Whisper
    print("\n🔊 Loading Whisper model (medium)…")
    model = WhisperModel("medium", device=device)

    print("\n🎙️ Transcribing… (may take a while)\n")
    segments, info = model.transcribe(video_path)
    segments = list(segments)

    #Write SRT with progress bar
    print("📝 Generating subtitles…")
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(tqdm(segments, desc="Writing .srt"), start=1):
            start = ts_format(seg.start)
            end = ts_format(seg.end)
            text = seg.text.strip()
            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

    #Burn subtitles
    ffmpeg_path = find_ffmpeg()
    # Escape Windows path for subtitles filter
    escaped_srt = srt_path.replace("\\", "\\\\")
    cmd = [
        ffmpeg_path,
        "-i", video_path,
        "-vf", f"subtitles='{escaped_srt}'",
        "-c:a", "copy",
        out_path
    ]

    print("\nBurning subtitles into video…\n")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("FFmpeg failed to encode the video.")
        input("Press Enter to exit...")
        return

    print("\nDONE!")
    print("Output saved as:")
    print("   " + out_path)
    input("\nPress Enter to exit...")

# -------------------- Entry point --------------------
if __name__ == "__main__":
    main()
