---
name: aso-cosmicmeta-ss
description: Generate high-converting App Store & Google Play screenshots for iOS and Android with device frames, benefit-driven headlines, and multi-language support
trigger: When users want to create app store screenshots, app listing visuals, or ASO screenshot assets for Apple App Store and/or Google Play Store
---

# ASO Screenshot Generator — iOS & Android

Generate 6-8 polished, high-converting App Store and Google Play screenshots with device frames, benefit-driven headlines, and multi-language support. Produces pixel-perfect images for both platforms simultaneously.

**Output dimensions:**
- iOS (Apple App Store): 1290 × 2796 px (iPhone 6.7")
- Android (Google Play): 1080 × 1920 px (standard phone)

---

## Phase 1 — Configuration & Recall

### Check for saved progress
Before starting, check Claude Code memory for any saved progress on this project:
- Look for memory entries related to "aso-screenshots", "store-screenshots", or the project name
- If found, present status of completed phases and ask whether to resume or start fresh

### Gather inputs from user

Ask the user for the following configuration. Present as a clean checklist:

1. **Target platforms** — Which platforms? (default: both iOS and Android)
   - iOS (Apple App Store)
   - Android (Google Play Store)
   - Both

2. **Number of screenshots** — How many per platform? (default: 6)
   - 6 screenshots (recommended minimum)
   - 8 screenshots (maximum coverage)

3. **Language** — What language for headline text? (default: English)
   - Let user specify any language (English, Turkish, Spanish, German, Japanese, etc.)
   - This affects the verb + descriptor text on each screenshot

4. **Screenshot source** — Where are the app screenshots coming from?
   - **Auto-capture**: I'll guide you through taking simulator screenshots
   - **Manual input**: User provides screenshot image files directly (PNG/JPG paths)

5. **Brand colour** — Background hex colour (e.g., #E31837)
   - If not provided, attempt to auto-detect from codebase (look for theme colors, brand constants, primary colors in the project)
   - If no codebase available, ask the user

6. **Gemini AI Enhancement** (Optional) — Use Gemini to polish screenshots with AI
   - **Enable/disable**: Whether to use Gemini AI for enhancement (default: disabled)
   - **Model**: Which Gemini model to use
     - `nano-banana-pro` — Higher quality, slower (recommended)
     - `nano-banana-2` — Faster, good quality
   - **API key**: Gemini API key for authentication
     - Can be provided directly, via `GEMINI_API_KEY` environment variable, or saved to `.gemini_config.json`
     - To save the key for future use: `python3 gemini_enhance.py --save-key "YOUR_KEY"`

Save all configuration to memory:
```
memory_key: aso-screenshots-config
data: { platforms, count, language, source_mode, brand_colour, project_name, gemini_enabled, gemini_model, gemini_api_key_configured }
```

---

## Phase 2 — Benefit Discovery

Identify the app's core value propositions that will become screenshot headlines.

### If codebase is available:
1. Analyze the app's codebase to identify **6-8 core benefits** (matching requested screenshot count)
2. Focus on features that are visually demonstrable in screenshots
3. **IMPORTANT**: Skip any paywall, subscription, or in-app purchase screens — these must NOT appear in store screenshots

### If no codebase (manual mode):
1. Ask the user to describe their app's key features and benefits
2. Collaboratively refine the list

### Headline format
Each benefit needs two parts:
- **Verb** — A bold action word (1-2 words max). Examples: TRACK, DISCOVER, ORGANIZE, CONNECT, CREATE, MONITOR, PLAN, SHARE
- **Descriptor** — What the user achieves (2-5 words). Examples: YOUR DAILY MOOD, NEW CONNECTIONS, WEEKLY GOALS

**Language adaptation**: If the configured language is not English, translate both verb and descriptor naturally. Don't do literal translations — use idiomatic expressions that sound compelling in the target language.

### Present to user
Show the complete benefit list as a numbered table:

| # | Verb | Descriptor | Combined Headline |
|---|------|------------|-------------------|
| 1 | TRACK | YOUR DAILY MOOD | TRACK YOUR DAILY MOOD |
| 2 | ... | ... | ... |

Ask user to approve, modify, or reorder. Iterate until approved.

Save to memory:
```
memory_key: aso-screenshots-benefits
data: { benefits: [{ verb, descriptor, order }], language }
```

---

## Phase 3 — Screenshot Pairing

### If Auto-capture mode:
1. Guide user through taking simulator screenshots for each benefit
2. For each screenshot provided, assess quality honestly:
   - **Great** — Perfect, ready to use
   - **Usable** — Minor issues but workable
   - **Retake** — Recommend retaking (explain why)
3. Match screenshots to benefits based on relevance and visual impact

### If Manual input mode:
1. Ask user to provide paths to their screenshot files
2. Accept any of: absolute paths, relative paths, glob patterns
3. Display thumbnails/filenames and let user assign each to a benefit
4. If fewer screenshots than benefits, ask user to provide more or reduce benefit count

### Screenshot rules
- **NO paywall screenshots** — Skip any screen showing subscription plans, pricing, or IAP items
- **NO purchase confirmation screens** — Skip any checkout or payment success screens
- Prefer screens that show the app's core functionality in action
- Prefer screens with visible content/data rather than empty states

### Quality check
For each screenshot, verify:
- Resolution is sufficient (warn if below 1170px wide for iOS or 1080px for Android)
- Content is appropriate (no placeholder/debug data)
- Screen shows a compelling state of the feature

Save pairings to memory:
```
memory_key: aso-screenshots-pairings
data: { pairings: [{ benefit_index, screenshot_path, assessment }] }
```

---

## Phase 4 — Generation

### Prerequisites
Ensure Python dependencies are available:
```bash
pip install Pillow
```

### Generate device frames (if not already present)
```bash
python generate_frame.py
```
This creates `assets/iphone_frame.png` and `assets/android_frame.png`.

### Generate screenshots
For each benefit-screenshot pair, generate the composed image:

```bash
# iOS version
python compose.py \
  --platform ios \
  --bg "{brand_colour}" \
  --verb "{verb}" \
  --desc "{descriptor}" \
  --screenshot "{screenshot_path}" \
  --output "output/ios/screenshot_{n}.png"

# Android version
python compose.py \
  --platform android \
  --bg "{brand_colour}" \
  --verb "{verb}" \
  --desc "{descriptor}" \
  --screenshot "{screenshot_path}" \
  --output "output/android/screenshot_{n}.png"
```

### Output directory structure
```
output/
  ios/
    screenshot_1.png  (1290x2796)
    screenshot_2.png
    ...
  android/
    screenshot_1.png  (1080x1920)
    screenshot_2.png
    ...
```

### Quality check after generation
1. Open each generated screenshot and verify:
   - Text is readable and properly centered
   - Device frame is correctly positioned
   - Screenshot content is visible and well-framed
   - No clipping of important content
2. If any screenshot has issues, regenerate with adjustments

### Consistency
- The first approved screenshot sets the visual tone for the set
- All screenshots must use the same brand colour, font sizing pattern, and layout style
- Maintain visual rhythm across the set — they should look like a cohesive collection

### AI Enhancement with Gemini (Optional)
If Gemini enhancement was enabled in Phase 1, run `gemini_enhance.py` on each generated screenshot:

```bash
# Enhance a single screenshot
python3 gemini_enhance.py \
  --input "output/ios/screenshot_{n}.png" \
  --output "output/ios/screenshot_{n}.png" \
  --model "{gemini_model}" \
  --api-key "{gemini_api_key}"

# Or batch enhance an entire directory
python3 gemini_enhance.py \
  --input-dir output/ios/ \
  --output-dir output/ios/ \
  --model "{gemini_model}"
```

**Available models:**
- `nano-banana-pro` — Higher quality enhancement (recommended for final output)
- `nano-banana-2` — Faster enhancement, good quality (recommended for iteration)

**What Gemini enhancement does:**
- Adds realistic lighting effects, smooth gradients, and a premium feel
- Enhances background quality with professional polish
- Preserves text, device frame, and app content exactly as composed
- **Always** enforces exact store-required dimensions after AI processing

**API key resolution order:**
1. `--api-key` CLI argument
2. `GEMINI_API_KEY` environment variable
3. `.gemini_config.json` file (saved via `--save-key`)

Save generation state to memory:
```
memory_key: aso-screenshots-generation
data: { generated: [{ benefit_index, platform, output_path, status }] }
```

---

## Phase 5 — Showcase & Delivery

### Generate showcase preview
```bash
python showcase.py \
  --ios output/ios/screenshot_1.png output/ios/screenshot_2.png output/ios/screenshot_3.png \
  --android output/android/screenshot_1.png output/android/screenshot_2.png output/android/screenshot_3.png \
  --output showcase.png
```

### Present results
1. Show the showcase image to the user
2. List all generated files with their dimensions
3. Provide upload instructions:

**For Apple App Store Connect:**
- Navigate to your app > App Store tab > Screenshots section
- Upload each iOS screenshot in order (screenshot_1 through screenshot_N)
- Select "iPhone 6.7-inch Display" as the device type

**For Google Play Console:**
- Navigate to your app > Store listing > Phone screenshots
- Upload each Android screenshot in order
- Ensure "Phone" device type is selected

### Final checklist
- [ ] All screenshots are the correct dimensions
- [ ] Headlines are in the correct language
- [ ] No paywall or IAP screens included
- [ ] Screenshots show compelling app states
- [ ] Visual style is consistent across all screenshots
- [ ] Both platforms have matching content (same benefits, same order)

---

## Design Guidelines

### Text Safety
- Headlines must stay within the center 70% of canvas width
- Text should never touch or overlap the device frame
- Minimum 40px gap between text bottom and device top

### Device Placement
- Device frames are positioned in the upper-middle area of the canvas
- The bottom of the device intentionally extends beyond/crops at canvas edge
- This creates a professional, dynamic composition

### Colour & Contrast
- Background colour should be bold and brand-aligned
- Text automatically adjusts to white or dark based on background luminance
- Subtle gradient overlay adds depth (can be disabled with --no-gradient)

### Typography
- Action verbs: Maximum impact, largest possible size (150-256pt for iOS, 120-200pt for Android)
- Descriptors: Supporting text, slightly smaller (124pt iOS, 96pt Android)
- All text is uppercase for maximum store shelf impact
- Font: SF Pro Display Black (macOS) with fallbacks for other systems

### What Makes High-CTR Screenshots
1. **Benefit-first messaging** — Lead with what the user gets, not feature names
2. **Action verbs** — Create urgency and engagement (TRACK, DISCOVER, BUILD)
3. **Visual hierarchy** — Eye flows: headline -> device -> app content
4. **Consistent branding** — Same colour, same style, professional set
5. **Real app content** — Show the app in action with realistic data, not empty states
6. **No clutter** — Clean backgrounds, focused messaging, one benefit per screenshot
