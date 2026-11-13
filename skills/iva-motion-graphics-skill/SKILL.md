---
name: iva-motion-graphics-skill
description: Universal Multi-Model Advanced Motion Graphics Engine for IVA. Generates high-retention vertical (9:16) and horizontal (16:9) motion graphics, kinetic typography, app launch promos, and spec ads using 4 signature styles (Kinetic Type, Liquid Glass, Editorial Grain, Pop Bold), 10 classic moves, 9 code-made SFX, and 7 pro visual fixes for ANY LLM (Gemini, Claude, GPT, OpenRouter, or Autonomous Procedural).
---

# IVA Multi-Model Advanced Motion Graphics Skill

Integrates the Motion Graphics Starter Kit and Claude Code PDF techniques natively into IVA for **every model** (Gemini 3.8/2.5, Claude 3.7/Sonnet, GPT-4o/o3, OpenRouter, and offline autonomous procedural).

## Core Architecture & Invariants

1. **Category Mapping in IVA**:
   - **Video Creation (IVA Studios)**:
     - `Normal`: Standard Lemo-Opuscar procedural scenes and real media montage.
     - `Advanced`: Advanced Motion Graphics Engine (4 styles, 10 moves, multi-model, SFX).
   - **Marketing (IVA Marketing Studio)**:
     - `Normal`: Multi-platform campaign pack (YT, IG, LinkedIn, Reddit, inbox).
     - `Advanced`: Advanced Motion Graphics SaaS/App launch promo video with screenshot zoom-ins, kinetic text, and synced SFX.
   - **Simultaneous Availability**: Both Normal and Advanced modes can be used independently or combined in one command.

2. **The 4 Signature Visual Styles**:
   - **Kinetic Type** (`kinetic_type`):
     - Text is the entire video. Pure black `#000000` background, Archivo Black font, `#c6ff3d` lime accent on the most important word per screen.
     - Fast snappy motion (`power4.out`, 0.25 to 0.4s). Words slam in, stretch, and cut on the beat.
   - **Liquid Glass** (`liquid_glass`):
     - Frosted glass cards (80% opacity, 30px blur / SVG displacement refraction, thin white border, 32px rounded corners, soft drop shadow).
     - Soft light pastel drifting blobs (pale blue, lilac, peach).
     - Inter font (Inter-700 headings, Inter-400 text), dark grey text `#1d1d1f`, `#34c759` green accent.
     - Calm smooth motion (`power3.out`, 0.6s, scale 0.96 -> 1.0).
   - **Editorial Grain** (`editorial_grain`):
     - Printed magazine page feel. Warm paper `#efe8dc`, animated SVG noise/film grain at 12% opacity.
     - Instrument Serif font (InstrumentSerif-400 and italic), Inter-400 small uppercase letterspaced labels.
     - Ink black `#1a1a1a`, deep red accent `#c2412d`. Slightly rotated paper cutout tags (1-3 deg).
     - Unhurried staggered motion (`power2.inOut`), gentle wipes, no bounces.
   - **Pop Bold** (`pop_bold`):
     - Flat neon blocks (`#c6ff3d` lime, `#8a3cff` purple, `#ff4fd8` pink, `#111111`).
     - Bricolage Grotesque ExtraBold font, 4px black outlines, 8px hard offset shadows (no blur).
     - Spinning star and circle stickers, pop arrows, `back.out(2.5)` springy overshoot bounce.

3. **10 Canonical Moves**:
   1. `Rise`: Card fades in while moving up 40px.
   2. `Pop`: Card scales from 0.6 to 1.0 with overshoot.
   3. `Count-up`: Number smoothly rolls to target value.
   4. `Checklist Tick`: Items get green checks one by one.
   5. `Typewriter`: Sentence types letter by letter.
   6. `Slide-in`: Card slides in fast from edge.
   7. `Blur-in`: Elements transition from 20px blur to crisp.
   8. `Punch-in`: Frame zooms in 15% fast on key stat/word.
   9. `Reframe`: Full screen shrinks to card, new card appears.
   10. `Bar Fill`: Progress bar fills 0 to 100%.

4. **9 Code-Made SFX**:
   - `pop.wav`, `tick.wav`, `counter.wav`, `chime.wav`, `snap.wav`, `star.wav`, `switch.wav`, `fill.wav`, `success.wav`.
   - Synced to keyframe triggers; mastered at -14 LUFS, ducked 18-20 dB under voiceover.

5. **7 Pro Fixes from Production**:
   - **SVG Displacement Filter**: True liquid glass distortion without background-blur artifacts.
   - **3D Talking Head Depth**: Three card planes (far behind, beside, close to lens) with 3D tilt.
   - **Physical Weight**: Motion reacts with overshoot and settle, no straight robot slides.
   - **Personality Numbers**: Animated badges with soft reactions when values roll.
   - **Screenshot Kinetic Zoom**: Smooth pan & zoom into key UI cards without redrawing.
   - **Instagram Reels Safe Area**: 1080x1920 with safe margins (top 10%, bottom 20%, right 15% clear).
   - **Transparent MOV/PNG Export**: ProRes 4444 with alpha channel for NLE timeline overlays.

## CLI Usage

```powershell
# Video Creation (Advanced Mode)
iva studios video --mode advanced --title "Viewers Retention" --style kinetic_type --duration 12.0

# Marketing Studio (Advanced Mode)
iva studios marketing --mode advanced --app-name "Tally" --url "https://tally.shop" --how-to-use "Connect Shopify in 1 click" --value-prop "See true profit after fees and ads"

# Direct Multi-Model Motion Graphics Command
iva studios motion-graphics --product "IVA Autonomous Partner" --style liquid_glass --duration 10.0 --cta "Visit github.com/Abhishek200416/IVA"

# Interactive Studio Wizard
iva studios menu
```
