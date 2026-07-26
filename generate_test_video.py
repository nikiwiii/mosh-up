"""
Helper script to generate a synthetic test video with motion and color transitions
to test datamoshing functionality.
"""

import cv2
import numpy as np
import os

def create_sample_video(filename="sample_test.mp4", duration_sec=4, fps=30):
    width, height = 640, 360
    total_frames = duration_sec * fps
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))

    print(f"Generowanie pliku wideo testowego {filename} ({total_frames} ramek)...")

    for i in range(total_frames):
        # Frame canvas with changing color backgrounds and moving shapes
        t = i / total_frames
        img = np.zeros((height, width, 3), dtype=np.uint8)

        if i < total_frames // 2:
            # Scene 1: Pulsing Cyan/Blue background with moving circle
            img[:, :, 0] = int(120 + 80 * np.sin(t * 10))  # B
            img[:, :, 1] = int(80 + 50 * np.cos(t * 8))   # G
            img[:, :, 2] = 20                              # R

            cx = int(100 + (width - 200) * (i / (total_frames // 2)))
            cy = int(height // 2 + 50 * np.sin(i * 0.2))
            cv2.circle(img, (cx, cy), 45, (0, 255, 255), -1)
            cv2.putText(img, "SCENA 1 (RUCH KOŁA)", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        else:
            # Scene 2: High contrast Orange/Red background with moving rectangle
            img[:, :, 0] = 30
            img[:, :, 1] = int(100 + 60 * np.sin(t * 12))
            img[:, :, 2] = int(180 + 70 * np.cos(t * 10))

            x1 = int(50 + (width - 200) * ((total_frames - i) / (total_frames // 2)))
            y1 = int(100 + 40 * np.cos(i * 0.15))
            cv2.rectangle(img, (x1, y1), (x1 + 100, y1 + 100), (255, 255, 0), -1)
            cv2.putText(img, "SCENA 2 (PRZEJŚCIE & RUCH)", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        # Add frame counter text
        cv2.putText(img, f"Frame {i}/{total_frames}", (40, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
        out.write(img)

    out.release()
    print(f"Utworzono plik testowy: {os.path.abspath(filename)}")
    return os.path.abspath(filename)

if __name__ == "__main__":
    create_sample_video()
