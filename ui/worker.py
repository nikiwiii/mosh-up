from PySide6.QtCore import QThread, Signal
from datamosh_engine import DatamoshEngine


class DatamoshWorker(QThread):
    """
    Background worker thread for running datamosh operations
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
