---
name: iva-video-skill
description: Autonomous real-world visual directing, sound architecture, and kinetic caption compositing system integrated into IVA. Combines verified real-world camera photographs and real outside video clips (`real_media_fetcher.py` + FFmpeg) with rhythm-synced camera motion, lower-third typography, acoustic mastering (-14 LUFS), and cinematic foley. Never substitutes stick-figure/geometric code cartoons for real-world subjects.
---

# IVA Video Skill: Real-World Film Directing & Motion Compositing

IVA Video Skill is IVA's integrated autonomous directing framework. For any real-world, science, nature, news, or story subject, it **MUST drive every visual beat using verified real outside-world photographs and real video footage** (`studio/system/real_media_fetcher.py` + `assemble_real_world_montage`), using FFmpeg / Canvas strictly for camera motion (pan/zoom), transitions, kinetic lower-third captions, and `-14 LUFS` foley audio mastering—**NEVER synthetic stick-figure/cartoon code drawings**. Canvas/code rendering is reserved solely for explicit software/codebase walkthroughs (`codebase_motion_generator.py`).

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
5. **Copyright Safety & Transformative Editing Law (NEVER Raw Clip Re-Uploads)**:
   - **Never grab raw clips and upload them unedited.** Every external video clip MUST be heavily edited for copyright safety and high retention:
     * **Audio Stripping**: Always drop 100% of source clip audio (`-an`) and replace it with original educational/analytical voiceover + royalty-free/CC-BY BGM (attributed in description) + foley SFX.
     * **Short Transformative Cuts**: Limit any single third-party film/news clip cut to **`1.8s–3.5s` max continuous duration** (intercut cleanly with Wikimedia/NASA/public-domain photography, Pexels/CC0 B-roll, and BTS shots).
     * **Active Visual Transformation**: Always reframe into vertical `1080x1920`, apply camera motion (`zoompan`/push/crop pan), color grading (`eq`), dynamic transitions (`xfade`/flash/whoosh), and synced lower-third kinetic captions so the output is genuinely transformative commentary/education rather than a re-uploaded clip.

---

## 4. Reference Library Links

- Directing Handbook: [`DIRECTOR.md`](DIRECTOR.md)
- Technical Architecture & Code Examples: [`TECHNIQUE.md`](TECHNIQUE.md)
- Full Style Blueprints: [`styles/`](styles/)
