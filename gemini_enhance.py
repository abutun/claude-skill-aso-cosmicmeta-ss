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
  # Enhance a single screenshot
  python gemini_enhance.py \
    --input output/ios/screenshot_1.png \
    --output output/ios/screenshot_1_enhanced.png \
    --model nano-banana-pro \
    --api-key "YOUR_GEMINI_API_KEY"

  # Use environment variable for API key
  export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
  python gemini_enhance.py \
    --input output/ios/screenshot_1.png \
    --output output/ios/screenshot_1_enhanced.png

  # Batch enhance all screenshots in a directory
  python gemini_enhance.py \
    --input-dir output/ios/ \
    --output-dir output/ios/enhanced/ \
    --model nano-banana-2

  # Enhance with custom prompt
  python gemini_enhance.py \
    --input screenshot.png \
    --output enhanced.png \
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
SUPPORTED_MODELS = ["nano-banana-pro", "nano-banana-2"]

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

DEFAULT_ENHANCE_PROMPT = (
    "Enhance this app store screenshot to look more professional and polished. "
    "Add subtle lighting effects, smooth gradients, and a premium feel. "
    "Keep the text, device frame, and app content exactly as they are. "
    "Only enhance the background and overall visual quality. "
    "Maintain the exact same dimensions and layout."
)

# ─── Store dimensions for final crop ────────────────────────────────

PLATFORM_DIMS = {
    "ios": (1290, 2796),
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
    if w == 1290 and h == 2796:
        return "ios"
    elif w == 1080 and h == 1920:
        return "android"
    return None


def enhance_with_gemini(image_path, output_path, api_key, model=DEFAULT_MODEL,
                        prompt=None, platform=None):
    """Send image to Gemini for enhancement and save the result."""
    if model not in SUPPORTED_MODELS:
        print(f"  Error: Unknown model '{model}'. Supported: {', '.join(SUPPORTED_MODELS)}")
        return False

    enhance_prompt = prompt or DEFAULT_ENHANCE_PROMPT
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
                  prompt=None):
    """Enhance all PNG files in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    png_files = sorted(input_path.glob("*.png"))
    if not png_files:
        print(f"  No PNG files found in {input_dir}")
        return

    print(f"  Enhancing {len(png_files)} screenshots with {model}...")
    success = 0
    for img_file in png_files:
        out_file = output_path / img_file.name
        if enhance_with_gemini(str(img_file), str(out_file), api_key, model, prompt):
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
        default=DEFAULT_MODEL,
        choices=SUPPORTED_MODELS,
        help=f"Gemini model to use (default: {DEFAULT_MODEL})",
    )
    p.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY env var)")
    p.add_argument("--save-key", help="Save API key to .gemini_config.json")
    p.add_argument("--prompt", help="Custom enhancement prompt")
    p.add_argument(
        "--platform",
        choices=["ios", "android"],
        help="Force platform (auto-detected from dimensions if omitted)",
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
        batch_enhance(args.input_dir, args.output_dir, api_key, args.model, args.prompt)
        return

    # Single file mode
    if not args.input or not args.output:
        print("Error: --input and --output required (or use --input-dir/--output-dir)")
        sys.exit(1)

    enhance_with_gemini(
        args.input, args.output, api_key, args.model, args.prompt, args.platform
    )


if __name__ == "__main__":
    main()
