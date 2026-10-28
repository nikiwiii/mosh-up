import os
import wave
import struct
import random
import subprocess
from collections import deque
import cv2
import numpy as np

from ..ffmpeg import convert_to_avi_mpeg4, recombine_with_original_audio
from ..avi import find_video_frames, find_vop, is_iframe, is_pframe
from ..utils import cleanup_temp_files


def extract_and_analyze_audio(ffmpeg, audio_source_path, total_video_frames, fps, audio_band='bass', sensitivity=65.0):
    """
    Extracts audio to temporary mono WAV using FFmpeg and analyzes per-frame energy & beat onsets.
    Uses zero-padded spectral analysis and half-wave rectified spectral flux for reliable
    transient and rhythm detection across any audio genre.
    Returns:
        is_beat (np.ndarray of bool): True where a musical beat/transient was detected.
        beat_intensity (np.ndarray of float): Continuous normalized intensity envelope [0.0, 2.0].
    """
    temp_dir = os.path.dirname(audio_source_path) or "."
    temp_wav = os.path.join(temp_dir, f"_temp_analysis_{random.randint(1000, 9999)}.wav")

    try:
        cmd_extract = [
            ffmpeg, "-y",
            "-i", audio_source_path,
            "-vn",
            "-ac", "1",
            "-ar", "44100",
            temp_wav
        ]
        proc = subprocess.run(cmd_extract, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0 or not os.path.exists(temp_wav) or os.path.getsize(temp_wav) < 100:
            raise RuntimeError(
                "No valid audio track found in the input file! "
                "Please select an external audio file (MP3, WAV, AAC) or use a video with sound."
            )

        with wave.open(temp_wav, 'rb') as wf:
            n_frames = wf.getnframes()
            sr = wf.getframerate()
            raw_bytes = wf.readframes(n_frames)

        if not raw_bytes or n_frames == 0:
            raise RuntimeError("Audio stream is empty.")

        samples = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0

        n_video_frames = max(1, total_video_frames)
        samples_per_frame = sr / max(1.0, float(fps))
        energy = np.zeros(n_video_frames, dtype=np.float32)

        fft_size = 2048

        for i in range(n_video_frames):
            s = int(i * samples_per_frame)
            e = min(len(samples), int((i + 1) * samples_per_frame))
            if s >= len(samples):
                energy[i] = 0.0
                continue
            chunk = samples[s:e]
            if len(chunk) == 0:
                continue

            if audio_band == 'bass':
                w_chunk = chunk * np.hanning(len(chunk))
                fft_data = np.abs(np.fft.rfft(w_chunk, n=fft_size))
                freqs = np.fft.rfftfreq(fft_size, 1.0 / sr)
                mask = (freqs >= 20) & (freqs <= 220)
                energy[i] = np.sqrt(np.mean(fft_data[mask] ** 2)) if np.any(mask) else 0.0
            elif audio_band == 'high':
                w_chunk = chunk * np.hanning(len(chunk))
                fft_data = np.abs(np.fft.rfft(w_chunk, n=fft_size))
                freqs = np.fft.rfftfreq(fft_size, 1.0 / sr)
                mask = (freqs >= 2500) & (freqs <= 12000)
                energy[i] = np.sqrt(np.mean(fft_data[mask] ** 2)) if np.any(mask) else 0.0
            else:  # 'rms' full spectrum volume
                energy[i] = np.sqrt(np.mean(chunk ** 2))

        # Normalize energy envelope
        p95 = max(1e-5, np.percentile(energy, 95))
        norm_energy = np.clip(energy / p95, 0.0, 2.0)

        # Spectral flux: half-wave rectified onset transient detector
        flux = np.zeros_like(norm_energy)
        flux[1:] = np.maximum(0.0, norm_energy[1:] - norm_energy[:-1])

        # Adaptive threshold based on user sensitivity
        flux_std = np.std(flux) if np.std(flux) > 1e-5 else 0.1
        sens_norm = np.clip(float(sensitivity) / 100.0, 0.1, 1.0)
        thresh = max(0.04, (1.25 - 0.90 * sens_norm) * flux_std + (0.50 - 0.45 * sens_norm) * 0.1)

        is_beat = (flux > thresh) | (norm_energy > (1.35 - 0.55 * sens_norm))

        # Create smooth musical envelope (fast attack, smooth release)
        beat_intensity = np.zeros_like(norm_energy)
        curr_env = 0.0
        alpha = 0.75  # attack
        decay = 0.82  # release
        for i in range(len(norm_energy)):
            target = norm_energy[i] + (0.45 if is_beat[i] else 0.0)
            if target > curr_env:
                curr_env = alpha * target + (1.0 - alpha) * curr_env
            else:
                curr_env = decay * curr_env
            beat_intensity[i] = np.clip(curr_env, 0.0, 2.0)

        return is_beat, beat_intensity

    finally:
        cleanup_temp_files(temp_wav)


def mosh_audio_reactive(ffmpeg, input_path, output_path, options, progress_callback=None):
    """
    Audio-Reactive Datamoshing Effect.
    Analyzes the audio stream (or external audio track) for beats/frequency energy and
    dynamically triggers vector smearing, keyframe drops, bit corruption glitches, or chromatic pulses.
    """
    options = options or {}
    custom_audio = options.get('custom_audio_path', '').strip()
    audio_source = custom_audio if (custom_audio and os.path.exists(custom_audio)) else input_path

    reaction_mode = options.get('audio_reaction', 'smear')  # 'smear', 'melt', 'glitch', 'rgb', 'hybrid'
    audio_band = options.get('audio_band', 'bass')          # 'bass', 'rms', 'high'
    sensitivity = float(options.get('audio_sensitivity', 65.0))
    intensity_param = float(options.get('audio_intensity', 12.0))

    if progress_callback:
        progress_callback(8, "Analyzing audio track frequency spectrum and rhythm beats...")

    # Determine video properties
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video file: {input_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100
    cap.release()

    # Audio analysis per video frame
    is_beat, beat_intensity = extract_and_analyze_audio(
        ffmpeg, audio_source, total_frames, fps,
        audio_band=audio_band, sensitivity=sensitivity
    )

    beat_count = int(np.sum(is_beat))
    if progress_callback:
        progress_callback(20, f"Detected {beat_count} rhythm pulses in audio track. Applying '{reaction_mode}'...")

    temp_dir = os.path.dirname(output_path) or "."

    # --- Mode 1: Chromatic Beat Pulse ('rgb') via OpenCV ---
    if reaction_mode == 'rgb':
        temp_video = os.path.join(temp_dir, "_temp_audio_rgb.mp4")
        cap = cv2.VideoCapture(input_path)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

        max_delay = max(2, int(intensity_param / 2.5))
        max_shift = max(6, int(intensity_param * 1.8))

        buf_len = max(3, max_delay * 2 + 1)
        frame_buffer = deque(maxlen=buf_len)
        frame_idx = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    break

                curr_beat = bool(is_beat[frame_idx]) if frame_idx < len(is_beat) else False
                curr_int = float(beat_intensity[frame_idx]) if frame_idx < len(beat_intensity) else 0.0

                frame_buffer.append(frame)

                # Temporal channel lag modulated by audio
                dyn_delay = int(max_delay * (0.35 + 0.65 * curr_int)) if (curr_beat or curr_int > 0.4) else 0
                if dyn_delay > 0 and len(frame_buffer) > 1:
                    r_frame = frame_buffer[-1]
                    g_idx = max(0, len(frame_buffer) - 1 - dyn_delay // 2)
                    b_idx = max(0, len(frame_buffer) - 1 - dyn_delay)
                    b_frame = frame_buffer[b_idx]
                    g_frame = frame_buffer[g_idx]
                else:
                    r_frame = g_frame = b_frame = frame

                b_chan = b_frame[..., 0].copy()
                g_chan = g_frame[..., 1].copy()
                r_chan = r_frame[..., 2].copy()

                # Spatial chromatic aberration displacement
                dyn_shift = int(max_shift * (0.25 + 0.75 * curr_int))
                if curr_beat:
                    dyn_shift = int(dyn_shift * 1.6)

                if dyn_shift > 0:
                    M_r = np.float32([[1, 0, -dyn_shift], [0, 1, 0]])
                    M_b = np.float32([[1, 0, dyn_shift], [0, 1, 0]])
                    r_chan = cv2.warpAffine(r_chan, M_r, (width, height), borderMode=cv2.BORDER_REFLECT)
                    b_chan = cv2.warpAffine(b_chan, M_b, (width, height), borderMode=cv2.BORDER_REFLECT)

                # Beat shockwave scanline slices
                if curr_beat:
                    num_slices = random.randint(2, 4)
                    for _ in range(num_slices):
                        slice_h = random.randint(15, 60)
                        y1 = random.randint(0, max(1, height - slice_h))
                        y2 = min(height, y1 + slice_h)
                        shift_amt = int(random.choice([-1, 1]) * (dyn_shift + random.randint(8, 16)))
                        r_chan[y1:y2, :] = np.roll(r_chan[y1:y2, :], shift_amt, axis=1)
                        b_chan[y1:y2, :] = np.roll(b_chan[y1:y2, :], -shift_amt, axis=1)

                merged = cv2.merge([b_chan, g_chan, r_chan])
                out.write(merged)

                frame_idx += 1
                if progress_callback and frame_idx % 20 == 0:
                    pct = 25 + int(60 * (frame_idx / max(1, total_frames)))
                    progress_callback(pct, f"Audio pulsing frame {frame_idx}/{total_frames}...")

            cap.release()
            out.release()

            recombine_with_original_audio(ffmpeg, temp_video, audio_source, output_path, progress_callback, shortest=True)
            if progress_callback:
                progress_callback(100, "Done! Audio-Reactive RGB Pulse completed.")
            return True

        finally:
            cap.release()
            out.release()
            cleanup_temp_files(temp_video)

    # --- Modes 2, 3, 4, 5: MPEG-4 AVI Stream Manipulation ---
    temp_in_avi = os.path.join(temp_dir, "_temp_audio_in.avi")
    temp_out_avi = os.path.join(temp_dir, "_temp_audio_out.avi")

    try:
        # Use lower GOP size (15) for melt & hybrid modes so keyframes occur frequently enough to be melted to the beat
        avi_gop = 15 if reaction_mode in ('melt', 'hybrid') else 60
        convert_to_avi_mpeg4(ffmpeg, input_path, temp_in_avi, progress_callback, gop_size=avi_gop)

        with open(temp_in_avi, 'rb') as f:
            data = bytearray(f.read())

        frames = find_video_frames(data)
        if not frames:
            raise RuntimeError("No video frames found in converted AVI file!")

        modified_data = bytearray()
        first_frame_pos = frames[0][0]
        modified_data.extend(data[:first_frame_pos])

        total_avi_frames = len(frames)
        last_pframe_payload = None

        for idx, (f_pos, f_size) in enumerate(frames):
            if progress_callback and idx % 35 == 0:
                pct = 35 + int(50 * (idx / total_avi_frames))
                progress_callback(pct, f"Rhythm moshing frames ({idx}/{total_avi_frames})...")

            chunk_data = data[f_pos:f_pos + 8 + f_size]
            payload = bytearray(data[f_pos + 8:f_pos + 8 + f_size])

            norm_idx = min(idx, total_frames - 1)
            curr_beat = bool(is_beat[norm_idx]) if norm_idx < len(is_beat) else False
            curr_intensity = float(beat_intensity[norm_idx]) if norm_idx < len(beat_intensity) else 0.0

            frame_is_i = is_iframe(payload)
            frame_is_p = is_pframe(payload)

            if frame_is_p:
                last_pframe_payload = payload

            # Action 1: Beat Drop Melt ('melt')
            if reaction_mode == 'melt':
                near_beat = any(is_beat[max(0, norm_idx - 1):min(len(is_beat), norm_idx + 2)])
                # Drop I-frame if on or near a beat, or if audio energy is elevated
                if frame_is_i and idx > 0 and (near_beat or curr_intensity > 0.45) and last_pframe_payload:
                    new_chunk = bytearray(chunk_data[:8]) + last_pframe_payload
                    struct.pack_into('<I', new_chunk, 4, len(last_pframe_payload))
                    modified_data.extend(new_chunk)
                else:
                    modified_data.extend(chunk_data)
                    # If on a beat during P-frame: duplicate motion vector to stretch the melting liquid
                    if frame_is_p and curr_beat:
                        p_melt_dup = max(2, int(intensity_param * 0.45 * curr_intensity))
                        for _ in range(p_melt_dup):
                            modified_data.extend(chunk_data)

            # Action 2: Beat Motion Smear ('smear')
            elif reaction_mode == 'smear':
                modified_data.extend(chunk_data)
                if frame_is_p:
                    if curr_beat:
                        # Massive vector smear burst on beat kicks!
                        repeat_count = max(3, int(intensity_param * (0.6 + 0.9 * curr_intensity)))
                        for _ in range(repeat_count):
                            modified_data.extend(chunk_data)
                    elif curr_intensity > 0.75:
                        # Subtle motion glide on loud sustained passages
                        repeat_count = max(1, int(intensity_param * 0.3 * curr_intensity))
                        for _ in range(repeat_count):
                            modified_data.extend(chunk_data)

            # Action 3: Cyber Glitch Rhythm ('glitch')
            elif reaction_mode == 'glitch':
                if frame_is_p:
                    vop_idx, _ = find_vop(payload)
                    safe_start = max(16, vop_idx + 8 if vop_idx != -1 else 16)

                    if curr_beat:
                        # Heavy glitch burst
                        corrupt_bytes = int(len(payload) * 0.012 * (intensity_param / 10.0) * max(0.6, curr_intensity))
                        corrupt_bytes = min(len(payload) - safe_start, max(4, corrupt_bytes))
                    elif curr_intensity > 0.60:
                        # Subtle digital noise
                        corrupt_bytes = int(len(payload) * 0.003 * (intensity_param / 10.0) * (curr_intensity - 0.4))
                        corrupt_bytes = min(len(payload) - safe_start, max(1, corrupt_bytes))
                    else:
                        corrupt_bytes = 0

                    if corrupt_bytes > 0:
                        mod_payload = bytearray(payload)
                        for _ in range(corrupt_bytes):
                            byte_pos = random.randint(safe_start, len(mod_payload) - 1)
                            mod_payload[byte_pos] = (mod_payload[byte_pos] ^ random.randint(1, 255)) & 0xFF
                        modified_data.extend(chunk_data[:8] + mod_payload)
                    else:
                        modified_data.extend(chunk_data)
                else:
                    modified_data.extend(chunk_data)

            # Action 4: Full Audio Chaos ('hybrid')
            elif reaction_mode == 'hybrid':
                near_beat = any(is_beat[max(0, norm_idx - 1):min(len(is_beat), norm_idx + 2)])
                if frame_is_i and idx > 0 and (near_beat or curr_intensity > 0.45) and last_pframe_payload:
                    # Melt keyframe across drop
                    new_chunk = bytearray(chunk_data[:8]) + last_pframe_payload
                    struct.pack_into('<I', new_chunk, 4, len(last_pframe_payload))
                    modified_data.extend(new_chunk)
                elif frame_is_p and curr_beat:
                    # Both corrupt and duplicate on beats
                    vop_idx, _ = find_vop(payload)
                    safe_start = max(16, vop_idx + 8 if vop_idx != -1 else 16)
                    mod_payload = bytearray(payload)
                    corrupt_bytes = int(len(mod_payload) * 0.008 * (intensity_param / 10.0) * max(0.5, curr_intensity))
                    corrupt_bytes = min(len(mod_payload) - safe_start, max(2, corrupt_bytes))
                    for _ in range(corrupt_bytes):
                        byte_pos = random.randint(safe_start, len(mod_payload) - 1)
                        mod_payload[byte_pos] = (mod_payload[byte_pos] ^ random.randint(1, 255)) & 0xFF

                    corrupted_chunk = chunk_data[:8] + mod_payload
                    modified_data.extend(corrupted_chunk)

                    repeat_count = max(2, int(intensity_param * 0.5 * curr_intensity))
                    for _ in range(repeat_count):
                        modified_data.extend(corrupted_chunk)
                else:
                    modified_data.extend(chunk_data)

            else:
                modified_data.extend(chunk_data)

        last_frame_end = frames[-1][0] + 8 + frames[-1][1]
        if last_frame_end < len(data):
            modified_data.extend(data[last_frame_end:])

        with open(temp_out_avi, 'wb') as f:
            f.write(modified_data)

        # In modes that duplicate frames ('smear', 'melt', 'hybrid'), use shortest=False so smeared video frames are retained
        use_shortest = reaction_mode not in ('smear', 'melt', 'hybrid')
        recombine_with_original_audio(ffmpeg, temp_out_avi, audio_source, output_path, progress_callback, shortest=use_shortest)

        if progress_callback:
            progress_callback(100, f"Done! Audio-Reactive Moshing ({reaction_mode}) completed.")
        return True

    finally:
        cleanup_temp_files(temp_in_avi, temp_out_avi)
