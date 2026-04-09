"""
Accessibility tools launcher. Runs the various accessibility scripts from one entry point.

Usage:
  python accessible.py subtitle <video> [audio_subtitle options...]
  python accessible.py flicker <video> [threshold]
  python accessible.py dyslexia <input.html>
  python accessible.py caption <input.html>

Examples:
  python accessible.py subtitle my.mp4 --no-pause
  python accessible.py flicker my.mp4 0.4
  python accessible.py dyslexia page.html
  python accessible.py caption page.html
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def script_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def run_script(script_name: str, args: list[str]) -> int:
    """Run a Python script in this package's directory. Returns exit code."""
    path = os.path.join(script_dir(), script_name)
    if not os.path.isfile(path):
        print(f"Error: script not found: {path}", file=sys.stderr)
        return 1
    cmd = [sys.executable, path] + args
    return subprocess.run(cmd, cwd=script_dir()).returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="accessible",
        description="Run accessibility tools: subtitle, flicker, dyslexia, caption.",
    )
    parser.add_argument(
        "mode",
        choices=["subtitle", "flicker", "dyslexia", "caption"],
        help="Which tool to run",
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Input file (video for subtitle/flicker, .html for dyslexia/caption)",
    )
    parser.add_argument(
        "extra",
        nargs=argparse.REMAINDER,
        default=[],
        help="Extra arguments passed to the underlying script (e.g. --no-pause for subtitle, threshold for flicker)",
    )

    args = parser.parse_args()

    if not args.path:
        if args.mode in ("subtitle", "flicker"):
            print("Usage: python accessible.py", args.mode, "<video> [options...]", file=sys.stderr)
        else:
            print("Usage: python accessible.py", args.mode, "<input.html>", file=sys.stderr)
        return 1

    if args.mode == "subtitle":
        return run_script("audio_subtitle.py", [args.path] + args.extra)

    if args.mode == "flicker":
        # flicker.py expects: video_path, gray_threshold (float)
        threshold = "0.4"
        if args.extra:
            threshold = args.extra[0]
        return run_script("flicker.py", [args.path, threshold])

    if args.mode == "dyslexia":
        return run_script("dyslexia.py", [args.path])

    if args.mode == "caption":
        return run_script("image_caption.py", [args.path, "--yes"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
