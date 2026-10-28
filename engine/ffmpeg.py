import os
import subprocess


def has_audio_stream(ffmpeg_path, file_path):
    """Checks whether a media file contains a playable audio stream."""
    if not file_path or not os.path.exists(file_path):
        return False
    cmd = [
        ffmpeg_path, "-i", file_path,
        "-vn", "-t", "0.1", "-f", "null", "-"
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode == 0


def convert_to_avi_mpeg4(ffmpeg_path, input_path, temp_avi, progress_callback=None, target_res=None, gop_size=60):
    """
    Converts input video to raw MPEG-4 AVI container with Xvid fourcc,
    fixed keyframe interval and no B-frames (essential for datamoshing).
    """
    if progress_callback:
        progress_callback(10, "Converting to raw MPEG-4 AVI container...")

    cmd = [
        ffmpeg_path, "-y",
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
        "-g", str(gop_size),
        "-bf", "0",
        "-c:a", "mp3",
        temp_avi
    ])

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg error during AVI conversion: {proc.stderr.decode('utf-8', errors='ignore')}")


def recombine_with_original_audio(ffmpeg_path, moshed_avi, original_input, final_output, progress_callback=None, shortest=True):
    """
    Muxes the modified video stream with original audio track from input file.
    Falls back to video-only if audio muxing encounters an error.
    """
    if progress_callback:
        progress_callback(90, "Finalizing and merging audio track...")

    cmd = [
        ffmpeg_path, "-y",
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
            ffmpeg_path, "-y",
            "-i", moshed_avi,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            final_output
        ]
        subprocess.run(cmd_fallback, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
