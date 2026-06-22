import cv2
import numpy as np
import os
from collections import Counter

frames_dir = r"D:\Descargas\smt_divergence\frames"
files = sorted(os.listdir(frames_dir))

print(f"Total frames: {len(files)}")

# Analyze key frames
key_frames = [f for f in files if f.startswith("frame_")]
detail = [f for f in files if f.startswith("detail")]

for fname in key_frames[:10] + detail:
    path = os.path.join(frames_dir, fname)
    img = cv2.imread(path)
    if img is None:
        continue
    h, w, c = img.shape
    print(f"\n=== {fname} ({w}x{h}) ===")

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Predominant colors
    pixels = img.reshape(-1, 3)
    sampled = pixels[::100]
    sampled_tuples = [tuple(p) for p in sampled]
    color_counts = Counter(sampled_tuples)
    top_colors = color_counts.most_common(10)
    print("Top colors (BGR):")
    for bgr, cnt in top_colors:
        pct = cnt / len(sampled) * 100
        print(f"  {bgr} = {pct:.1f}%")

    # Lines
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
    if lines is not None:
        h_lines = v_lines = d_lines = 0
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            if angle < 10 or angle > 170: h_lines += 1
            elif 80 < angle < 100: v_lines += 1
            else: d_lines += 1
        print(f"Lines: {h_lines}H {v_lines}V {d_lines}D")

    # Color region detection
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    green_pct = np.sum(cv2.inRange(hsv, lower_green, upper_green) > 0) / (h*w) * 100

    lower_red1 = np.array([0, 40, 40])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 40, 40])
    upper_red2 = np.array([180, 255, 255])
    red_pct = np.sum((cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)) > 0) / (h*w) * 100

    lower_blue = np.array([100, 30, 30])
    upper_blue = np.array([130, 255, 255])
    blue_pct = np.sum(cv2.inRange(hsv, lower_blue, upper_blue) > 0) / (h*w) * 100

    lower_purple = np.array([125, 30, 30])
    upper_purple = np.array([155, 255, 255])
    purple_pct = np.sum(cv2.inRange(hsv, lower_purple, upper_purple) > 0) / (h*w) * 100

    lower_yellow = np.array([20, 40, 40])
    upper_yellow = np.array([35, 255, 255])
    yellow_pct = np.sum(cv2.inRange(hsv, lower_yellow, upper_yellow) > 0) / (h*w) * 100

    print(f"Colors: Green={green_pct:.2f}% Red={red_pct:.2f}% Blue={blue_pct:.2f}% Purple={purple_pct:.2f}% Yellow={yellow_pct:.2f}%")

    # Text regions
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    text_regions = sum(1 for cnt in contours if 10 < cv2.boundingRect(cnt)[2] < 200 and 5 < cv2.boundingRect(cnt)[3] < 50)
    print(f"Text regions: {text_regions}")

print("\n=== DETAIL ANALYSIS ===")
for fname in detail:
    path = os.path.join(frames_dir, fname)
    img = cv2.imread(path)
    if img is None:
        continue
    h, w, c = img.shape
    print(f"\n--- {fname} ({w}x{h}) ---")

    # Focus on the indicator panel area (right 30% of image)
    panel = img[:, int(w*0.65):]
    ph, pw, _ = panel.shape
    hsv_p = cv2.cvtColor(panel, cv2.COLOR_BGR2HSV)

    # Analyze panel colors
    low_g = np.array([40, 30, 30])
    high_g = np.array([85, 255, 255])
    g = np.sum(cv2.inRange(hsv_p, low_g, high_g) > 0) / (ph*pw) * 100

    low_r1 = np.array([0, 30, 30])
    high_r1 = np.array([10, 255, 255])
    low_r2 = np.array([170, 30, 30])
    high_r2 = np.array([180, 255, 255])
    r = np.sum((cv2.inRange(hsv_p, low_r1, high_r1) | cv2.inRange(hsv_p, low_r2, high_r2)) > 0) / (ph*pw) * 100

    low_b = np.array([100, 30, 30])
    high_b = np.array([140, 255, 255])
    b = np.sum(cv2.inRange(hsv_p, low_b, high_b) > 0) / (ph*pw) * 100

    low_w = np.array([0, 0, 200])
    high_w = np.array([180, 30, 255])
    w_pct = np.sum(cv2.inRange(hsv_p, low_w, high_w) > 0) / (ph*pw) * 100

    print(f"Panel (right 35%): Green={g:.2f}% Red={r:.2f}% Blue={b:.2f}% White={w_pct:.2f}%")

    # Detect horizontal zones in panel (potential indicator rows)
    panel_gray = cv2.cvtColor(panel, cv2.COLOR_BGR2GRAY)
    # Horizontal projection
    h_proj = np.sum(panel_gray < 100, axis=1)  # count dark pixels per row
    # Find rows with significant dark content
    threshold_row = pw * 0.3
    dark_rows = np.where(h_proj > threshold_row)[0]
    if len(dark_rows) > 0:
        # Find contiguous row blocks
        gaps = np.diff(dark_rows)
        breaks = np.where(gaps > 3)[0]
        row_groups = np.split(dark_rows, breaks + 1)
        print(f"Panel horizontal zones: {len(row_groups)}")
        for i, rg in enumerate(row_groups):
            if len(rg) > 5:
                print(f"  Zone {i}: rows {rg[0]}-{rg[-1]} ({len(rg)} rows)")

    # Detect colored labels (small bright colored regions)
    # Look for green/red/blue small text-like regions
    for color_name, mask_range in [("Green", (np.array([40, 50, 100]), np.array([80, 255, 255]))),
                                    ("Red", (np.array([0, 50, 100]), np.array([8, 255, 255]))),
                                    ("Blue", (np.array([100, 50, 100]), np.array([130, 255, 255])))]:
        mask = cv2.inRange(hsv_p, mask_range[0], mask_range[1])
        # Clean up noise
        kernel = np.ones((2,2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        contours_c, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        valid = [c for c in contours_c if 15 < cv2.contourArea(c) < 500]
        if valid:
            print(f"  {color_name} label-like regions: {len(valid)} (avg area: {np.mean([cv2.contourArea(c) for c in valid]):.0f}px)")
