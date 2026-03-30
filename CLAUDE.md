# ASO Screenshot Generator — CosmicMeta

This skill generates high-converting App Store and Google Play screenshots with device frames, benefit-driven headlines, and multi-language support.

## Architecture

- `SKILL.md` — Main workflow definition (5 phases)
- `compose.py` — Screenshot compositor (supports iOS 1320x2868 and Android 1080x1920)
- `generate_frame.py` — Device frame generator (iPhone + Android/Pixel)
- `gemini_enhance.py` — AI enhancement via Gemini (nano-banana-pro / nano-banana-2)
- `showcase.py` — Preview gallery generator (side-by-side comparison)
- `assets/` — Generated device frame PNGs

## Key Rules

- **Never include paywall or IAP screenshots** in the generated set
- Always generate frames before composing (`python generate_frame.py`)
- Maintain exact platform dimensions — iOS: 1320x2868, Android: 1080x1920
- Text adapts to background luminance (white on dark, dark on light)
- Support any language for headline text (verb + descriptor)

## Dependencies

- Python 3
- Pillow (`pip install Pillow`)
- Font: SF Pro Display (macOS) — falls back to system fonts on other platforms
- Gemini API key (required, for AI enhancement with nano-banana-pro or nano-banana-2)
