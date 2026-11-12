---
name: iva-video-skill
description: Autonomous code-driven animation, cinematic directing, and motion-graphics film creation system integrated into IVA. Generates short films, scientific micro-documentaries, data visualizations, and kinetic animations entirely through code (Canvas, Three.js, Python, FFmpeg) with 101 distinct visual styles, rhythm-synced camera grammar, acoustic mastering (-14 LUFS), and cinematic foley.
---

# IVA Video Skill: Autonomous Code-Driven Film & Motion Directing

IVA Video Skill is IVA's integrated autonomous directing and animation framework that creates cinematic films, animations, and micro-documentaries purely through deterministic code, eliminating reliance on unpredictable diffusion video models.

---

## 1. Core Directing Philosophy (Sound, Rhythm, Camera, Staging)

A film is judged in this strict priority:
1. **Sound**: Ambience bed, action-tied foley, music score ducked under voice, and deliberate silences before narrative turns.
2. **Rhythm**: Picture locked to an explicit musical/tempo grid; variable pacing (alternating fast and slow).
3. **Camera**: Dynamic moves with narrative purpose (push, pull, orbit, parallax, zoom) with zero static holds.
4. **Directing**: One subject, one goal, one dramatic turn, hook in the first 3 seconds, and a resonant concluding loop.

---

## 2. 101 Visual Style Engine

The style library in `styles/` contains 101 production-ready aesthetic blueprints. Popular visual styles for **IVA Studios** include:

- **`dark-documentary`**: Radar sweep, LiDAR contour lines, wireframe echoes, cold rim lights, instrument readouts, sonar pings, and bowed vibraphone.
- **`archive-lighttable`**: Historical evidence dossiers, slide-click foley, microfilm magnification, illuminated negatives, and forensic stamps.
- **`backrooms`**: Liminal geometry, analog CRT chromatic aberration, fluorescent hum, fluorescent flicker, and claustrophobic perspective.
- **`dark-keynote`**: Minimalist high-contrast typography, mathematical data callouts, dark matte textures, and crisp UI transitions.
- **`blueprint`**: Technical schematics, cyan/indigo gridlines, architectural measurements, drafting compass motion, and pencil-scritch foley.
- **`circuit-board`**: Microscopic PCB traces, pulsing electrical signals, macro solder textures, and electronic zap transitions.
- **`double-exposure`**: Silhouette blending, organic textures within human silhouettes, dreamlike overlay pacing, and deep ambient resonance.
- **`caption-news`**: Rapid-fire kinetic typography, urgent alert borders, live data feeds, and broadcast-grade lower-thirds.

---

## 3. Production Pipeline

```
BRIEF & SCRIPT → VOICEOVER (EDGE-TTS / SARVAM) → CUE MAP & BEAT GRID → SCENE STAGING → FOLEY & SOUND LAYERING → FFPEG COMPILATION & SUBTITLES (-14 LUFS)
```

1. **Script & Pacing**:
   - High-velocity delivery: `+24%` to `+26%` speed on ChristopherNeural / `1.28`–`1.32` pace on Sarvam AI.
   - 40–50 second sweet spot for vertical Shorts.
2. **1:1 Visual-Semantic Synchronization**:
   - Every spoken phrase MUST have an exact visual counterpart on screen at that precise second.
   - Zero looping of 2–3 generic clips.
   - Rapid cuts every 2.5 to 3.5 seconds (12–16 distinct scenes per 50s Short).
3. **Sound Design Layering**:
   - **Layer 1: Ambience Bed** (wind, room tone, deep ocean drone, cosmic hum).
   - **Layer 2: Action Foley** (whooshes, clicks, pings, sub-bass thuds on key words).
   - **Layer 3: Musical Score** (ducked -10 dB under voiceover).
   - **Layer 4: Voiceover** (highpass 75 Hz, loudnorm -14 LUFS).
4. **Kinetic Typography**:
   - Stylized ASS subtitles with font styling, high-contrast drop-shadows, and color-coded alert highlights (Cyan, Gold, Red).

---

## 4. Reference Library Links

- Directing Handbook: [`DIRECTOR.md`](DIRECTOR.md)
- Technical Architecture & Code Examples: [`TECHNIQUE.md`](TECHNIQUE.md)
- Full Style Blueprints: [`styles/`](styles/)
