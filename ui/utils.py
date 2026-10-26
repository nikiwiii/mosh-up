import os
import random
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect


def apply_card_shadow(widget, blur=18, offset_y=4, alpha=35):
    """Applies a subtle soft drop shadow effect to a card widget."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, offset_y)
    shadow.setColor(QColor(160, 175, 200, alpha))
    widget.setGraphicsEffect(shadow)


def generate_random_filename(input_path, mode=""):
    """Generates an output filename with random suffix in the input file's directory."""
    if not input_path:
        rand_id = random.randint(1000, 9999)
        return f"moshup_output_{rand_id}.mp4"

    dir_name = os.path.dirname(input_path) or "."
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    rand_id = random.randint(1000, 9999)

    mode_str = f"_{mode}" if mode else ""
    return os.path.join(dir_name, f"{base_name}_moshup{mode_str}_{rand_id}.mp4")
