---
name: iva-instagram-skill
description: "Instagram growth, Reel scriptwriting, viral hook scoring, caption linting, carousel design, humanization, and community automation suite for IVA."
author: "Jakeschincariol / Integrated by IVA"
version: "1.0.0"
category: "Media Studio & Social Growth"
---

# IVA Instagram Agent Skill Suite

Autonomous Instagram strategy, Reel scriptwriting, viral hook scoring, caption linting, and engagement automation engine for IVA Category 3 (IVA Marketing Studio).

## Capabilities & Commands

| Tool / Skill | Subdirectory | Purpose |
| :--- | :--- | :--- |
| `/ig-reel` | `skills/ig-reel/` | Reel hook generation from 26 formulas, local hook scoring out of 100 (`hookscore.py`), and timed beat sheets (`beats.py`). |
| `/ig-viral` | `skills/ig-viral/` | Niche swipe file analysis, outlier ranking, and hook formula attribution (`swipe.py`). |
| `/ig-caption` | `skills/ig-caption/` | Caption writing with 125-char preview linter, hashtag optimization (<=5 policy), and CTA checks (`caption.py`). |
| `/ig-carousel` | `skills/ig-carousel/` | High-swipe 1080x1350 carousel planning, slide copy, and cover design (`carousel.py`). |
| `/ig-human` | `skills/ig-human/` | Zero-watermark AI slop stripper, unicode sanitizer, and human tone scorer (`humanize.py`, `detect.py`, `slop.json`). |
| `/ig-story` | `skills/ig-story/` | Daily story sequence architecture, sticker funnel strategy, and DM engagement hooks. |
| `/ig-repurpose`| `skills/ig-repurpose/`| Cross-platform transformation: turns YouTube Shorts scripts and research topics into stand-alone Instagram Reels & Carousels. |
| `/ig-profile` | `skills/ig-profile/` | 12-point rubric audit of profile bio, link, and aesthetic grid score out of 100 (`rubric.json`). |
| `/ig-plan` | `skills/ig-plan/` | 7-day multi-format content calendar and targeted outbound engagement account lists. |
| `/ig-comment` | `skills/ig-comment/` | 9-type contextual comment generator for strategic niche post visibility. |
| `/ig-reply` | `skills/ig-reply/` | Inbound comment triage: keyword, lead, question, support, and substance routing. |
| `/ig-dm` | `skills/ig-dm/` | Inbound DM lead qualification, asset delivery, and collaboration outreach. |
| `/ig-audit` | `skills/ig-audit/` | Post-mortem performance audit ranking by outlier multiple and sends-per-reach. |

## Local CLI Tools (Pure Python Standard Library)

1. **Hook Scorer**:
   ```bash
   python skills/iva-instagram-skill/skills/ig-reel/hookscore.py --hook "Your hook text here"
   ```
2. **Beat Sheet Generator**:
   ```bash
   python skills/iva-instagram-skill/skills/ig-reel/beats.py script.txt --target 30
   ```
3. **Caption Linter**:
   ```bash
   python skills/iva-instagram-skill/skills/ig-caption/caption.py caption.txt
   ```
4. **Humanizer & AI Slop Stripper**:
   ```bash
   python skills/iva-instagram-skill/skills/ig-human/humanize.py draft.txt --report
   ```
5. **Swipe Analyzer**:
   ```bash
   python skills/iva-instagram-skill/skills/ig-viral/swipe.py data.json
   ```

## Integration with Category 3 (IVA Marketing Studio)

When IVA runs in **Category 3 (IVA Marketing Studio)**:
- Every YouTube Short produced by `iva-video-skill` (e.g. Dark Matters) is automatically cross-repurposed using `iva_instagram_bridge.py`.
- Generates 3 hook options scored >80, a 125-char mobile feed caption with 3-5 targeted niche hashtags, and a 4-slide carousel script.
