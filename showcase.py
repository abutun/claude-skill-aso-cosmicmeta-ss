#!/usr/bin/env python3
"""
Showcase Image Generator

Creates a preview image showing final App Store / Google Play screenshots
side-by-side on a clean background, organized by platform.
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageFont

# ─── Layout ─────────────────────────────────────────────────────────
PADDING = 60
GAP = 40
SECTION_GAP = 80
LABEL_H = 80
FONT_SIZE_MAX = 48
FONT_SIZE_MIN = 16
BG_COLOUR = (255, 255, 255)
LABEL_COLOUR = (60, 60, 60)

FONT_CANDIDATES = [
    "/Library/Fonts/SF-Pro-Display-Medium.otf",
    "/Library/Fonts/SF-Pro-Display-Regular.otf",
    "/System/Library/Fonts/SFProDisplay-Regular.otf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def find_font():
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


FONT_PATH = find_font()


def load_font(size):
    if FONT_PATH:
        return ImageFont.truetype(FONT_PATH, size)
    return ImageFont.load_default()


def create_showcase(ios_screenshots=None, android_screenshots=None,
                    output_path="showcase.png"):
    """Create a showcase with iOS and/or Android screenshots side-by-side."""
    sections = []

    if ios_screenshots:
        sections.append(("Apple App Store (iOS)", ios_screenshots))
    if android_screenshots:
        sections.append(("Google Play Store (Android)", android_screenshots))

    if not sections:
        print("No screenshots provided.")
        return

    target_h = 700
    all_rows = []

    for label, paths in sections:
        images = [Image.open(p).convert("RGBA") for p in paths]
        scaled = []
        for img in images:
            ratio = target_h / img.height
            scaled.append(
                img.resize((int(img.width * ratio), target_h), Image.LANCZOS)
            )
        row_w = sum(s.width for s in scaled) + GAP * (len(scaled) - 1)
        all_rows.append((label, scaled, row_w))

    max_row_w = max(rw for _, _, rw in all_rows)
    canvas_w = max_row_w + PADDING * 2

    # Calculate total height
    total_h = PADDING
    for i, (label, scaled, _) in enumerate(all_rows):
        total_h += LABEL_H + target_h
        if i < len(all_rows) - 1:
            total_h += SECTION_GAP
    total_h += PADDING

    canvas = Image.new("RGB", (canvas_w, total_h), BG_COLOUR)
    draw = ImageDraw.Draw(canvas)

    y_cursor = PADDING
    label_font = load_font(36)

    for label, scaled, row_w in all_rows:
        # Draw section label
        draw.text(
            (canvas_w // 2, y_cursor + LABEL_H // 2),
            label,
            fill=LABEL_COLOUR,
            font=label_font,
            anchor="mm",
        )
        y_cursor += LABEL_H

        # Place screenshots centered
        x = (canvas_w - row_w) // 2
        for s in scaled:
            canvas.paste(s, (x, y_cursor), s if s.mode == "RGBA" else None)
            x += s.width + GAP

        y_cursor += target_h + SECTION_GAP

    canvas.save(output_path, "PNG")
    print(f"  {output_path} ({canvas_w}x{total_h})")


def main():
    p = argparse.ArgumentParser(description="Generate showcase image")
    p.add_argument(
        "--ios",
        nargs="+",
        default=None,
        help="Paths to iOS final screenshot PNGs",
    )
    p.add_argument(
        "--android",
        nargs="+",
        default=None,
        help="Paths to Android final screenshot PNGs",
    )
    p.add_argument("--output", required=True, help="Output file path")
    args = p.parse_args()

    create_showcase(
        ios_screenshots=args.ios,
        android_screenshots=args.android,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
