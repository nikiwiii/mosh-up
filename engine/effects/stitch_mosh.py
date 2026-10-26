import os
import struct
import subprocess
import cv2

from ..ffmpeg import convert_to_avi_mpeg4, recombine_with_original_audio
from ..avi import parse_avi_chunks, find_vop, update_avi_headers, VOP_TYPE_I, VOP_TYPE_P
from ..utils import cleanup_temp_files


def mosh_stitch(ffmpeg, input_a, input_b, output_path, options, progress_callback=None):
    """
    Cross-video Datamosh Transition.
    Stitches Video B onto Video A with keyframe replacement across Video B
    for smooth, 1x realtime motion vector playback.
    """
    temp_dir = os.path.dirname(output_path) or "."
    temp_avi_a = os.path.join(temp_dir, "_temp_a.avi")
    temp_avi_b = os.path.join(temp_dir, "_temp_b.avi")
    temp_out_avi = os.path.join(temp_dir, "_temp_stitch.avi")

    try:
        cap_a = cv2.VideoCapture(input_a)
        if not cap_a.isOpened():
            raise RuntimeError(f"Cannot open Video A: {input_a}")
        width_a = int(cap_a.get(cv2.CAP_PROP_FRAME_WIDTH))
        height_a = int(cap_a.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps_a = cap_a.get(cv2.CAP_PROP_FPS) or 30.0
        cap_a.release()

        target_res = (width_a, height_a, fps_a)

        if progress_callback:
            progress_callback(10, "Preparing first video file A...")
        convert_to_avi_mpeg4(ffmpeg, input_a, temp_avi_a)

        if progress_callback:
            progress_callback(35, f"Preparing second video file B (matching {width_a}x{height_a} @ {fps_a:.1f}fps)...")
        convert_to_avi_mpeg4(ffmpeg, input_b, temp_avi_b, target_res=target_res)

        with open(temp_avi_a, 'rb') as f:
            data_a = bytearray(f.read())
        with open(temp_avi_b, 'rb') as f:
            data_b = bytearray(f.read())

        movi_pos_a, idx1_pos_a, frames_a = parse_avi_chunks(data_a)
        movi_pos_b, idx1_pos_b, frames_b = parse_avi_chunks(data_b)

        if not frames_a or not frames_b:
            raise RuntimeError("Failed to read video frames from clips A/B!")

        modified_data = bytearray()
        movi_end_a = idx1_pos_a if idx1_pos_a != -1 else len(data_a)
        modified_data.extend(data_a[:movi_end_a])

        if progress_callback:
            progress_callback(65, "Synthesizing vector motion melt transition...")

        # Find last P-frame payload of Video A to replace Video B's keyframes
        last_pframe_payload_a = None
        for c_id, f_pos, f_size in reversed(frames_a):
            if c_id == b'00dc':
                payload = data_a[f_pos + 8:f_pos + 8 + f_size]
                _, vop_type = find_vop(payload)
                if vop_type == VOP_TYPE_P:
                    last_pframe_payload_a = payload
                    break

        video_b_count = 0
        last_pframe_payload_b = last_pframe_payload_a

        for idx, (c_id, f_pos, f_size) in enumerate(frames_b):
            chunk_bytes = bytearray(data_b[f_pos:f_pos + 8 + f_size + (f_size % 2)])
            payload = data_b[f_pos + 8:f_pos + 8 + f_size]

            if c_id == b'00dc':
                _, vop_type = find_vop(payload)
                is_iframe = (vop_type == VOP_TYPE_I)

                # Replace ALL keyframes in Video B with delta payload so decoder never resets image
                if is_iframe:
                    if last_pframe_payload_b is not None:
                        new_chunk = bytearray(chunk_bytes[:8]) + last_pframe_payload_b
                        if len(new_chunk) % 2 != 0:
                            new_chunk.append(0)
                        struct.pack_into('<I', new_chunk, 4, len(last_pframe_payload_b))
                        chunk_bytes = new_chunk
                    else:
                        continue
                else:
                    last_pframe_payload_b = payload

                # 1x realtime playback - smooth transition without artificial freezing
                modified_data.extend(chunk_bytes)
                video_b_count += 1

        total_video_frames = len([f for f in frames_a if f[0] == b'00dc']) + video_b_count
        update_avi_headers(modified_data, movi_pos_a, total_video_frames)

        with open(temp_out_avi, 'wb') as f:
            f.write(modified_data)

        keep_audio = options.get('keep_audio', True)
        if keep_audio:
            recombine_with_original_audio(ffmpeg, temp_out_avi, input_a, output_path, progress_callback, shortest=False)
        else:
            cmd_remux = [ffmpeg, "-y", "-i", temp_out_avi, "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", output_path]
            subprocess.run(cmd_remux, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if progress_callback:
            progress_callback(100, "Done! Stitch Mosh completed successfully.")
        return True

    finally:
        cleanup_temp_files(temp_avi_a, temp_avi_b, temp_out_avi)
