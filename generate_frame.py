#!/usr/bin/env python3
"""
Generate device frame templates for iPhone and Android (Pixel-style).

Output:
  assets/iphone_frame.png   — iPhone 16 Pro Max-style frame (1054×2870)
  assets/android_frame.png  — Pixel-style frame (900×1980)

compose.py positions these dynamically based on text height.
"""

import os
from PIL import Image, ImageDraw, ImageChops, ImageFilter

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ─── iPhone Frame Constants (6.9" — iPhone 16 Pro Max) ─────────────
IPHONE_W = 1054
IPHONE_H = 2870
IPHONE_CORNER_R = 80
IPHONE_BEZEL = 20
IPHONE_SCREEN_CORNER_R = 60
IPHONE_DI_W = 200
IPHONE_DI_H = 56
IPHONE_DI_TOP = 18
IPHONE_SCREEN_W = IPHONE_W - 2 * IPHONE_BEZEL
IPHONE_SCREEN_H = IPHONE_H - 2 * IPHONE_BEZEL

# ─── Android Frame Constants ────────────────────────────────────────
ANDROID_W = 900
ANDROID_H = 1980
ANDROID_CORNER_R = 55
ANDROID_BEZEL = 14
ANDROID_SCREEN_CORNER_R = 41
ANDROID_PUNCH_R = 16
ANDROID_PUNCH_TOP = 20
ANDROID_SCREEN_W = ANDROID_W - 2 * ANDROID_BEZEL
ANDROID_SCREEN_H = ANDROID_H - 2 * ANDROID_BEZEL


def generate_iphone():
    """Generate iPhone 16 Pro Max-style device frame with Dynamic Island."""
    frame = Image.new("RGBA", (IPHONE_W, IPHONE_H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # ── Titanium outer shell — 3-layer depth ────────────────────────
    # Outermost edge — subtle metallic highlight
    fd.rounded_rectangle(
        [0, 0, IPHONE_W - 1, IPHONE_H - 1],
        radius=IPHONE_CORNER_R,
        fill=(58, 58, 60, 255),
    )
    # Mid-layer — titanium body
    fd.rounded_rectangle(
        [2, 2, IPHONE_W - 3, IPHONE_H - 3],
        radius=IPHONE_CORNER_R - 2,
        fill=(44, 44, 46, 255),
    )
    # Inner edge — darker toward screen
    fd.rounded_rectangle(
        [4, 4, IPHONE_W - 5, IPHONE_H - 5],
        radius=IPHONE_CORNER_R - 4,
        fill=(28, 28, 30, 255),
    )

    # ── Screen cutout (transparent) ─────────────────────────────────
    screen_x = IPHONE_BEZEL
    screen_y = IPHONE_BEZEL
    cutout = Image.new("L", (IPHONE_W, IPHONE_H), 255)
    ImageDraw.Draw(cutout).rounded_rectangle(
        [screen_x, screen_y, screen_x + IPHONE_SCREEN_W, screen_y + IPHONE_SCREEN_H],
        radius=IPHONE_SCREEN_CORNER_R,
        fill=0,
    )
    frame.putalpha(ImageChops.multiply(frame.getchannel("A"), cutout))

    # ── Dynamic Island — prominent pill with subtle depth ───────────
    di_x = (IPHONE_W - IPHONE_DI_W) // 2
    di_y = screen_y + IPHONE_DI_TOP
    fd2 = ImageDraw.Draw(frame)

    # Outer shadow ring for depth
    fd2.rounded_rectangle(
        [di_x - 2, di_y - 2, di_x + IPHONE_DI_W + 2, di_y + IPHONE_DI_H + 2],
        radius=(IPHONE_DI_H + 4) // 2,
        fill=(10, 10, 10, 180),
    )
    # Main Dynamic Island body
    fd2.rounded_rectangle(
        [di_x, di_y, di_x + IPHONE_DI_W, di_y + IPHONE_DI_H],
        radius=IPHONE_DI_H // 2,
        fill=(0, 0, 0, 255),
    )
    # Subtle front camera lens inside (right side of pill)
    cam_r = 8
    cam_x = di_x + IPHONE_DI_W - 38
    cam_y = di_y + IPHONE_DI_H // 2
    fd2.ellipse(
        [cam_x - cam_r, cam_y - cam_r, cam_x + cam_r, cam_y + cam_r],
        fill=(18, 18, 22, 255),
    )
    # Camera lens highlight
    hl_r = 3
    fd2.ellipse(
        [cam_x - hl_r, cam_y - hl_r - 1, cam_x + hl_r, cam_y + hl_r - 1],
        fill=(35, 35, 42, 255),
    )

    # ── Side buttons — thicker with metallic look ───────────────────
    btn_outer = (50, 50, 52, 255)
    btn_inner = (36, 36, 38, 255)

    # Power button (right side) — larger
    fd2.rounded_rectangle(
        [IPHONE_W - 1, 360, IPHONE_W + 5, 500], radius=3, fill=btn_outer
    )
    fd2.rounded_rectangle(
        [IPHONE_W, 362, IPHONE_W + 4, 498], radius=2, fill=btn_inner
    )

    # Volume up (left side)
    fd2.rounded_rectangle([-5, 300, 1, 390], radius=3, fill=btn_outer)
    fd2.rounded_rectangle([-4, 302, 0, 388], radius=2, fill=btn_inner)

    # Volume down (left side)
    fd2.rounded_rectangle([-5, 410, 1, 500], radius=3, fill=btn_outer)
    fd2.rounded_rectangle([-4, 412, 0, 498], radius=2, fill=btn_inner)

    # Action button (left side, smaller)
    fd2.rounded_rectangle([-5, 200, 1, 250], radius=3, fill=btn_outer)
    fd2.rounded_rectangle([-4, 202, 0, 248], radius=2, fill=btn_inner)

    out = os.path.join(ASSETS_DIR, "iphone_frame.png")
    frame.save(out, "PNG")
    print(f"  iPhone frame: {out} ({IPHONE_W}x{IPHONE_H})")
    return out


def generate_android():
    """Generate Pixel-style Android device frame with punch-hole camera."""
    frame = Image.new("RGBA", (ANDROID_W, ANDROID_H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # ── Device body — 3-layer depth ─────────────────────────────────
    fd.rounded_rectangle(
        [0, 0, ANDROID_W - 1, ANDROID_H - 1],
        radius=ANDROID_CORNER_R,
        fill=(48, 48, 50, 255),
    )
    fd.rounded_rectangle(
        [2, 2, ANDROID_W - 3, ANDROID_H - 3],
        radius=ANDROID_CORNER_R - 2,
        fill=(32, 32, 34, 255),
    )
    fd.rounded_rectangle(
        [3, 3, ANDROID_W - 4, ANDROID_H - 4],
        radius=ANDROID_CORNER_R - 3,
        fill=(20, 20, 22, 255),
    )

    # ── Screen cutout (transparent) ─────────────────────────────────
    screen_x = ANDROID_BEZEL
    screen_y = ANDROID_BEZEL
    cutout = Image.new("L", (ANDROID_W, ANDROID_H), 255)
    ImageDraw.Draw(cutout).rounded_rectangle(
        [screen_x, screen_y, screen_x + ANDROID_SCREEN_W, screen_y + ANDROID_SCREEN_H],
        radius=ANDROID_SCREEN_CORNER_R,
        fill=0,
    )
    frame.putalpha(ImageChops.multiply(frame.getchannel("A"), cutout))

    # ── Punch-hole camera (centered, near top) ──────────────────────
    punch_x = ANDROID_W // 2
    punch_y = screen_y + ANDROID_PUNCH_TOP + ANDROID_PUNCH_R
    fd2 = ImageDraw.Draw(frame)
    # Outer ring
    fd2.ellipse(
        [punch_x - ANDROID_PUNCH_R - 2, punch_y - ANDROID_PUNCH_R - 2,
         punch_x + ANDROID_PUNCH_R + 2, punch_y + ANDROID_PUNCH_R + 2],
        fill=(8, 8, 8, 200),
    )
    # Camera hole
    fd2.ellipse(
        [punch_x - ANDROID_PUNCH_R, punch_y - ANDROID_PUNCH_R,
         punch_x + ANDROID_PUNCH_R, punch_y + ANDROID_PUNCH_R],
        fill=(0, 0, 0, 255),
    )

    # ── Side buttons ────────────────────────────────────────────────
    btn_outer = (42, 42, 44, 255)
    btn_inner = (28, 28, 30, 255)

    # Power (right)
    fd2.rounded_rectangle(
        [ANDROID_W - 1, 300, ANDROID_W + 4, 400], radius=2, fill=btn_outer
    )
    fd2.rounded_rectangle(
        [ANDROID_W, 302, ANDROID_W + 3, 398], radius=2, fill=btn_inner
    )
    # Volume up (right, below power)
    fd2.rounded_rectangle(
        [ANDROID_W - 1, 440, ANDROID_W + 4, 520], radius=2, fill=btn_outer
    )
    fd2.rounded_rectangle(
        [ANDROID_W, 442, ANDROID_W + 3, 518], radius=2, fill=btn_inner
    )
    # Volume down (right, below vol up)
    fd2.rounded_rectangle(
        [ANDROID_W - 1, 540, ANDROID_W + 4, 620], radius=2, fill=btn_outer
    )
    fd2.rounded_rectangle(
        [ANDROID_W, 542, ANDROID_W + 3, 618], radius=2, fill=btn_inner
    )

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
