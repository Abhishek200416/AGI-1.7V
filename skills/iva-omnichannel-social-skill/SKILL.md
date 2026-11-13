---
name: iva-omnichannel-social-skill
description: "Universal multi-platform social media adaptation engine for IVA. Adapts any video, research, or story across YouTube Shorts, Instagram, TikTok, X (Twitter), LinkedIn, Threads, and Facebook Reels."
author: "IVA Omega Command"
version: "1.0.0"
category: "Media Studio & Social Distribution"
---

# IVA Omnichannel Social Distribution Skill

Automated cross-platform content adaptation engine for IVA Category 3 (IVA Marketing Studio). Transforms a single core research topic, documentary script, or YouTube Short into tailor-made formats for all major social media networks.

## Supported Social Networks & Formats

1. **YouTube Shorts & Long-Form**:
   - High-CTR hook title (<=90 characters, `#Shorts` tagged)
   - SEO-optimized description with timestamp breakdown & channel attribution
   - Pinned community discussion prompt
   - Targeted search tags

2. **Instagram (Reels, Carousels, Stories)**:
   - **Reels**: First-line hook engineered to land within the 125-character mobile feed cutoff before `... more`, line-break structured body, and maximum 5 hyper-targeted niche tags (compliant with Instagram's 2026 tag policy).
   - **Carousels**: 4 to 8 multi-slide swipe copy (Cover Hook $\rightarrow$ The Mechanism $\rightarrow$ Raw Physics $\rightarrow$ Call-to-Action).
   - **Stories**: 3-part sequence with interactive poll questions and sticker engagement hooks.

3. **TikTok**:
   - 0–3 second pattern-interrupt spoken and visual text hooks
   - High-velocity caption (<=150 characters)
   - Trending sound/audio recommendation cues

4. **X / Twitter**:
   - **Standalone Tweet**: High-signal text hook (<280 chars) paired with video attachment.
   - **Educational Thread**: 5 to 7 modular tweets breaking down the core mechanism step-by-step with zero hashtag clutter.

5. **LinkedIn**:
   - Executive & engineering thought-leadership format
   - Clean 2-line problem/curiosity hook
   - Bulleted technical takeaways & second-order industrial implications
   - Professional discussion prompt + 3 industry hashtags

6. **Threads & Facebook Reels**:
   - Conversational, debate-driven short-form copy with viral re-share potential.

## CLI & Programmatic Usage

```python
from studio.system.iva_omnichannel_social_engine import OmnichannelSocialEngine

bundle = OmnichannelSocialEngine.adapt_for_all_platforms(
    title="Why A 67,000-Lb Steel Tanker Implodes In 0.1 Seconds",
    script_beats=[
        "This is a 67,000-pound solid steel railroad tanker.",
        "Its walls are half an inch of structural steel.",
        "Yet in under 0.1 seconds, atmospheric pressure crushes it like a soda can.",
        "When steam inside cooled, it condensed into liquid, creating a vacuum.",
        "Over two million pounds of outside air pressure hammered the hull until it folded."
    ],
    brand_name="Dark Matters",
    niche="Science & Physics"
)
```
