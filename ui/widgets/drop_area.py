from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QMessageBox
from lucide_icons import get_lucide_pixmap


class DropAreaWidget(QFrame):
    """
    Drag and drop target area for video files with modern dotted border styling.
    """
    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropArea")
        self.setStyleSheet("""
            QFrame#dropArea {
                border: 2px dashed #cad5e2;
                border-radius: 20px;
                background-color: #f8fafc;
            }
            QFrame#dropArea:hover {
                background-color: #ffffff;
                border: 2px dashed #151829;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 40, 32, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(get_lucide_pixmap("upload", color="#475569", size=54))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_title = QLabel("Przeciągnij i upuść plik wideo tutaj", self)
        self.text_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #1e293b; background: transparent;")
        self.text_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_subtitle = QLabel("lub wybierz plik z dysku komputera\nObsługiwane formaty: MP4, MOV, MKV, AVI, WEBM", self)
        self.text_subtitle.setStyleSheet("font-size: 12px; font-weight: 500; color: #64748b; background: transparent; line-height: 1.4;")
        self.text_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_title)
        layout.addWidget(self.text_subtitle)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv')):
                self.file_dropped.emit(file_path)
            else:
                QMessageBox.warning(self, "Nieobsługiwany format", "Wybierz prawidłowy plik wideo (MP4, AVI, MOV, MKV, WEBM)")
