"""
Datamosh Engine - Core Video Glitch & Datamoshing Processing
Supports MPEG-4 AVI keyframe manipulation, P-frame duplication, bit corruption,
and Optical Flow vector drift.
"""

import os
import sys
import struct
import random
import subprocess
import shutil
import cv2
import numpy as np
import imageio_ffmpeg


def get_ffmpeg_exe():
    """Returns absolute path to executable FFmpeg binary."""
    try:
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def parse_timestamp(ts_str):
    """
    Parses timestamp string format like MM:SS, MM:SS.s, HH:MM:SS, or seconds float.
    Returns seconds as float or None if invalid.
    """
    if not ts_str or not isinstance(ts_str, str):
        return None

    ts_str = ts_str.strip()
    try:
        if ':' not in ts_str:
            sec = float(ts_str)
            return sec if sec >= 0 else None

        parts = ts_str.split(':')
        if len(parts) == 2:  # MM:SS or MM:SS.s
            m = float(parts[0])
            s = float(parts[1])
            if m < 0 or s < 0 or s >= 60:
                return None
            return m * 60.0 + s
        elif len(parts) == 3:  # HH:MM:SS
            h = float(parts[0])
            m = float(parts[1])
            s = float(parts[2])
            if h < 0 or m < 0 or m >= 60 or s < 0 or s >= 60:
                return None
            return h * 3600.0 + m * 60.0 + s
    except ValueError:
        return None
    return None


def format_seconds_to_timestamp(seconds):
    """Formats seconds float into MM:SS.s string."""
    if seconds is None or seconds < 0:
        return "00:00"
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m:02d}:{s:04.1f}"


class DatamoshEngine:
    def __init__(self, ffmpeg_path=None):
        self.ffmpeg = ffmpeg_path or get_ffmpeg_exe()

    def process(self, mode, input_path, output_path, options=None, progress_callback=None):
        """
        Main entry point for video datamoshing.
        modes: 'volcano_melt', 'motion_smear', 'stitch_mosh', 'cyber_glitch', 'flow_drift'
        """
        options = options or {}
        if progress_callback:
            progress_callback(5, "Preparing video file...")

        if mode == 'volcano_melt':
            return self.mosh_volcano_melt(input_path, output_path, options, progress_callback)
        elif mode == 'motion_smear':
            return self.mosh_motion_smear(input_path, output_path, options, progress_callback)
        elif mode == 'stitch_mosh':
            input_b = options.get('input_b')
            if not input_b or not os.path.exists(input_b):
                raise ValueError("Missing second video file B for Stitch Mosh!")
            return self.mosh_stitch(input_path, input_b, output_path, options, progress_callback)
        elif mode == 'cyber_glitch':
            return self.mosh_cyber_glitch(input_path, output_path, options, progress_callback)
        elif mode == 'flow_drift':
            return self.mosh_flow_drift(input_path, output_path, options, progress_callback)
        else:
            raise ValueError(f"Unknown datamosh mode: {mode}")

    def _convert_to_avi_mpeg4(self, input_path, temp_avi, progress_callback=None, target_res=None):
        """Converts input video to MPEG4 AVI with iframe interval suitable for datamoshing."""
        if progress_callback:
            progress_callback(10, "Converting to raw MPEG-4 AVI container...")
        
        cmd = [
            self.ffmpeg, "-y",
            "-i", input_path,
        ]
        
        if target_res:
            w, h, fps = target_res
            cmd.extend([
                "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2",
                "-r", str(fps)
            ])

        cmd.extend([
            "-c:v", "mpeg4",
            "-vtag", "xvid",
            "-q:v", "3",
            "-g", "60",
            "-bf", "0",
            "-c:a", "mp3",
            temp_avi
        ])
        
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg error during AVI conversion: {proc.stderr.decode('utf-8', errors='ignore')}")

    def _recombine_with_original_audio(self, moshed_avi, original_input, final_output, progress_callback=None, shortest=True):
        """Recombines moshed video with audio from original input video."""
        if progress_callback:
            progress_callback(90, "Finalizing and merging audio track...")

        cmd = [
            self.ffmpeg, "-y",
            "-i", moshed_avi,
            "-i", original_input,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-map", "0:v:0",
            "-map", "1:a:0?",
            "-c:a", "aac",
            "-b:a", "192k",
        ]
        if shortest:
            cmd.append("-shortest")

        cmd.append(final_output)
        
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0 or not os.path.exists(final_output):
            cmd_fallback = [
                self.ffmpeg, "-y",
                "-i", moshed_avi,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                final_output
            ]
            subprocess.run(cmd_fallback, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def mosh_volcano_melt(self, input_path, output_path, options, progress_callback=None):
        """
        I-Frame Removal Datamosh.
        Removes I-frames (keyframes) between start_time and end_time (in seconds) or percentage.
        """
        temp_dir = os.path.dirname(output_path) or "."
        temp_in_avi = os.path.join(temp_dir, "_temp_in.avi")
        temp_out_avi = os.path.join(temp_dir, "_temp_out.avi")

        try:
            self._convert_to_avi_mpeg4(input_path, temp_in_avi, progress_callback)
            
            if progress_callback:
                progress_callback(30, "Analyzing AVI keyframes...")

            with open(temp_in_avi, 'rb') as f:
                data = bytearray(f.read())

            frames = []
            pos = 0
            while True:
                pos = data.find(b'00dc', pos)
                if pos == -1:
                    break
                if pos + 8 <= len(data):
                    chunk_size = struct.unpack('<I', data[pos+4:pos+8])[0]
                    frames.append((pos, chunk_size))
                    pos += 8 + chunk_size
                else:
                    pos += 4

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

                is_iframe = False
                vop_idx = payload.find(b'\x00\x00\x01\xb6')
                if vop_idx != -1 and vop_idx + 4 < len(payload):
                    vop_type = (payload[vop_idx + 4] & 0xC0) >> 6
                    if vop_type == 0:
                        is_iframe = True

                if is_iframe and idx > 0 and (start_frame <= idx <= end_frame):
                    if last_pframe_payload is not None:
                        new_chunk = bytearray(chunk_data[:8]) + last_pframe_payload
                        struct.pack_into('<I', new_chunk, 4, len(last_pframe_payload))
                        modified_data.extend(new_chunk)
                    else:
                        continue
                else:
                    modified_data.extend(chunk_data)
                    if not is_iframe:
                        last_pframe_payload = payload

            last_frame_end = frames[-1][0] + 8 + frames[-1][1]
            if last_frame_end < len(data):
                modified_data.extend(data[last_frame_end:])

            with open(temp_out_avi, 'wb') as f:
                f.write(modified_data)

            keep_audio = options.get('keep_audio', True)
            if keep_audio:
                self._recombine_with_original_audio(temp_out_avi, input_path, output_path, progress_callback, shortest=True)
            else:
                cmd_remux = [self.ffmpeg, "-y", "-i", temp_out_avi, "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path]
                subprocess.run(cmd_remux, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if progress_callback:
                progress_callback(100, "Done! Datamoshing completed successfully.")
            return True

        finally:
            for t_file in (temp_in_avi, temp_out_avi):
                if os.path.exists(t_file):
                    try:
                        os.remove(t_file)
                    except Exception:
                        pass

    def mosh_motion_smear(self, input_path, output_path, options, progress_callback=None):
        """
        P-Frame Duplication Datamosh.
        Duplicates P-frames to smear motion vectors endlessly.
        """
        temp_dir = os.path.dirname(output_path) or "."
        temp_in_avi = os.path.join(temp_dir, "_temp_in.avi")
        temp_out_avi = os.path.join(temp_dir, "_temp_out.avi")

        try:
            self._convert_to_avi_mpeg4(input_path, temp_in_avi, progress_callback)
            
            dup_count = int(options.get('repeat_count', 12))
            frequency = int(options.get('frequency', 5))

            with open(temp_in_avi, 'rb') as f:
                data = bytearray(f.read())

            frames = []
            pos = 0
            while True:
                pos = data.find(b'00dc', pos)
                if pos == -1:
                    break
                if pos + 8 <= len(data):
                    chunk_size = struct.unpack('<I', data[pos+4:pos+8])[0]
                    frames.append((pos, chunk_size))
                    pos += 8 + chunk_size
                else:
                    pos += 4

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

                is_pframe = False
                vop_idx = payload.find(b'\x00\x00\x01\xb6')
                if vop_idx != -1 and vop_idx + 4 < len(payload):
                    vop_type = (payload[vop_idx + 4] & 0xC0) >> 6
                    if vop_type == 1:
                        is_pframe = True

                modified_data.extend(chunk_data)

                if is_pframe:
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
                self._recombine_with_original_audio(temp_out_avi, input_path, output_path, progress_callback, shortest=False)
            else:
                cmd_remux = [self.ffmpeg, "-y", "-i", temp_out_avi, "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path]
                subprocess.run(cmd_remux, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if progress_callback:
                progress_callback(100, "Done! Motion Smear effect completed.")
            return True

        finally:
            for t_file in (temp_in_avi, temp_out_avi):
                if os.path.exists(t_file):
                    try:
                        os.remove(t_file)
                    except Exception:
                        pass

    def mosh_stitch(self, input_a, input_b, output_path, options, progress_callback=None):
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
            self._convert_to_avi_mpeg4(input_a, temp_avi_a)

            if progress_callback:
                progress_callback(35, f"Preparing second video file B (matching {width_a}x{height_a} @ {fps_a:.1f}fps)...")
            self._convert_to_avi_mpeg4(input_b, temp_avi_b, target_res=target_res)

            with open(temp_avi_a, 'rb') as f:
                data_a = bytearray(f.read())
            with open(temp_avi_b, 'rb') as f:
                data_b = bytearray(f.read())

            def parse_avi_chunks(data):
                frames = []
                movi_pos = data.find(b'LIST')
                while movi_pos != -1:
                    if movi_pos + 12 <= len(data) and data[movi_pos+8:movi_pos+12] == b'movi':
                        break
                    movi_pos = data.find(b'LIST', movi_pos + 4)

                pos = movi_pos + 12 if movi_pos != -1 else 0
                idx1_pos = data.find(b'idx1')

                limit = idx1_pos if idx1_pos != -1 else len(data)

                while pos < limit:
                    chunk_id = data[pos:pos+4]
                    if chunk_id in (b'00dc', b'01wb', b'00db'):
                        if pos + 8 <= len(data):
                            c_size = struct.unpack('<I', data[pos+4:pos+8])[0]
                            frames.append((chunk_id, pos, c_size))
                            pos += 8 + c_size + (c_size % 2)
                        else:
                            break
                    else:
                        pos += 1
                return movi_pos, idx1_pos, frames

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
                    vop_idx = payload.find(b'\x00\x00\x01\xb6')
                    if vop_idx != -1 and vop_idx + 4 < len(payload):
                        vop_type = (payload[vop_idx + 4] & 0xC0) >> 6
                        if vop_type == 1:
                            last_pframe_payload_a = payload
                            break

            video_b_count = 0
            last_pframe_payload_b = last_pframe_payload_a

            for idx, (c_id, f_pos, f_size) in enumerate(frames_b):
                chunk_bytes = bytearray(data_b[f_pos:f_pos + 8 + f_size + (f_size % 2)])
                payload = data_b[f_pos + 8:f_pos + 8 + f_size]

                if c_id == b'00dc':
                    vop_idx = payload.find(b'\x00\x00\x01\xb6')
                    is_iframe = False
                    if vop_idx != -1 and vop_idx + 4 < len(payload):
                        vop_type = (payload[vop_idx + 4] & 0xC0) >> 6
                        if vop_type == 0:  # I-frame
                            is_iframe = True

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

            # Update avih dwTotalFrames
            avih_pos = modified_data.find(b'avih')
            if avih_pos != -1 and avih_pos + 24 <= len(modified_data):
                total_video_frames = len([f for f in frames_a if f[0] == b'00dc']) + video_b_count
                struct.pack_into('<I', modified_data, avih_pos + 20, total_video_frames)

            # Update LIST movi size
            if movi_pos_a != -1 and movi_pos_a + 8 <= len(modified_data):
                new_movi_size = len(modified_data) - (movi_pos_a + 8)
                struct.pack_into('<I', modified_data, movi_pos_a + 4, new_movi_size)

            # Update RIFF header size
            if len(modified_data) >= 8:
                struct.pack_into('<I', modified_data, 4, len(modified_data) - 8)

            with open(temp_out_avi, 'wb') as f:
                f.write(modified_data)

            keep_audio = options.get('keep_audio', True)
            if keep_audio:
                self._recombine_with_original_audio(temp_out_avi, input_a, output_path, progress_callback, shortest=False)
            else:
                cmd_remux = [self.ffmpeg, "-y", "-i", temp_out_avi, "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", output_path]
                subprocess.run(cmd_remux, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if progress_callback:
                progress_callback(100, "Done! Stitch Mosh completed successfully.")
            return True

        finally:
            for t_file in (temp_avi_a, temp_avi_b, temp_out_avi):
                if os.path.exists(t_file):
                    try:
                        os.remove(t_file)
                    except Exception:
                        pass

    def mosh_cyber_glitch(self, input_path, output_path, options, progress_callback=None):
        """
        Bitwise Payload Corruptor.
        Swaps and flips macroblock bytes in P-frame payloads.
        """
        temp_dir = os.path.dirname(output_path) or "."
        temp_in_avi = os.path.join(temp_dir, "_temp_in.avi")
        temp_out_avi = os.path.join(temp_dir, "_temp_out.avi")

        try:
            self._convert_to_avi_mpeg4(input_path, temp_in_avi, progress_callback)

            corrupt_rate = options.get('corrupt_rate', 0.05)
            intensity = options.get('intensity', 0.02)
            seed = int(options.get('seed', 42))
            random.seed(seed)

            with open(temp_in_avi, 'rb') as f:
                data = bytearray(f.read())

            pos = 0
            frames = []
            while True:
                pos = data.find(b'00dc', pos)
                if pos == -1:
                    break
                if pos + 8 <= len(data):
                    c_size = struct.unpack('<I', data[pos+4:pos+8])[0]
                    frames.append((pos, c_size))
                    pos += 8 + c_size
                else:
                    pos += 4

            modified_data = bytearray()
            modified_data.extend(data[:frames[0][0]])
            total_frames = len(frames)

            for idx, (f_pos, f_size) in enumerate(frames):
                if progress_callback and idx % 40 == 0:
                    pct = 30 + int(55 * (idx / total_frames))
                    progress_callback(pct, f"Injecting Cyber Glitch bitwise errors ({idx}/{total_frames})...")

                chunk_header = data[f_pos:f_pos + 8]
                payload = bytearray(data[f_pos + 8:f_pos + 8 + f_size])

                is_iframe = False
                vop_idx = payload.find(b'\x00\x00\x01\xb6')
                if vop_idx != -1 and vop_idx + 4 < len(payload):
                    vop_type = (payload[vop_idx + 4] & 0xC0) >> 6
                    if vop_type == 0:
                        is_iframe = True

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
                self._recombine_with_original_audio(temp_out_avi, input_path, output_path, progress_callback, shortest=True)
            else:
                cmd_remux = [self.ffmpeg, "-y", "-i", temp_out_avi, "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path]
                subprocess.run(cmd_remux, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if progress_callback:
                progress_callback(100, "Done! Cyber Glitch effect generated.")
            return True

        finally:
            for t_file in (temp_in_avi, temp_out_avi):
                if os.path.exists(t_file):
                    try:
                        os.remove(t_file)
                    except Exception:
                        pass

    def mosh_flow_drift(self, input_path, output_path, options, progress_callback=None):
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
                self._recombine_with_original_audio(temp_video, input_path, output_path, progress_callback, shortest=True)
            else:
                cmd_remux = [self.ffmpeg, "-y", "-i", temp_video, "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path]
                subprocess.run(cmd_remux, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if progress_callback:
                progress_callback(100, "Done! Optical Flow Drift effect completed.")
            return True

        finally:
            cap.release()
            out.release()
            if os.path.exists(temp_video):
                try:
                    os.remove(temp_video)
                except Exception:
                    pass
