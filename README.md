# ASO Screenshot Generator

Generate high-converting App Store & Google Play screenshots with device frames, benefit-driven headlines, and multi-language support. Works as a standalone CLI tool or as a Claude Code skill with a guided 5-phase workflow.

## Features

- **Dual platform** — iOS (1320x2868) and Android (1080x1920) output in one workflow
- **6-8 screenshots** per platform with benefit-driven action headlines
- **Multi-language** — Headlines in any language (English, Turkish, Spanish, German, Japanese, etc.)
- **Manual or auto** — Provide your own screenshots or capture from simulator
- **Device frames** — Realistic iPhone 16 Pro Max and Pixel-style Android frames with Dynamic Island / punch-hole camera
- **High CTR design** — Action verbs, visual hierarchy, bold brand colours, subtle gradients
- **Smart text colour** — Automatically picks white or dark text based on background luminance
- **Gemini AI enhancement** — All screenshots are polished with `nano-banana-pro` or `nano-banana-2` models for professional-grade output
- **No paywall rule** — Enforced throughout the workflow (never includes subscription/IAP screens)

## Requirements

- Python 3.8+
- [Pillow](https://python-pillow.org/) (PIL fork)
- macOS recommended (uses SF Pro Display font; falls back to system fonts on Linux)
- [Gemini API key](https://aistudio.google.com/apikey) (required for AI enhancement)

## Installation

### 1. Clone and install dependencies

```bash
# Clone the repo
git clone https://github.com/abutun/claude-skill-aso-cosmicmeta-ss.git
cd claude-skill-aso-cosmicmeta-ss

# Install the Python dependency
pip3 install Pillow
```

### 2. Install the font

The skill uses **SF Pro Display Black** for headline text. On macOS, download and install it from [Apple's developer fonts](https://developer.apple.com/fonts/). The expected path after installation is:

```
/Library/Fonts/SF-Pro-Display-Black.otf
```

If SF Pro is not available, the script falls back to other system fonts (Helvetica on macOS, DejaVu Sans on Linux), but SF Pro Display Black is strongly recommended for the best visual results.

### 3. Generate device frames

```bash
# Only needed once (or after modifying frame constants)
python3 generate_frame.py
```

This creates two frame PNGs in `assets/`:
- `iphone_frame.png` (1054x2870 — iPhone 16 Pro Max style)
- `android_frame.png` (900x1980 — Pixel style)

### Gemini API Key (Required)

All screenshots are enhanced with Gemini AI. Set up your API key before generating:

```bash
# Option 1: Environment variable
export GEMINI_API_KEY="your-api-key-here"

# Option 2: Save to config file (persists across sessions)
python3 gemini_enhance.py --save-key "your-api-key-here"

# Option 3: Pass directly via CLI each time
python3 gemini_enhance.py --api-key "your-api-key-here" ...
```

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey).

## Usage

### Option A — Claude Code Skill (Recommended)

Add this repo as a skill in Claude Code and let the guided workflow handle everything.

**Install the skill using one of these methods:**

**Method 1 — Using `npx add-skill` CLI (easiest):**

```bash
npx skills add abutun/claude-skill-aso-cosmicmeta-ss
```

Select the installation scope when prompted:
- **Personal** (available across all projects): installs to `~/.claude/skills/`
- **Project-specific** (current repo only): installs to `.claude/skills/`

**Method 2 — Manual installation:**

```bash
# Clone the repo
git clone https://github.com/abutun/claude-skill-aso-cosmicmeta-ss.git

# For personal use (available across all projects)
cp -r claude-skill-aso-cosmicmeta-ss ~/.claude/skills/

# OR for project-specific use (current repo only)
cp -r claude-skill-aso-cosmicmeta-ss .claude/skills/
```

> **Note:** The `SKILL.md` file must be directly inside the skill folder, not nested in an extra level of directories.

**After installation:**

1. Restart your Claude Code session to ensure the new skill is detected and loaded
2. Verify by typing `/` followed by the skill name, or ask Claude to generate store screenshots

**The skill walks through 5 phases:**

| Phase | What happens |
|-------|-------------|
| **1. Configuration** | Choose platforms, screenshot count (6 or 8), language, screenshot source, brand colour, Gemini model (`nano-banana-pro` or `nano-banana-2`), and API key |
| **2. Benefit Discovery** | Analyzes your codebase (or asks you) to identify core value propositions and craft action-verb headlines |
| **3. Screenshot Pairing** | Matches your app screenshots to benefits, assesses quality, enforces the no-paywall rule |
| **4. Generation** | Runs `compose.py` for each benefit-screenshot pair, enhances with Gemini AI, verifies output quality |
| **5. Showcase** | Generates a side-by-side preview and provides upload instructions for App Store Connect and Google Play Console |

**Example interaction:**
```
You: Generate store screenshots for my app
Claude: [Starts Phase 1 — asks for platform, count, language, etc.]
You: Both platforms, 6 screenshots, Turkish
Claude: [Analyzes codebase, proposes headlines in Turkish...]
```

### Option B — Standalone CLI

Use the Python scripts directly without Claude Code.

#### compose.py — Generate a single screenshot

```bash
# iOS screenshot
python3 compose.py \
  --platform ios \
  --bg "#E31837" \
  --verb "TRACK" \
  --desc "YOUR DAILY MOOD" \
  --screenshot path/to/app_screenshot.png \
  --output output/ios/screenshot_1.png

# Android screenshot
python3 compose.py \
  --platform android \
  --bg "#1A73E8" \
  --verb "DISCOVER" \
  --desc "NEW FEATURES" \
  --screenshot path/to/app_screenshot.png \
  --output output/android/screenshot_1.png

# Disable the subtle background gradient
python3 compose.py \
  --platform ios \
  --bg "#2D2D2D" \
  --verb "CREATE" \
  --desc "BEAUTIFUL DESIGNS" \
  --screenshot shot.png \
  --output output.png \
  --no-gradient
```

**compose.py arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `--platform` | Yes | `ios` or `android` |
| `--bg` | Yes | Background hex colour (e.g., `#E31837`) |
| `--verb` | Yes | Action verb headline (e.g., `TRACK`) |
| `--desc` | Yes | Benefit descriptor (e.g., `YOUR DAILY MOOD`) |
| `--screenshot` | Yes | Path to the app screenshot PNG/JPG |
| `--output` | Yes | Output file path |
| `--no-gradient` | No | Disable the subtle background gradient overlay |

#### gemini_enhance.py — AI-powered screenshot enhancement

```bash
# Enhance a single screenshot (uses nano-banana-pro by default)
python3 gemini_enhance.py \
  --input output/ios/screenshot_1.png \
  --output output/ios/screenshot_1_enhanced.png

# Use nano-banana-2 for faster processing
python3 gemini_enhance.py \
  --input output/ios/screenshot_1.png \
  --output output/ios/screenshot_1_enhanced.png \
  --model nano-banana-2

# Batch enhance all screenshots in a directory
python3 gemini_enhance.py \
  --input-dir output/ios/ \
  --output-dir output/ios/enhanced/ \
  --model nano-banana-pro

# Use a custom enhancement prompt
python3 gemini_enhance.py \
  --input screenshot.png \
  --output enhanced.png \
  --prompt "Add warm lighting and subtle glass reflections on the device"
```

**gemini_enhance.py arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `--input` | Yes* | Input screenshot path |
| `--output` | Yes* | Output enhanced screenshot path |
| `--input-dir` | Yes* | Input directory for batch mode |
| `--output-dir` | Yes* | Output directory for batch mode |
| `--model` | Yes | `nano-banana-pro` (higher quality) or `nano-banana-2` (faster) |
| `--api-key` | No | Gemini API key (or use `GEMINI_API_KEY` env var / `.gemini_config.json`) |
| `--save-key` | No | Save API key to `.gemini_config.json` for future use |
| `--prompt` | No | Custom enhancement prompt (overrides default) |
| `--platform` | No | Force `ios` or `android` (auto-detected from dimensions) |

*Use either `--input`/`--output` for single file or `--input-dir`/`--output-dir` for batch.

**Gemini models:**

| Model | Quality | Speed | Best for |
|-------|---------|-------|----------|
| `nano-banana-pro` | Higher | Slower | Final production screenshots |
| `nano-banana-2` | Good | Faster | Rapid iteration and previews |

#### showcase.py — Generate a preview gallery

```bash
# Both platforms
python3 showcase.py \
  --ios output/ios/screenshot_1.png output/ios/screenshot_2.png output/ios/screenshot_3.png \
  --android output/android/screenshot_1.png output/android/screenshot_2.png output/android/screenshot_3.png \
  --output showcase.png

# iOS only
python3 showcase.py \
  --ios output/ios/screenshot_1.png output/ios/screenshot_2.png \
  --output showcase_ios.png
```

#### generate_frame.py — Regenerate device frames

```bash
python3 generate_frame.py
```

Overwrites `assets/iphone_frame.png` and `assets/android_frame.png`. Only needed if you modify the frame constants in the script.

## Output Structure

```
output/
  ios/
    screenshot_1.png    # 1320 x 2868 px
    screenshot_2.png
    screenshot_3.png
    ...
  android/
    screenshot_1.png    # 1080 x 1920 px
    screenshot_2.png
    screenshot_3.png
    ...
showcase.png            # Side-by-side preview of all screenshots
```

## Screenshot Dimensions

| Platform | Width | Height | Device |
|----------|-------|--------|--------|
| iOS (App Store) | 1320 | 2868 | iPhone 6.9" (16 Pro Max) |
| Android (Google Play) | 1080 | 1920 | Standard phone |

These are the exact dimensions required by App Store Connect and Google Play Console for phone screenshots.

## Uploading to Stores

### Apple App Store Connect
1. Go to **My Apps** > your app > **App Store** tab
2. Scroll to **Screenshots** section
3. Select **iPhone 6.9-inch Display**
4. Upload the iOS screenshots in order (`screenshot_1.png` through `screenshot_N.png`)

### Google Play Console
1. Go to your app > **Store presence** > **Main store listing**
2. Scroll to **Phone screenshots**
3. Upload the Android screenshots in order

## Design Principles

The generated screenshots follow proven ASO best practices for maximum CTR and conversion:

- **Benefit-first messaging** — Headlines communicate user value, not feature names
- **Action verbs** — Bold verbs (TRACK, DISCOVER, BUILD, CREATE) drive engagement
- **Visual hierarchy** — Eye flows naturally: headline > device > app content
- **Consistent branding** — Same colour, typography, and layout across the entire set
- **Real content** — Screenshots show the app in action, never empty states
- **No clutter** — One benefit per screenshot, clean backgrounds, focused messaging

## Customization

### Changing device frame appearance
Edit the constants in `generate_frame.py` (corner radius, bezel width, colours, Dynamic Island size, etc.) and regenerate:
```bash
python3 generate_frame.py
```

### Changing layout and typography
Edit the `PLATFORMS` dict in `compose.py` to adjust:
- `device_y` — Vertical position of the device on canvas
- `text_top` — Where headline text starts
- `verb_size_max` / `verb_size_min` — Font size range for action verbs
- `desc_size` — Font size for descriptors

### Using custom fonts
Update the `FONT_CANDIDATES_BOLD` and `FONT_CANDIDATES_REGULAR` lists in `compose.py` to point to your preferred fonts.

## License

MIT
