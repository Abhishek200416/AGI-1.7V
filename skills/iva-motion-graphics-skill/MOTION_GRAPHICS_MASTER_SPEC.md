# IVA Multi-Model Advanced Motion Graphics Engine — Master Specification
**Universal Code-Driven Motion Design, Kinetic Typography, App Launch Promos & Spec Ads**  
*Extracted and synthesized from the Motion Graphics Starter Kit & Claude Code Guide by Damiano Caudullo for ALL LLMs in IVA.*

---

## 1. Executive Summary & Multi-Model Invariant
While the original reference guide was tailored specifically for Claude Code using HyperFrames, **IVA decouples this entire motion pipeline from any single LLM or proprietary toolchain**.

IVA's motion graphics engine operates identically across:
- **Google Gemini** (Gemini 3.8 Flash, 3.8 Pro, 2.5 Pro)
- **Anthropic Claude** (Claude 3.7 Sonnet, Claude 3.5 Sonnet)
- **OpenAI** (GPT-4o, o3-mini, o1)
- **OpenRouter Free & Open-Weight Models** (DeepSeek V3/R1, Qwen 2.5, Llama 3.3)
- **IVA Autonomous Procedural Engine** (100% offline, deterministic code generator with zero API tokens required)

Rendering is handled natively via **Playwright + Chromium hardware rasterization + FFmpeg**, rendering vertical 9:16 (1080x1920) and horizontal 16:9 (1920x1080) videos in **under 12 seconds**.

---

## 2. Dual-Mode Category Architecture in IVA

### A. Video Creation (IVA Studios)
- **[1] Normal**: Standard IVA Studios / `lemo-opuscar` procedural Canvas/Three.js scene directing with narration, real web visual fetching, and standard montage.
- **[2] Advanced**: Advanced Motion Graphics Starter Kit pipeline (choice of 4 signature styles, 10 moves, multi-model generation, and SFX integration).

### B. Marketing Studio (IVA Marketing Studio)
- **[1] Normal**: Multi-platform text, card image, and caption campaign pack (YouTube, Instagram, LinkedIn, Reddit, inbox reply queue).
- **[2] Advanced**: Advanced Motion Graphics SaaS/App launch promo video (using real app screenshots, product launch structure [0-2s reveal, 2-9s features, 9-12s CTA], kinetic typography, and synced SFX).
- **Simultaneous Execution**: Both Normal and Advanced modes can be used independently or run concurrently in a single command.

---

## 3. The 4 Signature Visual Styles

### Style 1: Kinetic Type (`kinetic_type`)
- **Aesthetic**: Huge, all-caps words slamming in on the beat. High contrast, maximum scroll-stopping energy.
- **Typography**: Archivo Black (`ArchivoBlack-400.woff2`), all caps, headline fills 85-90% of screen width.
- **Color Palette**: Pure black background (`#000000`), crisp white text (`#ffffff`), accent color `#c6ff3d` (lime neon) for the single most important word on each screen.
- **Motion Physics**: Words slam in fast and snappy (`power4.out`, 0.25 to 0.4s). Motion moves include side slides, squash-to-full-height stretches, and letter splits. Screen exits quickly before the next beat hits.
- **Best For**: Viral hooks, short punchy scripts, bold announcements.

### Style 2: Liquid Glass (`liquid_glass`)
- **Aesthetic**: The Apple look. Frosted glass cards, soft drifting pastel blobs, calm, sophisticated motion.
- **Typography**: Inter (`Inter-700.woff2` for headings, `Inter-400.woff2` for body and labels). Dark grey text `#1d1d1f` or pure white `#ffffff` on dark mode, uppercase grey tags above headings.
- **Surface**: Frosted glass cards at 80% opacity, 30px background blur (or SVG displacement filter for refraction), thin white border (`1px solid rgba(255,255,255,0.2)`), 32-36px corner radius, soft ambient shadow.
- **Background**: Soft gradient with 2-3 blurred drifting pastel color blobs (pale blue `#8ec5fc`, lilac `#e0c3fc`, peach `#fbc2eb`).
- **Accent**: Green `#34c759` for checkmarks, pills, and metrics.
- **Motion Physics**: Calm and smooth. Cards rise 30-40px and fade in (`power3.out`, 0.6s), scaling up from 0.96. Text arrives piece-by-piece. No bouncy overshoot.
- **Best For**: Product features, UI card showcases, premium SaaS.

### Style 3: Editorial Grain (`editorial_grain`)
- **Aesthetic**: Printed magazine editorial page. Handmade paper texture, animated film noise, serif typography.
- **Typography**: Instrument Serif (`InstrumentSerif-400.woff2` and `InstrumentSerif-400-italic.woff2`) for large headlines, mixing upright and italic emphasis words. Small uppercase letterspaced labels in Inter (`Inter-400.woff2`).
- **Color Palette**: Warm paper `#efe8dc`, ink black `#1a1a1a`, deep red accent `#c2412d`.
- **Texture**: Visible animated film grain overlay (SVG fractal noise filter at 12% opacity).
- **Shapes**: Cut-out paper rectangles behind key words slightly rotated (1° to 3°), thin hairline rules, corner issue/page numbering (`VOL. 26 // ISSUE 01`).
- **Motion Physics**: Unhurried and organic. Staggered timings, gentle slides and wipes, no artificial bounces.
- **Best For**: Stories, thought leadership, documentaries, opinion essays.

### Style 4: Pop Bold (`pop_bold`)
- **Aesthetic**: Loud on purpose. Flat neon blocks, chunky typography, hard black outlines, sticker badges, springy physics.
- **Typography**: Bricolage Grotesque ExtraBold (`BricolageGrotesque-800.woff2`), big and chunky.
- **Color Palette**: Flat solid blocks of lime `#c6ff3d`, purple `#8a3cff`, pink `#ff4fd8`, and black `#111111`.
- **Borders & Shadows**: 4px solid black outlines, 8px hard offset drop shadows with zero blur (`box-shadow: 8px 8px 0px #111111`).
- **Decorations**: Rotating star and circle sticker badges (`★`, `●`), pop arrows, CSS geometric accents.
- **Motion Physics**: Bouncy and springy (`back.out(2.5)`), overshoot, subtle wobble, squash and stretch. Stickers continuously rotate slowly.
- **Best For**: High-energy Reels, youth culture, viral SaaS promos, attention hooks.

---

## 4. The 10 Canonical Moves

1. **Rise**: Card fades in while moving upward 30-40px.
2. **Pop**: Card scales up from 0.6 to 1.0 with subtle overshoot.
3. **Count-up**: A number rolls smoothly from 0 to target value (e.g., 0 to 100, 40 to 90+).
4. **Checklist Tick**: List items receive animated green checkmarks sequentially.
5. **Typewriter**: Text types itself character-by-character.
6. **Slide-in**: Element enters with high velocity from the screen edge.
7. **Blur-in**: Transition from blurry (20px Gaussian blur) to needle-sharp clarity.
8. **Punch-in**: Entire camera frame zooms in 15% fast to emphasize a key punchline.
9. **Reframe**: Full-screen video shrinks into a card while new interface elements appear.
10. **Bar Fill**: Progress bar fills smoothly from 0% to 100%.

---

## 5. Sound Engine & Acoustic Mastering
- **9 Code-Made SFX**:
  - `pop.wav`: Card pop-in and element reveals.
  - `tick.wav`: Sequential checklist checkmarks and list items.
  - `counter.wav`: Number rolling and data incrementing.
  - `chime.wav`: Final card completion and success moment.
  - `snap.wav`: Snappy transitions and layout snaps.
  - `star.wav`: Sticker pop and badge appearance.
  - `switch.wav`: Mode toggle or dark-mode flip.
  - `fill.wav`: Progress bar and meter filling.
  - `success.wav`: Call to action and final confirmation.
- **Mastering Invariants**:
  - Sound effects sit 18-20 dB under spoken voiceover.
  - Mastered at **-14 LUFS**, True Peak under **-1.0 dBFS**.
  - No sound on card exits, no artificial whooshes.

---

## 6. The 7 Production Fixes (From PDF Guide)

1. **Clear Liquid Glass (Fix 01)**: Use an SVG displacement filter (`feTurbulence` into `feDisplacementMap`) as `backdrop-filter` with `saturate(180%)`, a 5% white tint, and a 1px top highlight. Whatever is underneath bends realistically at card edges.
2. **3D Talking Head Depth (Fix 02)**: Cut out speaker with clean matte; place UI cards across 3 depth planes: far behind (small, blurred), beside speaker (sharp), close to lens (large, blurred).
3. **Blender MCP 3D Integration (Fix 03)**: Real 3D models with matte materials, key light, rim light, and real contact shadows. Clay preview first, render after approval.
4. **Anti-Template Organic Physics (Fix 04)**: Real physical weight with overshoot and settle. Never identical copies or sterile linear moves.
5. **Personality Numbers (Fix 05)**: Turn key statistics into soft 3D objects with reactions (coin drop, subtle bounce, character expressions).
6. **Realistic UI Camera Movement (Fix 06)**: Rebuild real application interfaces directly from screenshots; move camera close following cursor and numbers instead of displaying flat static images.
7. **Instagram Reels Safe Area (Fix 07)**: Keep all critical visuals and typography inside the safe zone: clear top 10%, bottom 20% (for captions/username), and right 15% (for Like, Comment, and Share buttons).

---

## 7. Export Configurations & Codecs

- **Standard Vertical Short**: `1080x1920` @ 30 fps (H.264/AAC MP4).
- **High-Motion 60 FPS**: `1080x1920` @ 60 fps.
- **Ultra-HD 4K**: `3840x2160` (or `2160x3840`) @ 60 fps.
- **Transparent Alpha Overlay**: Apple ProRes 4444 MOV with alpha channel (`--format mov`) or PNG frame sequence for direct import into Premiere Pro, DaVinci Resolve, or Final Cut.
- **File Size Optimization**: `--crf 23` for web delivery.
