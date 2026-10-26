import os
import struct
import subprocess

from ..ffmpeg import convert_to_avi_mpeg4, recombine_with_original_audio
from ..avi import find_video_frames, is_iframe
from ..utils import cleanup_temp_files


def mosh_volcano_melt(ffmpeg, input_path, output_path, options, progress_callback=None):
    """
    I-Frame Removal Datamosh.
    Removes/replaces I-frames (keyframes) between start_time and end_time (in seconds) or percentage.
    """
    temp_dir = os.path.dirname(output_path) or "."
    temp_in_avi = os.path.join(temp_dir, "_temp_in.avi")
    temp_out_avi = os.path.join(temp_dir, "_temp_out.avi")

    try:
        convert_to_avi_mpeg4(ffmpeg, input_path, temp_in_avi, progress_callback)

        if progress_callback:
            progress_callback(30, "Analyzing AVI keyframes...")

        with open(temp_in_avi, 'rb') as f:
            data = bytearray(f.read())

        frames = find_video_frames(data)
        if not frames:
            raise RuntimeError("No video frames found in AVI file!")

        total_frames = len(frames)

        start_sec = options.get('start_sec')
        end_sec = options.get('end_sec')
        video_duration = options.get('video_duration', 0.0)

        if start_sec is not None and end_sec is not None and video_duration > 0:
            start_frame = int(total_frames * (start_sec / video_duration))
            end_frame = int(total_frames * (end_sec / video_duration))
        else:
            start_pct = options.get('start_pct', 0.0) / 100.0
            end_pct = options.get('end_pct', 100.0) / 100.0
            start_frame = int(total_frames * start_pct)
            end_frame = int(total_frames * end_pct)

        start_frame = max(0, min(total_frames - 1, start_frame))
        end_frame = max(start_frame, min(total_frames, end_frame))

        if progress_callback:
            progress_callback(50, f"Modifying I-Frames (frames: {start_frame}-{end_frame}/{total_frames})...")

        modified_data = bytearray()
        last_pframe_payload = None

        first_frame_pos = frames[0][0]
        modified_data.extend(data[:first_frame_pos])

        for idx, (f_pos, f_size) in enumerate(frames):
            if progress_callback and idx % 50 == 0:
                pct = 50 + int(35 * (idx / total_frames))
                progress_callback(pct, f"Processing frame {idx}/{total_frames}...")

            chunk_data = data[f_pos:f_pos + 8 + f_size]
            payload = data[f_pos + 8:f_pos + 8 + f_size]

            is_frame_i = is_iframe(payload)

            if is_frame_i and idx > 0 and (start_frame <= idx <= end_frame):
                if last_pframe_payload is not None:
                    new_chunk = bytearray(chunk_data[:8]) + last_pframe_payload
                    struct.pack_into('<I', new_chunk, 4, len(last_pframe_payload))
                    modified_data.extend(new_chunk)
                else:
                    continue
            else:
                modified_data.extend(chunk_data)
                if not is_frame_i:
                    last_pframe_payload = payload

        last_frame_end = frames[-1][0] + 8 + frames[-1][1]
        if last_frame_end < len(data):
            modified_data.extend(data[last_frame_end:])

        with open(temp_out_avi, 'wb') as f:
            f.write(modified_data)

        keep_audio = options.get('keep_audio', True)
        if keep_audio:
            recombine_with_original_audio(ffmpeg, temp_out_avi, input_path, output_path, progress_callback, shortest=True)
        else:
            cmd_remux = [ffmpeg, "-y", "-i", temp_out_avi, "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path]
            subprocess.run(cmd_remux, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if progress_callback:
            progress_callback(100, "Done! Datamoshing completed successfully.")
        return True

    finally:
        cleanup_temp_files(temp_in_avi, temp_out_avi)
