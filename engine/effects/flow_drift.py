import os
import subprocess
import cv2
import numpy as np

from ..ffmpeg import recombine_with_original_audio
from ..utils import cleanup_temp_files


def mosh_flow_drift(ffmpeg, input_path, output_path, options, progress_callback=None):
    """
    Optical Flow Pixel Field Datamosh.
    Uses OpenCV Farneback Optical flow vectors to displace pixels and accumulate feedback motion.
    """
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video file: {input_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100

    temp_dir = os.path.dirname(output_path) or "."
    temp_video = os.path.join(temp_dir, "_temp_flow.mp4")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

    ret, prev_frame = cap.read()
    if not ret:
        cap.release()
        raise RuntimeError("Empty video file!")

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    accumulated_canvas = prev_frame.astype(np.float32)

    flow_scale = options.get('flow_scale', 2.5)
    decay = options.get('decay', 0.85)

    frame_idx = 0
    grid_y, grid_x = np.mgrid[0:height, 0:width].astype(np.float32)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_idx += 1
            if progress_callback and frame_idx % 10 == 0:
                pct = 10 + int(75 * (frame_idx / max(1, total_frames)))
                progress_callback(pct, f"Synthesizing optical flow vector field (frame {frame_idx}/{total_frames})...")

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray, None,
                pyr_scale=0.5, levels=3, winsize=15,
                iterations=3, poly_n=5, poly_sigma=1.2, flags=0
            )

            map_x = (grid_x + flow[..., 0] * flow_scale).astype(np.float32)
            map_y = (grid_y + flow[..., 1] * flow_scale).astype(np.float32)

            warped_canvas = cv2.remap(
                accumulated_canvas, map_x, map_y,
                interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
            )

            accumulated_canvas = warped_canvas * decay + frame.astype(np.float32) * (1.0 - decay)
            output_frame = np.clip(accumulated_canvas, 0, 255).astype(np.uint8)

            out.write(output_frame)
            prev_gray = gray

        cap.release()
        out.release()

        keep_audio = options.get('keep_audio', True)
        if keep_audio:
            recombine_with_original_audio(ffmpeg, temp_video, input_path, output_path, progress_callback, shortest=True)
        else:
            cmd_remux = [ffmpeg, "-y", "-i", temp_video, "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path]
            subprocess.run(cmd_remux, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if progress_callback:
            progress_callback(100, "Done! Optical Flow Drift effect completed.")
        return True

    finally:
        cap.release()
        out.release()
        cleanup_temp_files(temp_video)
