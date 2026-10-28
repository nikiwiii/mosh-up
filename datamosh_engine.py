"""
Datamosh Engine Module (Backward Compatibility Facade).
This module re-exports components from the modular `engine` package.
"""

from engine import (
    DatamoshEngine,
    get_ffmpeg_exe,
    parse_timestamp,
    format_seconds_to_timestamp,
    cleanup_temp_files,
    convert_to_avi_mpeg4,
    recombine_with_original_audio,
    has_audio_stream,
    find_video_frames,
    find_vop,
    is_iframe,
    is_pframe,
    parse_avi_chunks,
    update_avi_headers,
    VOP_TYPE_I,
    VOP_TYPE_P,
    VOP_TYPE_B,
    VOP_TYPE_S,
    mosh_rgb_split,
    mosh_audio_reactive,
)

__all__ = [
    'DatamoshEngine',
    'get_ffmpeg_exe',
    'parse_timestamp',
    'format_seconds_to_timestamp',
    'cleanup_temp_files',
    'convert_to_avi_mpeg4',
    'recombine_with_original_audio',
    'has_audio_stream',
    'find_video_frames',
    'find_vop',
    'is_iframe',
    'is_pframe',
    'parse_avi_chunks',
    'update_avi_headers',
    'VOP_TYPE_I',
    'VOP_TYPE_P',
    'VOP_TYPE_B',
    'VOP_TYPE_S',
    'mosh_rgb_split',
    'mosh_audio_reactive',
]
