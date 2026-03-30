#!/usr/bin/env python3
"""
App Store & Google Play Screenshot Composer

Composites headline text, device frame template, and app screenshot
into pixel-perfect store-ready images.

Supports:
  - iOS (Apple App Store): 1320x2868 px  (6.9" iPhone 16 Pro Max)
  - Android (Google Play): 1080x1920 px  (standard phone)

Usage:
  python compose.py --platform ios --bg "#E31837" --verb "TRACK" \
    --desc "YOUR DAILY MOOD" --screenshot shot.png --output final.png

  python compose.py --platform android --bg "#1A73E8" --verb "DISCOVER" \
    --desc "NEW FEATURES" --screenshot shot.png --output final.png
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ─── Platform Configurations ────────────────────────────────────────

PLATFORMS = {
    "ios": {
        "canvas_w": 1320,
        "canvas_h": 2868,
        "device_w": 1054,
        "bezel": 15,
        "screen_corner_r": 65,
        "device_y": 740,
        "text_top": 200,
        "verb_size_max": 260,
        "verb_size_min": 150,
        "desc_size": 128,
        "frame_file": "iphone_frame.png",
    },
    "android": {
        "canvas_w": 1080,
        "canvas_h": 1920,
        "device_w": 900,
        "bezel": 12,
        "screen_corner_r": 43,
        "device_y": 520,
        "text_top": 130,
        "verb_size_max": 200,
        "verb_size_min": 120,
        "desc_size": 96,
        "frame_file": "android_frame.png",
    },
}

# ─── Typography ─────────────────────────────────────────────────────

VERB_DESC_GAP = 20
DESC_LINE_GAP = 24
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# Font search paths — tries SF Pro first, then common alternatives
FONT_CANDIDATES_BOLD = [
    "/Library/Fonts/SF-Pro-Display-Black.otf",
    "/Library/Fonts/SF-Pro-Display-Bold.otf",
    "/System/Library/Fonts/SFProDisplay-Black.otf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

FONT_CANDIDATES_REGULAR = [
    "/Library/Fonts/SF-Pro-Display-Regular.otf",
    "/System/Library/Fonts/SFProDisplay-Regular.otf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def find_font(candidates):
    """Return first available font path from candidates."""
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


FONT_PATH = find_font(FONT_CANDIDATES_BOLD)
FONT_PATH_REGULAR = find_font(FONT_CANDIDATES_REGULAR)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def luminance(rgb):
    """Perceived luminance (0-255)."""
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]


def text_color_for_bg(bg_rgb):
    """Return white or dark text depending on background brightness."""
    return (255, 255, 255) if luminance(bg_rgb) < 160 else (20, 20, 20)


def word_wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(text, max_w, size_max, size_min):
    """Return the largest font size where text fits within max_w."""
    if not FONT_PATH:
        return ImageFont.load_default()
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for size in range(size_max, size_min - 1, -4):
        font = ImageFont.truetype(FONT_PATH, size)
        bbox = dummy.textbbox((0, 0), text, font=font)
        if (bbox[2] - bbox[0]) <= max_w:
            return font
    return ImageFont.truetype(FONT_PATH, size_min)


def draw_centered(draw, y, text, font, fill, canvas_w, max_w=None):
    lines = word_wrap(draw, text, font, max_w) if max_w else [text]
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        draw.text(
            (canvas_w // 2, y - bbox[1]),
            line,
            fill=fill,
            font=font,
            anchor="mt",
        )
        y += h + DESC_LINE_GAP
    return y


def add_subtle_gradient(canvas, bg_rgb, canvas_w, canvas_h):
    """Add a subtle vertical gradient overlay for visual depth."""
    gradient = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)
    # Slightly lighter at top, slightly darker at bottom
    for y_pos in range(canvas_h):
        ratio = y_pos / canvas_h
        alpha = int(30 * ratio)  # subtle darkening toward bottom
        draw.line([(0, y_pos), (canvas_w, y_pos)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(canvas, gradient)


def compose(platform, bg_hex, verb, desc, screenshot_path, output_path,
            gradient=True):
    """Compose a store-ready screenshot."""
    cfg = PLATFORMS[platform]
    bg = hex_to_rgb(bg_hex)
    fill = text_color_for_bg(bg)

    canvas_w = cfg["canvas_w"]
    canvas_h = cfg["canvas_h"]
    device_w = cfg["device_w"]
    bezel = cfg["bezel"]
    screen_w = device_w - 2 * bezel
    screen_corner_r = cfg["screen_corner_r"]

    max_text_w = int(canvas_w * 0.92)
    max_verb_w = int(canvas_w * 0.92)

    # ── 1. Canvas ───────────────────────────────────────────────────
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (*bg, 255))

    if gradient:
        canvas = add_subtle_gradient(canvas, bg, canvas_w, canvas_h)

    draw = ImageDraw.Draw(canvas)

    # ── 2. Typography ───────────────────────────────────────────────
    verb_font = fit_font(
        verb.upper(), max_verb_w, cfg["verb_size_max"], cfg["verb_size_min"]
    )
    desc_font = (
        ImageFont.truetype(FONT_PATH, cfg["desc_size"])
        if FONT_PATH
        else ImageFont.load_default()
    )

    # Draw text
    y = cfg["text_top"]
    y = draw_centered(draw, y, verb.upper(), verb_font, fill, canvas_w)
    y += VERB_DESC_GAP
    draw_centered(draw, y, desc.upper(), desc_font, fill, canvas_w, max_w=max_text_w)

    # ── 3. Device positioning ───────────────────────────────────────
    device_y = cfg["device_y"]
    device_x = (canvas_w - device_w) // 2
    screen_x = device_x + bezel
    screen_y = device_y + bezel

    # ── 4. Screenshot into screen area ──────────────────────────────
    shot = Image.open(screenshot_path).convert("RGBA")
    scale = screen_w / shot.width
    sc_w = screen_w
    sc_h = int(shot.height * scale)
    shot = shot.resize((sc_w, sc_h), Image.LANCZOS)

    screen_h = canvas_h - screen_y + 500

    scr_mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(scr_mask).rounded_rectangle(
        [screen_x, screen_y, screen_x + screen_w, screen_y + screen_h],
        radius=screen_corner_r,
        fill=255,
    )

    scr_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(scr_layer).rounded_rectangle(
        [screen_x, screen_y, screen_x + screen_w, screen_y + screen_h],
        radius=screen_corner_r,
        fill=(0, 0, 0, 255),
    )
    scr_layer.paste(shot, (screen_x, screen_y))
    scr_layer.putalpha(scr_mask)
    canvas = Image.alpha_composite(canvas, scr_layer)

    # ── 5. Device frame overlay ─────────────────────────────────────
    frame_path = os.path.join(ASSETS_DIR, cfg["frame_file"])
    if os.path.exists(frame_path):
        frame_template = Image.open(frame_path).convert("RGBA")
        frame_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        frame_layer.paste(frame_template, (device_x, device_y))
        canvas = Image.alpha_composite(canvas, frame_layer)

    # ── 6. Save ─────────────────────────────────────────────────────
    canvas.convert("RGB").save(output_path, "PNG")
    print(f"  {output_path} ({canvas_w}x{canvas_h})")


def main():
    p = argparse.ArgumentParser(description="Compose store screenshot")
    p.add_argument(
        "--platform",
        required=True,
        choices=["ios", "android"],
        help="Target platform (ios or android)",
    )
    p.add_argument("--bg", required=True, help="Background hex colour (#E31837)")
    p.add_argument("--verb", required=True, help="Action verb headline (TRACK)")
    p.add_argument(
        "--desc", required=True, help="Benefit descriptor (YOUR DAILY MOOD)"
    )
    p.add_argument("--screenshot", required=True, help="App screenshot path")
    p.add_argument("--output", required=True, help="Output file path")
    p.add_argument(
        "--no-gradient",
        action="store_true",
        help="Disable subtle background gradient",
    )
    args = p.parse_args()

    compose(
        args.platform,
        args.bg,
        args.verb,
        args.desc,
        args.screenshot,
        args.output,
        gradient=not args.no_gradient,
    )


if __name__ == "__main__":
    main()
