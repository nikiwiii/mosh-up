import os
import random
import subprocess

from ..ffmpeg import convert_to_avi_mpeg4, recombine_with_original_audio
from ..avi import find_video_frames, find_vop, VOP_TYPE_I
from ..utils import cleanup_temp_files


def mosh_cyber_glitch(ffmpeg, input_path, output_path, options, progress_callback=None):
    """
    Bitwise Payload Corruptor.
    Swaps and flips macroblock bytes in P-frame payloads.
    """
    temp_dir = os.path.dirname(output_path) or "."
    temp_in_avi = os.path.join(temp_dir, "_temp_in.avi")
    temp_out_avi = os.path.join(temp_dir, "_temp_out.avi")

    try:
        convert_to_avi_mpeg4(ffmpeg, input_path, temp_in_avi, progress_callback)

        corrupt_rate = options.get('corrupt_rate', 0.05)
        intensity = options.get('intensity', 0.02)
        seed = int(options.get('seed', 42))
        random.seed(seed)

        with open(temp_in_avi, 'rb') as f:
            data = bytearray(f.read())

        frames = find_video_frames(data)
        if not frames:
            raise RuntimeError("No video frames found in AVI file!")

        modified_data = bytearray()
        modified_data.extend(data[:frames[0][0]])
        total_frames = len(frames)

        for idx, (f_pos, f_size) in enumerate(frames):
            if progress_callback and idx % 40 == 0:
                pct = 30 + int(55 * (idx / total_frames))
                progress_callback(pct, f"Injecting Cyber Glitch bitwise errors ({idx}/{total_frames})...")

            chunk_header = data[f_pos:f_pos + 8]
            payload = bytearray(data[f_pos + 8:f_pos + 8 + f_size])

            vop_idx, vop_type = find_vop(payload)
            is_iframe = (vop_type == VOP_TYPE_I)

            if not is_iframe and idx > 2 and random.random() < corrupt_rate:
                safe_start = max(16, vop_idx + 8 if vop_idx != -1 else 16)
                num_bytes = int(len(payload) * intensity)
                for _ in range(num_bytes):
                    b_idx = random.randint(safe_start, len(payload) - 1)
                    payload[b_idx] = (payload[b_idx] ^ random.randint(1, 255)) & 0xFF

            modified_data.extend(chunk_header)
            modified_data.extend(payload)

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
            progress_callback(100, "Done! Cyber Glitch effect generated.")
        return True

    finally:
        cleanup_temp_files(temp_in_avi, temp_out_avi)
