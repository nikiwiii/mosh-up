import os
import imageio_ffmpeg


def get_ffmpeg_exe():
    """Returns path to ffmpeg executable or fallback to system 'ffmpeg'."""
    try:
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def parse_timestamp(ts_str):
    """
    Parses timestamp string (seconds, MM:SS, or HH:MM:SS) to float seconds.
    Returns None if format is invalid.
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


def cleanup_temp_files(*file_paths):
    """Safely removes temporary files if they exist."""
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass
