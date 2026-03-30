#!/usr/bin/env python3
"""
Gemini AI Screenshot Enhancer

Uses Google's Gemini API (Imagen models) to enhance deterministic screenshot
scaffolds with professional-quality visuals — lighting, textures, reflections,
and polished backgrounds.

Supported models:
  - nano-banana-pro  (higher quality, slower)
  - nano-banana-2    (faster, good quality)

Usage:
  # Enhance a single screenshot (model is required)
  python gemini_enhance.py \
    --input output/ios/screenshot_1.png \
    --output output/ios/screenshot_1_enhanced.png \
    --model nano-banana-pro \
    --api-key "YOUR_GEMINI_API_KEY"

  # Use environment variable for API key
  export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
  python gemini_enhance.py \
    --input output/ios/screenshot_1.png \
    --output output/ios/screenshot_1_enhanced.png \
    --model nano-banana-2

  # Batch enhance all screenshots in a directory
  python gemini_enhance.py \
    --input-dir output/ios/ \
    --output-dir output/ios/enhanced/ \
    --model nano-banana-pro

  # Enhance with custom prompt
  python gemini_enhance.py \
    --input screenshot.png \
    --output enhanced.png \
    --model nano-banana-pro \
    --prompt "Add subtle glass reflection on the device screen and warm lighting"
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip3 install Pillow")
    sys.exit(1)

# ─── Defaults ───────────────────────────────────────────────────────

DEFAULT_MODEL = "nano-banana-pro"
SUPPORTED_MODELS = ["nano-banana-pro", "nano-banana-2", "nano-banana",
                    "gemini-3-pro-image-preview", "gemini-3.1-flash-image-preview",
                    "gemini-2.5-flash-image"]
MODEL_ALIASES = {
    "nano-banana-pro": "gemini-3-pro-image-preview",
    "nano-banana-2": "gemini-3.1-flash-image-preview",
    "nano-banana": "gemini-2.5-flash-image",
}

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

DEFAULT_ENHANCE_PROMPT = (
    "Transform this app store screenshot into a premium, high-converting visual "
    "that makes users want to download the app within 3 seconds. "
    "\n\n"
    "CRITICAL TEXT RULES:\n"
    "- The headline text MUST remain clearly readable with maximum contrast\n"
    "- If the background is dark, text MUST be bright white with a subtle glow/shadow\n"
    "- If the background is light, text MUST be deep black or dark color\n"
    "- Text should NEVER blend into or be hard to read against the background\n"
    "- Keep the exact same text content, font style, and positioning\n"
    "- NEVER alter, strip, or replace language-specific characters "
    "(Turkish: İ,Ç,Ö,Ü,Ğ,Ş / German: Ä,Ö,Ü,ß / accented: É,Ñ,À, etc.)\n"
    "- Preserve every character exactly as shown — incorrect letters destroy readability\n"
    "\n"
    "VISUAL ENHANCEMENTS:\n"
    "- Add floating decorative elements related to the app's purpose "
    "(icons, abstract shapes, particles, sparkles, emoji-style graphics)\n"
    "- Create depth with layered elements at different sizes and opacities\n"
    "- Add subtle ambient lighting, glows, and lens flare effects\n"
    "- Enhance the background with rich gradients, organic shapes, or abstract patterns\n"
    "- Add soft shadows and reflections around the device frame\n"
    "- Consider tilting the device slightly (5-15 degrees) for a dynamic, "
    "3D perspective feel\n"
    "- Add small floating UI elements or app-related icons that break outside "
    "the device frame for a \"breakout\" effect\n"
    "\n"
    "STYLE REFERENCE:\n"
    "- Think premium App Store featured apps (Apple, Headspace, Calm style)\n"
    "- Rich, vibrant backgrounds with depth and dimension\n"
    "- Professional marketing material quality, not a plain mockup\n"
    "- The overall composition should feel like a designer spent hours on it\n"
    "\n"
    "CONSTRAINTS:\n"
    "- Keep the app screenshot content inside the device exactly as shown\n"
    "- Maintain the exact same image dimensions\n"
    "- The device frame should remain visible and recognizable\n"
    "- Do NOT add any new text — only enhance the existing text's visibility"
)

# Alternate prompt for variety (used for even-numbered screenshots)
ALTERNATE_ENHANCE_PROMPT = (
    "Create a stunning, award-winning app store screenshot from this mockup. "
    "\n\n"
    "CRITICAL TEXT RULES:\n"
    "- Headline text MUST have maximum readability — bright white on dark "
    "backgrounds, deep dark on light backgrounds\n"
    "- Add a subtle text glow or shadow to ensure text pops against any background\n"
    "- Keep the exact same text content and positioning\n"
    "- NEVER alter, strip, or replace language-specific characters "
    "(Turkish: İ,Ç,Ö,Ü,Ğ,Ş / German: Ä,Ö,Ü,ß / accented: É,Ñ,À, etc.)\n"
    "- Preserve every character exactly as shown — incorrect letters destroy readability\n"
    "\n"
    "VISUAL STYLE:\n"
    "- Tilt the phone at a slight angle (10-20 degrees) for a dynamic, "
    "editorial magazine feel\n"
    "- Add floating 3D elements, abstract shapes, and decorative graphics "
    "that relate to the app's theme\n"
    "- Use dramatic lighting — soft glows, ambient light sources, "
    "bokeh-style background elements\n"
    "- Add depth with elements at multiple layers (foreground, mid, background)\n"
    "- Include subtle particle effects, sparkles, or floating icons\n"
    "- Create a rich, immersive atmosphere around the device\n"
    "\n"
    "QUALITY:\n"
    "- This should look like it was designed by a top creative agency\n"
    "- Think Apple keynote presentation quality\n"
    "- Professional, polished, and visually striking\n"
    "\n"
    "CONSTRAINTS:\n"
    "- Preserve the app content inside the device screen exactly\n"
    "- Maintain exact image dimensions\n"
    "- Keep device frame visible\n"
    "- Do NOT add new text, only enhance existing text visibility"
)

# ─── Store dimensions for final crop ────────────────────────────────

PLATFORM_DIMS = {
    "ios": (1320, 2868),
    "android": (1080, 1920),
}


def get_api_key(cli_key=None):
    """Resolve API key from CLI arg, env var, or config file."""
    if cli_key:
        return cli_key

    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key:
        return env_key

    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".gemini_config.json"
    )
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
            if config.get("api_key"):
                return config["api_key"]

    return None


def save_api_key(api_key):
    """Save API key to local config file for future use."""
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".gemini_config.json"
    )
    config = {}
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
    config["api_key"] = api_key
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"  API key saved to {config_path}")


def image_to_base64(image_path):
    """Read image file and return base64 encoded string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def detect_platform(image_path):
    """Detect platform from image dimensions."""
    img = Image.open(image_path)
    w, h = img.size
    if w == 1320 and h == 2868:
        return "ios"
    elif w == 1080 and h == 1920:
        return "android"
    return None


def build_prompt(base_prompt, app_desc=None, bg_color=None):
    """Build the final prompt with optional app context."""
    parts = [base_prompt]
    if app_desc:
        parts.append(
            f"\n\nAPP CONTEXT: This is a screenshot for '{app_desc}'. "
            f"Add floating decorative elements, icons, and graphics that relate "
            f"to this app's theme and purpose."
        )
    if bg_color:
        parts.append(
            f"\n\nBACKGROUND COLOR: The base background is {bg_color}. "
            f"Enhance it with gradients and depth while keeping the same color family."
        )
    return "".join(parts)


def enhance_with_gemini(image_path, output_path, api_key, model=DEFAULT_MODEL,
                        prompt=None, platform=None, app_desc=None,
                        bg_color=None, index=0):
    """Send image to Gemini for enhancement and save the result."""
    if model not in SUPPORTED_MODELS:
        print(f"  Error: Unknown model '{model}'. Supported: {', '.join(SUPPORTED_MODELS)}")
        return False

    # Resolve friendly alias to actual API model ID
    model = MODEL_ALIASES.get(model, model)

    # Alternate prompts for visual variety across the set
    if prompt:
        enhance_prompt = prompt
    elif index % 2 == 0:
        enhance_prompt = build_prompt(DEFAULT_ENHANCE_PROMPT, app_desc, bg_color)
    else:
        enhance_prompt = build_prompt(ALTERNATE_ENHANCE_PROMPT, app_desc, bg_color)
    image_b64 = image_to_base64(image_path)

    # Detect platform for final dimension enforcement
    if not platform:
        platform = detect_platform(image_path)

    url = f"{GEMINI_API_BASE}/models/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": enhance_prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_b64,
                        }
                    },
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["image", "text"],
            "temperature": 0.4,
        },
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"  Gemini API error ({e.code}): {error_body[:200]}")
        return False
    except urllib.error.URLError as e:
        print(f"  Network error: {e.reason}")
        return False

    # Extract image from response
    candidates = result.get("candidates", [])
    if not candidates:
        print("  Error: No candidates returned from Gemini.")
        return False

    for part in candidates[0].get("content", {}).get("parts", []):
        if "inlineData" in part:
            img_data = base64.b64decode(part["inlineData"]["data"])
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(img_data)

            # Enforce exact store dimensions
            if platform and platform in PLATFORM_DIMS:
                target_w, target_h = PLATFORM_DIMS[platform]
                img = Image.open(output_path)
                if img.size != (target_w, target_h):
                    img = img.resize((target_w, target_h), Image.LANCZOS)
                    img.save(output_path, "PNG")
                    print(f"  Resized to {target_w}x{target_h}")

            print(f"  {output_path} (enhanced with {model})")
            return True

    print("  Error: No image data in Gemini response.")
    return False


def batch_enhance(input_dir, output_dir, api_key, model=DEFAULT_MODEL,
                  prompt=None, app_desc=None, bg_color=None):
    """Enhance all PNG files in a directory with alternating prompts."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    png_files = sorted(input_path.glob("*.png"))
    if not png_files:
        print(f"  No PNG files found in {input_dir}")
        return

    print(f"  Enhancing {len(png_files)} screenshots with {model}...")
    success = 0
    for i, img_file in enumerate(png_files):
        out_file = output_path / img_file.name
        if enhance_with_gemini(
            str(img_file), str(out_file), api_key, model, prompt,
            app_desc=app_desc, bg_color=bg_color, index=i
        ):
            success += 1

    print(f"  Done: {success}/{len(png_files)} enhanced successfully.")


def main():
    p = argparse.ArgumentParser(
        description="Enhance screenshots using Gemini AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Models:
  nano-banana-pro    Higher quality enhancement (recommended)
  nano-banana-2      Faster enhancement, good quality

API Key:
  Provide via --api-key, GEMINI_API_KEY env var, or .gemini_config.json

Examples:
  # Single file
  python gemini_enhance.py --input shot.png --output enhanced.png

  # Batch enhance
  python gemini_enhance.py --input-dir output/ios/ --output-dir output/ios/enhanced/

  # Save API key for future use
  python gemini_enhance.py --save-key "YOUR_API_KEY"
        """,
    )

    p.add_argument("--input", help="Input screenshot path")
    p.add_argument("--output", help="Output enhanced screenshot path")
    p.add_argument("--input-dir", help="Input directory for batch enhancement")
    p.add_argument("--output-dir", help="Output directory for batch enhancement")
    p.add_argument(
        "--model",
        required=True,
        choices=SUPPORTED_MODELS,
        help="Gemini model to use: nano-banana-pro (higher quality) or nano-banana-2 (faster)",
    )
    p.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY env var)")
    p.add_argument("--save-key", help="Save API key to .gemini_config.json")
    p.add_argument("--prompt", help="Custom enhancement prompt (overrides built-in prompts)")
    p.add_argument(
        "--app-desc",
        help="Short app description for contextual decorative elements "
             "(e.g., 'tunnel racing game', 'mood tracker')",
    )
    p.add_argument(
        "--bg-color",
        help="Background hex color for gradient guidance (e.g., '#1A73E8')",
    )
    p.add_argument(
        "--platform",
        choices=["ios", "android"],
        help="Force platform (auto-detected from dimensions if omitted)",
    )
    p.add_argument(
        "--index",
        type=int,
        default=0,
        help="Screenshot index for prompt alternation (even=default, odd=alternate)",
    )

    args = p.parse_args()

    # Save key mode
    if args.save_key:
        save_api_key(args.save_key)
        return

    # Resolve API key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No Gemini API key found.")
        print("  Provide via: --api-key, GEMINI_API_KEY env var, or --save-key")
        sys.exit(1)

    # Batch mode
    if args.input_dir:
        if not args.output_dir:
            print("Error: --output-dir required with --input-dir")
            sys.exit(1)
        batch_enhance(
            args.input_dir, args.output_dir, api_key, args.model,
            args.prompt, args.app_desc, args.bg_color,
        )
        return

    # Single file mode
    if not args.input or not args.output:
        print("Error: --input and --output required (or use --input-dir/--output-dir)")
        sys.exit(1)

    enhance_with_gemini(
        args.input, args.output, api_key, args.model, args.prompt,
        args.platform, args.app_desc, args.bg_color, args.index,
    )


if __name__ == "__main__":
    main()
