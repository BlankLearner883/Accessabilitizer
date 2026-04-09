import sys
import os
import cv2
import numpy as np

# flicker.py around line 7
try:
    import cupy as cp
    # Smoke test: Try a small operation to ensure CUDA DLLs are actually found
    cp.array([1.0])
    GPU_AVAILABLE = True
except Exception as e:
    GPU_AVAILABLE = False
    # If it was a loading error (like missing DLL), notify the user
    if "cupy" in sys.modules:
        print(f"CuPy installed but GPU unavailable (missing DLLs). Falling back to CPU.")
    else:
        print("CuPy not available — falling back to CPU.")


def reduce_flicker_frame(prev, curr, alpha=0.3):
    """
    Simple temporal smoothing:
    result = alpha * curr + (1 - alpha) * prev
    """

    if GPU_AVAILABLE:
        curr_gpu = cp.asarray(curr, dtype=cp.float32)
        prev_gpu = cp.asarray(prev, dtype=cp.float32)

        result = alpha * curr_gpu + (1 - alpha) * prev_gpu
        result = cp.clip(result, 0, 255)

        return cp.asnumpy(result.astype(cp.uint8))
    else:
        # Ensure frames are of type uint8
        curr = cv2.convertScaleAbs(curr)
        prev = cv2.convertScaleAbs(prev)
        return cv2.addWeighted(curr, alpha, prev, 1 - alpha, 0)


def process_video(input_path, output_path):
    if os.path.exists(output_path):
        print(f"[SKIP] Already exists: {output_path}")
        return

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open video: {input_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Save to a temporary silent file first
    temp_v = output_path.replace(".mp4", "_silent.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_v, fourcc, fps, (width, height))

    prev_frame = None
    while True:
        ret, frame = cap.read()
        if not ret: break
        smoothed = reduce_flicker_frame(prev_frame, frame) if prev_frame is not None else frame
        out.write(smoothed)
        prev_frame = smoothed

    cap.release()
    out.release()

    # Use FFmpeg to merge original audio and fix the container for web playback
    import subprocess
    merge_cmd = [
        'ffmpeg', '-y',
        '-i', temp_v,       # Processed video
        '-i', input_path,   # Original file (for audio)
        '-c:v', 'libx264',  # Re-encode to H.264 for universal playback
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',      # Convert audio to AAC
        '-map', '0:v:0',    # Map video from temp
        '-map', '1:a:0?',   # Map audio from original (if it exists)
        '-shortest',
        output_path
    ]
    subprocess.run(merge_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(temp_v): os.remove(temp_v)
    print(f"[DONE] {output_path}")


def process_html(html_file):
    from bs4 import BeautifulSoup

    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    base_dir = os.path.dirname(html_file)

    for video in soup.find_all("video"):
        # Handle <video src="">
        if video.get("src"):
            src = video["src"]
            input_path = os.path.join(base_dir, src)

            new_name = os.path.splitext(src)[0] + "_flicker.mp4"
            output_path = os.path.join(base_dir, new_name)

            if os.path.exists(input_path):
                process_video(input_path, output_path)
                video["src"] = new_name

        # Handle <source src="">
        for source in video.find_all("source"):
            src = source.get("src")
            if not src:
                continue

            input_path = os.path.join(base_dir, src)
            new_name = os.path.splitext(src)[0] + "_flicker.mp4"
            output_path = os.path.join(base_dir, new_name)

            if os.path.exists(input_path):
                process_video(input_path, output_path)
                source["src"] = new_name

    output_html = html_file.replace(".html", "_flicker.html")

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print(f"[HTML DONE] {output_html}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python flicker_reduction.py file.html")
        sys.exit(1)

    process_html(sys.argv[1])