import os
import subprocess

from ..ffmpeg import convert_to_avi_mpeg4, recombine_with_original_audio
from ..avi import find_video_frames, is_pframe
from ..utils import cleanup_temp_files


def mosh_motion_smear(ffmpeg, input_path, output_path, options, progress_callback=None):
    """
    P-Frame Duplication Datamosh.
    Duplicates P-frames to smear motion vectors endlessly.
    """
    temp_dir = os.path.dirname(output_path) or "."
    temp_in_avi = os.path.join(temp_dir, "_temp_in.avi")
    temp_out_avi = os.path.join(temp_dir, "_temp_out.avi")

    try:
        convert_to_avi_mpeg4(ffmpeg, input_path, temp_in_avi, progress_callback)

        dup_count = int(options.get('repeat_count', 12))
        frequency = int(options.get('frequency', 5))

        with open(temp_in_avi, 'rb') as f:
            data = bytearray(f.read())

        frames = find_video_frames(data)
        if not frames:
            raise RuntimeError("No video frames found in AVI file!")

        modified_data = bytearray()
        modified_data.extend(data[:frames[0][0]])

        total_frames = len(frames)
        p_counter = 0

        for idx, (f_pos, f_size) in enumerate(frames):
            if progress_callback and idx % 40 == 0:
                pct = 30 + int(55 * (idx / total_frames))
                progress_callback(pct, f"Duplicating P vector frames ({idx}/{total_frames})...")

            chunk_data = data[f_pos:f_pos + 8 + f_size]
            payload = data[f_pos + 8:f_pos + 8 + f_size]

            is_frame_p = is_pframe(payload)

            modified_data.extend(chunk_data)

            if is_frame_p:
                p_counter += 1
                if p_counter % frequency == 0:
                    for _ in range(dup_count):
                        modified_data.extend(chunk_data)

        last_frame_end = frames[-1][0] + 8 + frames[-1][1]
        if last_frame_end < len(data):
            modified_data.extend(data[last_frame_end:])

        with open(temp_out_avi, 'wb') as f:
            f.write(modified_data)

        keep_audio = options.get('keep_audio', True)
        if keep_audio:
            recombine_with_original_audio(ffmpeg, temp_out_avi, input_path, output_path, progress_callback, shortest=False)
        else:
            cmd_remux = [ffmpeg, "-y", "-i", temp_out_avi, "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path]
            subprocess.run(cmd_remux, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if progress_callback:
            progress_callback(100, "Done! Motion Smear effect completed.")
        return True

    finally:
        cleanup_temp_files(temp_in_avi, temp_out_avi)
