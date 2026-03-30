#!/usr/bin/env python3
"""
Generate device frame templates for iPhone and Android (Pixel-style).

Output:
  assets/iphone_frame.png   — iPhone 15 Pro-style frame (1030×2800)
  assets/android_frame.png  — Pixel-style frame (900×1980)

compose.py positions these dynamically based on text height.
"""

import os
from PIL import Image, ImageDraw, ImageChops

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ─── iPhone Frame Constants ─────────────────────────────────────────
IPHONE_W = 1030
IPHONE_H = 2800
IPHONE_CORNER_R = 77
IPHONE_BEZEL = 15
IPHONE_SCREEN_CORNER_R = 62
IPHONE_DI_W = 130
IPHONE_DI_H = 38
IPHONE_DI_TOP = 14
IPHONE_SCREEN_W = IPHONE_W - 2 * IPHONE_BEZEL
IPHONE_SCREEN_H = IPHONE_H - 2 * IPHONE_BEZEL

# ─── Android Frame Constants ────────────────────────────────────────
ANDROID_W = 900
ANDROID_H = 1980
ANDROID_CORNER_R = 55
ANDROID_BEZEL = 12
ANDROID_SCREEN_CORNER_R = 43
ANDROID_PUNCH_R = 16
ANDROID_PUNCH_TOP = 18
ANDROID_SCREEN_W = ANDROID_W - 2 * ANDROID_BEZEL
ANDROID_SCREEN_H = ANDROID_H - 2 * ANDROID_BEZEL


def generate_iphone():
    """Generate iPhone 15 Pro-style device frame with Dynamic Island."""
    frame = Image.new("RGBA", (IPHONE_W, IPHONE_H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # Device body — titanium-style outer shell
    fd.rounded_rectangle(
        [0, 0, IPHONE_W - 1, IPHONE_H - 1],
        radius=IPHONE_CORNER_R,
        fill=(42, 42, 42, 255),
    )
    fd.rounded_rectangle(
        [1, 1, IPHONE_W - 2, IPHONE_H - 2],
        radius=IPHONE_CORNER_R - 1,
        fill=(22, 22, 22, 255),
    )

    # Screen cutout (transparent)
    screen_x = IPHONE_BEZEL
    screen_y = IPHONE_BEZEL
    cutout = Image.new("L", (IPHONE_W, IPHONE_H), 255)
    ImageDraw.Draw(cutout).rounded_rectangle(
        [screen_x, screen_y, screen_x + IPHONE_SCREEN_W, screen_y + IPHONE_SCREEN_H],
        radius=IPHONE_SCREEN_CORNER_R,
        fill=0,
    )
    frame.putalpha(ImageChops.multiply(frame.getchannel("A"), cutout))

    # Dynamic Island
    di_x = (IPHONE_W - IPHONE_DI_W) // 2
    di_y = screen_y + IPHONE_DI_TOP
    ImageDraw.Draw(frame).rounded_rectangle(
        [di_x, di_y, di_x + IPHONE_DI_W, di_y + IPHONE_DI_H],
        radius=IPHONE_DI_H // 2,
        fill=(0, 0, 0, 255),
    )

    # Side buttons
    btn_color = (30, 30, 30, 255)
    fd2 = ImageDraw.Draw(frame)
    # Power (right)
    fd2.rounded_rectangle([IPHONE_W, 340, IPHONE_W + 4, 460], radius=2, fill=btn_color)
    # Volume up (left)
    fd2.rounded_rectangle([-4, 280, 0, 360], radius=2, fill=btn_color)
    # Volume down (left)
    fd2.rounded_rectangle([-4, 380, 0, 460], radius=2, fill=btn_color)
    # Silent switch (left)
    fd2.rounded_rectangle([-4, 180, 0, 220], radius=2, fill=btn_color)

    out = os.path.join(ASSETS_DIR, "iphone_frame.png")
    frame.save(out, "PNG")
    print(f"  iPhone frame: {out} ({IPHONE_W}x{IPHONE_H})")
    return out


def generate_android():
    """Generate Pixel-style Android device frame with punch-hole camera."""
    frame = Image.new("RGBA", (ANDROID_W, ANDROID_H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # Device body — matte black style
    fd.rounded_rectangle(
        [0, 0, ANDROID_W - 1, ANDROID_H - 1],
        radius=ANDROID_CORNER_R,
        fill=(35, 35, 35, 255),
    )
    fd.rounded_rectangle(
        [1, 1, ANDROID_W - 2, ANDROID_H - 2],
        radius=ANDROID_CORNER_R - 1,
        fill=(18, 18, 18, 255),
    )

    # Screen cutout (transparent)
    screen_x = ANDROID_BEZEL
    screen_y = ANDROID_BEZEL
    cutout = Image.new("L", (ANDROID_W, ANDROID_H), 255)
    ImageDraw.Draw(cutout).rounded_rectangle(
        [screen_x, screen_y, screen_x + ANDROID_SCREEN_W, screen_y + ANDROID_SCREEN_H],
        radius=ANDROID_SCREEN_CORNER_R,
        fill=0,
    )
    frame.putalpha(ImageChops.multiply(frame.getchannel("A"), cutout))

    # Punch-hole camera (centered, near top)
    punch_x = ANDROID_W // 2
    punch_y = screen_y + ANDROID_PUNCH_TOP + ANDROID_PUNCH_R
    fd2 = ImageDraw.Draw(frame)
    fd2.ellipse(
        [punch_x - ANDROID_PUNCH_R, punch_y - ANDROID_PUNCH_R,
         punch_x + ANDROID_PUNCH_R, punch_y + ANDROID_PUNCH_R],
        fill=(0, 0, 0, 255),
    )

    # Side buttons
    btn_color = (25, 25, 25, 255)
    # Power (right)
    fd2.rounded_rectangle([ANDROID_W, 280, ANDROID_W + 3, 380], radius=2, fill=btn_color)
    # Volume up (right, above power)
    fd2.rounded_rectangle([ANDROID_W, 420, ANDROID_W + 3, 500], radius=2, fill=btn_color)
    # Volume down (right, below vol up)
    fd2.rounded_rectangle([ANDROID_W, 520, ANDROID_W + 3, 600], radius=2, fill=btn_color)

    out = os.path.join(ASSETS_DIR, "android_frame.png")
    frame.save(out, "PNG")
    print(f"  Android frame: {out} ({ANDROID_W}x{ANDROID_H})")
    return out


if __name__ == "__main__":
    os.makedirs(ASSETS_DIR, exist_ok=True)
    print("Generating device frames...")
    generate_iphone()
    generate_android()
    print("Done.")
