#!/usr/bin/env python3
"""
IVA Studios — Social Media, Instagram & Campaign Generator
Supports generating high-retention content for:
- Instagram Reels (1080x1920)
- Instagram Feed Posts & Carousels (1080x1080 / 1080x1350)
- High-Converting Commercial / Product Advertisements
- Breaking Negative News / Urgent Bulletins
Outputs formatted captions, hashtags, and visual assets ready for distribution.
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_DIR = r"c:\Users\abhis\Downloads\ytsss\AI_MEDIA_STUDIO"
FFMPEG = r"C:\ffmpeg\ffmpeg-7.1-full_build\bin\ffmpeg.exe"
OUTPUT_DIR = os.path.join(BASE_DIR, "uploads", "instagram")

def generate_social_post(topic: str, media_format: str = "post", angle: str = "Investigation", brand_name: str = "IVA Studios"):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_slug = "".join(c if c.isalnum() else "_" for c in topic.lower()[:30]).strip("_")
    
    # 1. Generate High-Converting Instagram Caption
    caption = f"""🚨 {topic.upper()}
━━━━━━━━━━━━━━━━━━━━
They didn't want this getting out. 

Look closer at what just happened. While the public was distracted by standard headlines, key data quietly slipped through the cracks. 

What this actually means:
1️⃣ The baseline model just fundamentally shifted.
2️⃣ Mainstream outlets are under-reporting the second-order consequences.
3️⃣ If you don't adjust your position right now, the gap is going to widen.

💬 What's your take on this? Is this being suppressed or ignored? Drop your perspective in the comments below.

Follow @{brand_name.lower().replace(' ', '_')} for unfiltered daily investigative breakdowns and deep analysis.
━━━━━━━━━━━━━━━━━━━━
#investigation #breakingnews #techupdates #marketshift #criticalalert #intel #deepdive #truth #{clean_slug}"""

    caption_path = os.path.join(OUTPUT_DIR, f"{clean_slug}_{timestamp}_caption.txt")
    with open(caption_path, "w", encoding="utf-8") as f:
        f.write(caption)

    # 2. Generate Graphic Visual Card (1080x1080 or 1080x1920)
    dimensions = "1080x1920" if media_format.lower() in ["reel", "story", "short"] else "1080x1080"
    out_img = os.path.join(OUTPUT_DIR, f"{clean_slug}_{timestamp}_card.png")
    
    font_path = "C\\:/Windows/Fonts/impact.ttf"
    safe_topic = topic.replace("'", "").replace(":", " -").replace('"', '').replace("[", "").replace("]", "")
    safe_brand = brand_name.replace("'", "").replace("[", "").replace("]", "")
    
    t_line1 = safe_topic[:38]
    t_line2 = safe_topic[38:76]
    
    vf = (
        f"drawbox=x=40:y=40:w=iw-80:h=ih-80:color=0x4f46e5@0.6:t=6,"
        f"drawtext=fontfile='{font_path}':text='CRITICAL INTEL':fontcolor=0xef4444:fontsize=50:x=(w-text_w)/2:y=130,"
        f"drawtext=fontfile='{font_path}':text='{safe_brand.upper()}':fontcolor=0x94a3b8:fontsize=32:x=(w-text_w)/2:y=200,"
        f"drawtext=fontfile='{font_path}':text='{t_line1}':fontcolor=0xffffff:fontsize=52:x=(w-text_w)/2:y=460,"
        f"drawtext=fontfile='{font_path}':text='{t_line2}':fontcolor=0xffffff:fontsize=52:x=(w-text_w)/2:y=530,"
        f"drawtext=fontfile='{font_path}':text='SWIPE / READ CAPTION FOR FULL INTEL':fontcolor=0xfbbf24:fontsize=32:x=(w-text_w)/2:y=h-140"
    )

    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi", "-i", f"color=c=0x0a0c10:s={dimensions}:d=1",
        "-vf", vf,
        "-frames:v", "1",
        "-update", "1",
        out_img
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        img_success = True
    except Exception as e:
        print(f"[WARN] Card generation warning: {e}")
        img_success = False

    result = {
        "success": True,
        "format": media_format,
        "topic": topic,
        "caption_file": caption_path,
        "card_image": out_img if img_success else None,
        "caption_preview": caption[:200] + "..."
    }
    
    return result


def generate_marketing_pack(
    app_name: str,
    app_url: str,
    how_to_use: str,
    value_prop: str,
    brand_name: str = "IVA Marketing Studio",
    song_track: str = "investigative_electronic_pulse.mp3",
    include_voiceover: bool = True,
) -> dict:
    """
    IVA Marketing Studio — Cross-Platform Product Growth Pack:
    Generates coordinated YouTube, Instagram (with song + optional voiceover),
    LinkedIn, and Reddit campaign drafts explaining where users can find the
    application and step-by-step how to use it.
    """
    pack_dir = os.path.join(BASE_DIR, "uploads", "marketing_packs")
    os.makedirs(pack_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = "".join(c if c.isalnum() else "_" for c in app_name.lower()[:28]).strip("_")
    music_path = os.path.join(BASE_DIR, "music", "compositions", song_track)

    ig_card = generate_social_post(
        topic=f"{app_name}: {value_prop}",
        media_format="reel",
        angle="Product Launch",
        brand_name=brand_name,
    )

    linkedin_post = (
        f"Introducing {app_name} — {value_prop}\n\n"
        f"Where to find it:\n{app_url}\n\n"
        f"How to get started in 60 seconds:\n{how_to_use}\n\n"
        f"Built & promoted with {brand_name}. Try it today and drop questions in the comments — our team replies directly.\n\n"
        f"#ProductLaunch #SoftwareEngineering #AI #Automation #{slug}"
    )
    reddit_post = {
        "title": f"I built {app_name} — {value_prop}",
        "body": (
            f"Hey everyone,\n\nI wanted to share {app_name}: {value_prop}\n\n"
            f"**Where to find it:** {app_url}\n"
            f"**How to run it:** {how_to_use}\n\n"
            "Happy to answer technical questions or take feedback in the comments!"
        ),
    }
    yt_brief = {
        "video_title": f"How to Use {app_name} in 60 Seconds ({value_prop[:45]})",
        "description": (
            f"{app_name}: {value_prop}\n\n"
            f"Find it here: {app_url}\n\n"
            f"How to use {app_name}:\n{how_to_use}\n\n"
            "#Shorts #TechDemo #Productivity"
        ),
        "hook_0_4s": f"Stop wasting hours manually — here is how {app_name} solves it in seconds.",
        "demo_beats": [
            f"Where to find {app_name}: {app_url}",
            f"How to run it: {how_to_use}",
            "Live proof + CTA to subscribe & try it now",
        ],
    }

    pack = {
        "app_name": app_name,
        "app_url": app_url,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "platforms": {
            "youtube": yt_brief,
            "instagram": {
                "caption_file": ig_card["caption_file"],
                "card_image": ig_card["card_image"],
                "song_track": music_path if os.path.exists(music_path) else song_track,
                "include_voiceover": include_voiceover,
            },
            "linkedin": {"post_text": linkedin_post},
            "reddit": reddit_post,
        },
    }
    pack_path = os.path.join(pack_dir, f"{slug}_{ts}_campaign.json")
    with open(pack_path, "w", encoding="utf-8") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
    pack["pack_file"] = pack_path
    return pack


if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else "The Submarine Cable Cut: Why Global Internet Stalled"
    fmt = sys.argv[2] if len(sys.argv) > 2 else "post"
    res = generate_social_post(t, fmt)
    print("==================================================")
    print("📸 IVA STUDIOS — SOCIAL CONTENT STAGED")
    print("==================================================")
    print(f"Format:       {res['format']}")
    print(f"Topic:        {res['topic']}")
    print(f"Caption File: {res['caption_file']}")
    print(f"Image Card:   {res['card_image']}")
    print("==================================================")
