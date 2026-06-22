import easyocr
import cv2
import numpy as np
import os
import re

frames_dir = r"D:\Descargas\smt_divergence\frames"
reader = easyocr.Reader(['en'], gpu=False)

files = sorted(os.listdir(frames_dir))
detail = [f for f in files if f.startswith("detail")]
key_frames = [f for f in files if f.startswith("frame_")]

# First analyze detail_01.jpg - it's a closeup of the indicator
for fname in detail + key_frames[:5]:
    path = os.path.join(frames_dir, fname)
    img = cv2.imread(path)
    if img is None:
        continue
    h, w, _ = img.shape
    print(f"\n{'='*60}")
    print(f"FILE: {fname} ({w}x{h})")
    print('='*60)

    # Extract text from the whole image
    results = reader.readtext(img)
    print(f"\nOCR RESULTS ({len(results)} texts found):")
    print("-"*40)
    for bbox, text, conf in results:
        if conf > 0.3:
            # Get position
            x_center = (bbox[0][0] + bbox[2][0]) / 2 / w
            y_center = (bbox[0][1] + bbox[2][1]) / 2 / h
            region = "left" if x_center < 0.33 else "center" if x_center < 0.66 else "right"
            print(f"  [{region}] (y={y_center:.2f}) [{conf:.2f}] {text.strip()}")

print("\n\nDONE")
