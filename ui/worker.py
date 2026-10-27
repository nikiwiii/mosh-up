import os
import subprocess
from PySide6.QtCore import QThread, Signal
from datamosh_engine import DatamoshEngine, get_ffmpeg_exe, cleanup_temp_files


class DatamoshWorker(QThread):
    """
    Background worker thread for running full datamosh operations
    without blocking the PySide6 UI event loop.
    """
    progress_signal = Signal(int, str)
    finished_signal = Signal(str)
    error_signal = Signal(str)

    def __init__(self, mode, input_path, output_path, options):
        super().__init__()
        self.mode = mode
        self.input_path = input_path
        self.output_path = output_path
        self.options = options
        self.engine = DatamoshEngine()

    def run(self):
        try:
            def cb(pct, msg):
                self.progress_signal.emit(pct, msg)

            self.engine.process(self.mode, self.input_path, self.output_path, self.options, progress_callback=cb)
            self.finished_signal.emit(self.output_path)
        except Exception as e:
            self.error_signal.emit(str(e))


class FastDraftWorker(QThread):
    """
    Background worker thread for generating a 3-second Fast Draft preview clip.
    Extracts a 3-second slice from the source video, applies the chosen datamosh
    mode with current parameters, and outputs a temporary preview file.
    """
    progress_signal = Signal(int, str)
    finished_signal = Signal(str)
    error_signal = Signal(str)

    def __init__(self, mode, input_path_a, input_path_b, output_draft_path, options, t_start=0.0):
        super().__init__()
        self.mode = mode
        self.input_path_a = input_path_a
        self.input_path_b = input_path_b
        self.output_draft_path = output_draft_path
        self.options = options
        self.t_start = max(0.0, float(t_start))
        self.ffmpeg = get_ffmpeg_exe()
        self.engine = DatamoshEngine(ffmpeg_path=self.ffmpeg)

    def run(self):
        temp_dir = os.path.dirname(self.output_draft_path) or "."
        temp_cut_a = os.path.join(temp_dir, "_temp_draft_cut_a.mp4")
        temp_cut_b = os.path.join(temp_dir, "_temp_draft_cut_b.mp4")

        try:
            self.progress_signal.emit(15, "Wycinanie 3-sekundowego fragmentu...")
            cmd_cut_a = [
                self.ffmpeg, "-y",
                "-ss", f"{self.t_start:.2f}",
                "-i", self.input_path_a,
                "-t", "3.0",
                "-c:v", "libx264", "-preset", "ultrafast",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                temp_cut_a
            ]
            proc_a = subprocess.run(cmd_cut_a, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if proc_a.returncode != 0 or not os.path.exists(temp_cut_a):
                cmd_cut_a_fallback = [
                    self.ffmpeg, "-y",
                    "-i", self.input_path_a,
                    "-t", "3.0",
                    "-c:v", "libx264", "-preset", "ultrafast",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    temp_cut_a
                ]
                subprocess.run(cmd_cut_a_fallback, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            draft_options = dict(self.options)

            if self.mode == 'stitch_mosh':
                if not self.input_path_b or not os.path.exists(self.input_path_b):
                    raise ValueError("Brak drugiego pliku wideo B dla trybu Stitch Mosh!")
                cmd_cut_b = [
                    self.ffmpeg, "-y",
                    "-i", self.input_path_b,
                    "-t", "3.0",
                    "-c:v", "libx264", "-preset", "ultrafast",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    temp_cut_b
                ]
                subprocess.run(cmd_cut_b, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                draft_options['input_b'] = temp_cut_b

            elif self.mode == 'volcano_melt':
                draft_options['start_sec'] = 0.0
                draft_options['end_sec'] = 3.0
                draft_options['video_duration'] = 3.0

            def cb(pct, msg):
                mapped_pct = 20 + int(pct * 0.75)
                self.progress_signal.emit(mapped_pct, f"Fast Draft: {msg}")

            self.engine.process(self.mode, temp_cut_a, self.output_draft_path, draft_options, progress_callback=cb)
            self.finished_signal.emit(self.output_draft_path)

        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            cleanup_temp_files(temp_cut_a, temp_cut_b)
