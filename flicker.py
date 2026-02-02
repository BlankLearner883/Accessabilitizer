import cv2
import sys
import progress_bar_util

print("Finished Importing")

# Sets up input video and determines basic characteristics
input_file_path = sys.argv[1]
video = cv2.VideoCapture(input_file_path)
print("Setting Up: █", end="\r")
fps = video.get(cv2.CAP_PROP_FPS)
print("Setting Up: ██", end="\r")
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
print("Setting Up: ███", end="\r")
duration = frame_count / fps
print("Setting Up ████", end="\r")
gray_history = []
gray_threshold = float(sys.argv[2])
gray_marked_frames = set()
gray_window = 5
width  = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
video_fps = video.get(cv2.CAP_PROP_FPS)
TEMPORAL_ALPHA = 0.6   # 0 = no smoothing, 1 = heavy smoothing
TEMPORAL_EPS   = 6.0   # minimum luma drop (in 0–255) to trigger smoothing

print("Setting Up █████", end="\r")
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(
    "output.mp4",
    fourcc,
    video_fps,
    (width, height)
)

#Setting up the Progress Bar
first_bar = progress_bar_util.ProgressBar(50)
second_bar = progress_bar_util.ProgressBar(50)

# Checks if the video file was opened successfully and whether the output file was created successfully
if not writer.isOpened():
    raise RuntimeError("ERROR: VideoWriter failed to open")

if not video.isOpened():
    print("ERROR: Video failed to open")
    sys.exit(1)

# Determines whether to use cupy or numpy
try:
    import cupy
    gpu_available = True
except ImportError:
    cp = None
    gpu_available = False

import numpy

xpy = cupy if gpu_available else numpy

# Converts numpy array into a cupy array if CUDA is available, else it returns the same array
def to_xpy(array):
    if gpu_available:
        return cupy.asarray(array)
    else:
        return array

def to_npy(array):
    if gpu_available:
        return cupy.asnumpy(array)
    else:
        return array

def absolute_luminance_clamp_batch(frames, max_luma):
    """
    frames: (B, H, W, 3) uint8 BGR
    max_luma: scalar or (B,) array, in 0–255
    """
    xp = cupy if gpu_available else numpy

    frames_f = to_xpy(frames).astype(xp.float32)

    # BGR → luminance (Rec.709)
    b = frames_f[..., 0]
    g = frames_f[..., 1]
    r = frames_f[..., 2]
    luma = 0.0722 * b + 0.7152 * g + 0.2126 * r  # (B, H, W)

    # Prepare per-frame max luma
    if xp.isscalar(max_luma):
        max_luma = xp.full((frames_f.shape[0],), max_luma, dtype=xp.float32)
    else:
        max_luma = to_xpy(max_luma).astype(xp.float32)

    max_luma = max_luma[:, None, None]

    # Compute scale (never amplify)
    scale = xp.minimum(1.0, max_luma / xp.maximum(luma, 1.0))

    # Apply scale uniformly to RGB
    frames_f *= scale[..., None]

    return to_npy(frames_f.clip(0, 255).astype(numpy.uint8))

def process_batch(frames, indices):
    global previous_output

    xp = cupy if gpu_available else numpy

    # Stack on CPU → transfer once
    batch = to_xpy(numpy.stack(frames)).astype(xp.float32)

    # Per-frame clamp limits
    max_luma = xp.array(
        [gray_threshold if idx in gray_marked_frames else 255 for idx in indices],
        dtype=xp.float32
    )

    # --- Luminance clamp (GPU) ---
    b, g, r = batch[..., 0], batch[..., 1], batch[..., 2]
    luma = 0.0722*b + 0.7152*g + 0.2126*r

    scale = xp.minimum(
        1.0,
        max_luma[:, None, None] / xp.maximum(luma, 1.0)
    )
    batch *= scale[..., None]

    # --- Temporal dampening (GPU) ---
    if previous_output is not None:
        prev = to_xpy(previous_output).astype(xp.float32)
        prev_luma = gpu_luma(prev)[0]

        for i, idx in enumerate(indices):
            if idx in gray_marked_frames:
                curr_luma = gpu_luma(batch[i:i+1])[0]
                drop = prev_luma.mean() - curr_luma.mean()

                if drop > TEMPORAL_EPS:
                    batch[i] = (
                        TEMPORAL_ALPHA * prev[0]
                      + (1 - TEMPORAL_ALPHA) * batch[i]
                    )

            prev = batch[i:i+1]
            prev_luma = gpu_luma(prev)[0]

    # Convert once → write
    out = to_npy(batch.clip(0, 255).astype(numpy.uint8))
    for f in out:
        writer.write(f)

    previous_output = out[-1:]


def gpu_luma(frames_f):
    # frames_f: (B, H, W, 3) float32 BGR (CuPy)
    b = frames_f[..., 0]
    g = frames_f[..., 1]
    r = frames_f[..., 2]
    return 0.0722 * b + 0.7152 * g + 0.2126 * r

#Detects all black and white frames that need to be altered

previous_avg = None
delta_percent = None
previous_gray = None
while True:
    video_not_done, frame = video.read()
    current_frame_number = video.get(cv2.CAP_PROP_POS_FRAMES) - 1

    #checks if all frames of the video have been iterated through
    if not video_not_done:
        first_bar.end()
        print("Finished scanning")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if previous_gray is not None:
        diff = cv2.absdiff(gray, previous_gray)
        area_ratio = (diff > 25).mean()  # fraction of pixels that changed

        if area_ratio >= 0.25:
            gray_marked_frames.add(current_frame_number)


    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray_mean = gray.mean()
    gray_history.append(gray_mean)

    # Checks to see if the average difference between the last 10 frames has been more than x
    past_average = 0
    if len(gray_history) < gray_window:
        previous_avg = gray_mean
        continue

    rolling_avg = round(sum(gray_history[-gray_window:]) / gray_window, 4)

    if previous_avg is not None:
        delta = round(abs(rolling_avg - previous_avg), 4)
        delta_percent = round(delta / 255, 4)

    if delta_percent is not None and delta_percent >= gray_threshold:
        gray_marked_frames.add(current_frame_number)

    current_completion_percent = current_frame_number / frame_count
    first_bar.update(current_completion_percent)
    previous_avg = rolling_avg
    previous_gray = gray.copy()

gray_marked_frames = set(gray_marked_frames)

#Goes through the frames sequentially, and if they are in the marked list, clamps its luminance and replaces the old one with the clamped one
video = cv2.VideoCapture(input_file_path)
previous_original = None
previous_output = None
frame_idx = 0
gpu_batch_size = 32
frames = []
frame_indices = []

while True:
    ok, frame = video.read()
    if ok:
        frames.append(frame)
        frame_indices.append(frame_idx)
        frame_idx += 1

    if len(frames) == gpu_batch_size or not ok:
        process_batch(frames, frame_indices)
        frames.clear()
        frame_indices.clear()
        if gpu_available:
            cupy.get_default_memory_pool().free_all_blocks()

    second_bar.update(frame_idx / frame_count)
    if not ok:
        break

second_bar.end()
writer.release()
video.release()
