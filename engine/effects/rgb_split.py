import os
import random
import subprocess
from collections import deque
import cv2
import numpy as np

from ..ffmpeg import recombine_with_original_audio
from ..utils import cleanup_temp_files


def mosh_rgb_split(ffmpeg, input_path, output_path, options, progress_callback=None):
    """
    RGB Channel Split Datamosh Effect.
    Splits video into independent color channels (Red, Green, Blue) with:
    - Temporal delay (R leads, G intermediate, B lags) creating dynamic rainbow motion fringing
    - Spatial offset (chromatic aberration translation dx, dy)
    - VHS scanline jitter (occasional random horizontal slice displacements)
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video file: {input_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100

    temp_dir = os.path.dirname(output_path) or "."
    temp_video = os.path.join(temp_dir, "_temp_rgb_split.mp4")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

    temporal_delay = int(options.get('rgb_delay', 4))
    spatial_shift = int(options.get('rgb_shift', 8))
    jitter_pct = float(options.get('rgb_jitter', 10))
    blend = float(options.get('rgb_blend', 1.0))
    direction = options.get('rgb_direction', 'horizontal')  # 'horizontal', 'diagonal', 'vertical'

    # Precalculate shift offsets
    if direction == 'vertical':
        dx, dy = 0, spatial_shift
    elif direction == 'diagonal':
        dx, dy = spatial_shift, max(1, spatial_shift // 2)
    else:  # horizontal default
        dx, dy = spatial_shift, 0

    # Max buffer size: blue delays by 2 * temporal_delay frames
    max_buf_len = max(1, temporal_delay * 2 + 1)
    frame_buffer = deque(maxlen=max_buf_len)

    # Affine matrices for spatial shift
    M_r = np.float32([[1, 0, -dx], [0, 1, -dy]])
    M_b = np.float32([[1, 0, dx], [0, 1, dy]])

    frame_idx = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            frame_idx += 1
            if progress_callback and frame_idx % 15 == 0:
                pct = 10 + int(75 * (frame_idx / max(1, total_frames)))
                progress_callback(pct, f"Processing RGB Channel Split (frame {frame_idx}/{total_frames})...")

            frame_buffer.append(frame)

            # Retrieve frames with temporal delay
            if temporal_delay > 0:
                r_frame = frame_buffer[-1]
                g_idx = max(0, len(frame_buffer) - 1 - temporal_delay)
                b_frame = frame_buffer[0]
                g_frame = frame_buffer[g_idx]
            else:
                r_frame = g_frame = b_frame = frame

            # Extract color planes (OpenCV BGR ordering)
            b_chan = b_frame[..., 0].copy()
            g_chan = g_frame[..., 1].copy()
            r_chan = r_frame[..., 2].copy()

            # Apply spatial chromatic shift if dx or dy != 0
            if dx != 0 or dy != 0:
                r_chan = cv2.warpAffine(r_chan, M_r, (width, height), borderMode=cv2.BORDER_REFLECT)
                b_chan = cv2.warpAffine(b_chan, M_b, (width, height), borderMode=cv2.BORDER_REFLECT)

            # Apply scanline jitter / glitch slice if triggered
            if jitter_pct > 0 and random.random() < (jitter_pct / 100.0):
                slice_h = random.randint(12, 45)
                y1 = random.randint(0, max(1, height - slice_h))
                y2 = min(height, y1 + slice_h)
                shift_amt = random.randint(-24, 24)
                if shift_amt != 0:
                    target_chan = r_chan if random.random() < 0.5 else b_chan
                    target_chan[y1:y2, :] = np.roll(target_chan[y1:y2, :], shift_amt, axis=1)

            # Merge modified channels back into BGR image
            merged = cv2.merge([b_chan, g_chan, r_chan])

            if blend < 0.99:
                output_frame = cv2.addWeighted(merged, blend, frame, 1.0 - blend, 0)
            else:
                output_frame = merged

            out.write(output_frame)

        cap.release()
        out.release()

        keep_audio = options.get('keep_audio', True)
        if keep_audio:
            recombine_with_original_audio(ffmpeg, temp_video, input_path, output_path, progress_callback, shortest=True)
        else:
            cmd_remux = [ffmpeg, "-y", "-i", temp_video, "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path]
            subprocess.run(cmd_remux, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if progress_callback:
            progress_callback(100, "Done! RGB Channel Split completed successfully.")
        return True

    finally:
        cap.release()
        out.release()
        cleanup_temp_files(temp_video)
