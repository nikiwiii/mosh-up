import os

from .utils import get_ffmpeg_exe
from .ffmpeg import convert_to_avi_mpeg4, recombine_with_original_audio
from .effects import (
    mosh_volcano_melt,
    mosh_motion_smear,
    mosh_stitch,
    mosh_cyber_glitch,
    mosh_flow_drift,
    mosh_rgb_split,
    mosh_audio_reactive,
)


class DatamoshEngine:
    """
    Main Datamosh Processing Engine.
    Coordinates video preparation, effect dispatching, and audio/video recombining.
    """
    def __init__(self, ffmpeg_path=None):
        self.ffmpeg = ffmpeg_path or get_ffmpeg_exe()

    def process(self, mode, input_path, output_path, options=None, progress_callback=None):
        """
        Processes video using specified datamosh mode.
        Supported modes: 'volcano_melt', 'motion_smear', 'stitch_mosh', 'cyber_glitch', 'flow_drift', 'rgb_split', 'audio_reactive'
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
        elif mode == 'rgb_split':
            return self.mosh_rgb_split(input_path, output_path, options, progress_callback)
        elif mode == 'audio_reactive':
            return self.mosh_audio_reactive(input_path, output_path, options, progress_callback)
        else:
            raise ValueError(f"Unknown datamosh mode: {mode}")

    def _convert_to_avi_mpeg4(self, input_path, temp_avi, progress_callback=None, target_res=None):
        return convert_to_avi_mpeg4(self.ffmpeg, input_path, temp_avi, progress_callback, target_res)

    def _recombine_with_original_audio(self, moshed_avi, original_input, final_output, progress_callback=None, shortest=True):
        return recombine_with_original_audio(self.ffmpeg, moshed_avi, original_input, final_output, progress_callback, shortest)

    def mosh_volcano_melt(self, input_path, output_path, options, progress_callback=None):
        return mosh_volcano_melt(self.ffmpeg, input_path, output_path, options, progress_callback)

    def mosh_motion_smear(self, input_path, output_path, options, progress_callback=None):
        return mosh_motion_smear(self.ffmpeg, input_path, output_path, options, progress_callback)

    def mosh_stitch(self, input_a, input_b, output_path, options, progress_callback=None):
        return mosh_stitch(self.ffmpeg, input_a, input_b, output_path, options, progress_callback)

    def mosh_cyber_glitch(self, input_path, output_path, options, progress_callback=None):
        return mosh_cyber_glitch(self.ffmpeg, input_path, output_path, options, progress_callback)

    def mosh_flow_drift(self, input_path, output_path, options, progress_callback=None):
        return mosh_flow_drift(self.ffmpeg, input_path, output_path, options, progress_callback)

    def mosh_rgb_split(self, input_path, output_path, options, progress_callback=None):
        return mosh_rgb_split(self.ffmpeg, input_path, output_path, options, progress_callback)

    def mosh_audio_reactive(self, input_path, output_path, options, progress_callback=None):
        return mosh_audio_reactive(self.ffmpeg, input_path, output_path, options, progress_callback)

