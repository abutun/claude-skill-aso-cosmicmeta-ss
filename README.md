# ASO Screenshot Generator

Generate high-converting App Store & Google Play screenshots with device frames, benefit-driven headlines, and multi-language support.

## Features

- **Dual platform**: iOS (1290x2796) and Android (1080x1920) in one workflow
- **6-8 screenshots** per platform with benefit-driven headlines
- **Multi-language**: Headlines in any language (default English)
- **Manual or auto**: Provide your own screenshots or capture from simulator
- **Device frames**: Realistic iPhone 15 Pro and Pixel-style frames
- **High CTR design**: Action verbs, visual hierarchy, brand colours

## Quick Start

```bash
# Install dependency
pip install Pillow

# Generate device frames
python generate_frame.py

# Compose a single screenshot
python compose.py \
  --platform ios \
  --bg "#E31837" \
  --verb "TRACK" \
  --desc "YOUR DAILY MOOD" \
  --screenshot input.png \
  --output output.png
```

## As a Claude Code Skill

Add this repo as a skill in Claude Code. The skill walks through a 5-phase workflow:

1. **Configuration** — Platform, count, language, screenshot source
2. **Benefit Discovery** — Identify app value propositions
3. **Screenshot Pairing** — Match screenshots to benefits
4. **Generation** — Compose final images with frames and headlines
5. **Showcase** — Preview and delivery instructions

## License

MIT
