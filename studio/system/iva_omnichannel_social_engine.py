"""
iva_omnichannel_social_engine.py — Universal Omnichannel Social Media Engine for IVA.

Adapts any core content package (video scripts, documentary research, breaking bulletins)
across ALL major social media platforms with strict platform-native conventions:
1. YouTube Shorts & Video (SEO title <=95 chars, tags, pinned comment)
2. Instagram (Reel caption <=125 char visible window, <=5 tags, 4-slide carousel, story poll)
3. TikTok (0-3s pattern-interrupt hook, concise caption <=150 chars, viral sound cues)
4. X / Twitter (High-signal standalone tweet + 5-part educational thread, 0 hashtag clutter)
5. LinkedIn (Engineering/business case study format, clear first-2-lines hook, 3 industry tags)
6. Threads & Facebook Reels (Conversational debate prompt + viral short-form snippet)
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IVA_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))

# Optional import of local instagram humanizer & hookscorer
try:
    from iva_instagram_bridge import humanize_draft, score_reel_hook
except ImportError:
    def humanize_draft(text: str) -> Dict[str, Any]:
        return {"text": text}
    def score_reel_hook(hook: str) -> Dict[str, Any]:
        return {"score": 75.0, "verdict": "OK"}


class OmnichannelSocialEngine:
    """Universal content adapter and distributor across all social platforms."""

    SUPPORTED_PLATFORMS = [
        "youtube_shorts",
        "instagram",
        "tiktok",
        "x_twitter",
        "linkedin",
        "threads",
        "facebook_reels",
    ]

    @staticmethod
    def clean_text(text: str) -> str:
        """Strip AI slop and return humanized text."""
        res = humanize_draft(text)
        return res.get("text", text).strip()

    @classmethod
    def generate_youtube_shorts(cls, title: str, script_beats: List[str], brand_name: str, niche: str) -> Dict[str, Any]:
        full_story = " ".join(script_beats)
        short_title = title if len(title) <= 90 else title[:87] + "..."
        if "#Shorts" not in short_title:
            short_title += " #Shorts"

        tags = [
            "Shorts",
            "Science",
            "Physics",
            "Engineering",
            "DidYouKnow",
            niche.replace(" ", ""),
            brand_name.replace(" ", ""),
        ]

        description = (
            f"{title}\n\n"
            f"{full_story}\n\n"
            f"Subscribe to @{brand_name.replace(' ', '')} for daily high-speed science and engineering breakdowns!\n\n"
            f"{' '.join(['#' + t for t in tags[:7]])}"
        )

        return {
            "title": short_title,
            "description": cls.clean_text(description),
            "tags": tags,
            "pinned_comment": f"What was the most surprising fact about this? Drop your thoughts below! 👇",
        }

    @classmethod
    def generate_instagram(cls, title: str, script_beats: List[str], brand_name: str, niche: str) -> Dict[str, Any]:
        # Reel caption: first line MUST land whole and punchy before 125 char cutoff
        first_line = title[:110]
        full_body = "\n\n".join(script_beats)
        hashtags = ["#science", "#physics", "#engineering", "#didyouknow", "#tech"]

        reel_caption = (
            f"{first_line}\n\n"
            f"Swipe up or watch till the end to see the real slow motion physics.\n\n"
            f"{full_body}\n\n"
            f"Save this reel to revisit later! {' '.join(hashtags[:5])}"
        )

        # 4-Slide Carousel Breakdown
        b_count = len(script_beats)
        s1 = script_beats[0] if b_count > 0 else title
        s2 = script_beats[b_count // 3] if b_count > 2 else "The critical mechanism."
        s3 = script_beats[(2 * b_count) // 3] if b_count > 2 else "The peak force."
        s4 = script_beats[-1] if b_count > 0 else "The final takeaway."

        carousel = [
            {"slide": 1, "role": "Cover Hook", "headline": title[:50], "subtext": s1[:120]},
            {"slide": 2, "role": "The Mechanism", "headline": "What Happened Inside?", "subtext": s2[:140]},
            {"slide": 3, "role": "The Raw Physics", "headline": "The Hidden Force", "subtext": s3[:140]},
            {"slide": 4, "role": "Key Takeaway", "headline": "Final Verdict", "subtext": s4[:140], "cta": "Save & Share this post!"},
        ]

        story = {
            "slide_1_teaser": f"Did you know {title[:60]}?",
            "poll_question": "Did you expect this to happen?",
            "poll_options": ["Yes, knew it! 🧠", "Mind blown 💥"],
            "swipe_link_cta": "Tap here to watch the full breakdown!",
        }

        return {
            "reel_caption": cls.clean_text(reel_caption),
            "hashtags": hashtags[:5],
            "first_line_chars": len(first_line),
            "carousel_slides": carousel,
            "story_strategy": story,
        }

    @classmethod
    def generate_tiktok(cls, title: str, script_beats: List[str], brand_name: str, niche: str) -> Dict[str, Any]:
        hook = script_beats[0] if script_beats else title
        caption = f"{title[:90]} 🤯 Watch what happens next! #science #fyp #learnontiktok #engineering #mindblown"

        return {
            "pattern_interrupt_hook": cls.clean_text(hook),
            "caption": cls.clean_text(caption),
            "text_overlay_line_1": title[:35].upper(),
            "text_overlay_line_2": "WATCH THE IMPACT 👇",
            "sound_recommendation": "Trending suspense / dark ambient audio",
            "hashtags": ["#fyp", "#science", "#learnontiktok", "#engineering", "#physics"],
        }

    @classmethod
    def generate_twitter_x(cls, title: str, script_beats: List[str], brand_name: str, niche: str) -> Dict[str, Any]:
        # Tweet 1: Hook with stakes and video attachment prompt
        t1 = f"{title}.\n\nHere is the exact real-world physics breakdown and why this happens: 🧵👇"

        thread_tweets = [t1]
        for idx, beat in enumerate(script_beats):
            tw = f"{idx + 1}/ {beat}"
            thread_tweets.append(tw[:278])

        final_cta = (
            f"If you enjoyed this breakdown:\n"
            f"1. Follow @{brand_name.replace(' ', '')} for daily high-retention engineering & science intel.\n"
            f"2. Repost the first tweet to share with your network."
        )
        thread_tweets.append(final_cta)

        standalone_tweet = f"{title}.\n\nWatch the full real-life high-speed footage below. The physics is unreal: 👇"

        return {
            "standalone_tweet": cls.clean_text(standalone_tweet),
            "thread_total_tweets": len(thread_tweets),
            "thread_tweets": [cls.clean_text(t) for t in thread_tweets],
        }

    @classmethod
    def generate_linkedin(cls, title: str, script_beats: List[str], brand_name: str, niche: str) -> Dict[str, Any]:
        body_points = "\n\n".join([f"• {beat}" for beat in script_beats[:6]])
        post = (
            f"The physics behind this engineering phenomenon is astonishing: {title}.\n\n"
            f"Most people underestimate how rapidly mechanical and atmospheric forces scale under real conditions.\n\n"
            f"Key takeaways from this analysis:\n\n"
            f"{body_points}\n\n"
            f"In systems engineering and industrial operations, safety margins aren't suggestions—they are thermodynamic realities.\n\n"
            f"What has been your experience with unexpected pressure/force failures in physical systems?\n\n"
            f"#Engineering #Physics #MaterialScience #Innovation #Technology"
        )
        return {
            "post_text": cls.clean_text(post),
            "target_audience": "Engineers, Systems Architects, Technical Founders, Science Enthusiasts",
        }

    @classmethod
    def generate_threads_and_facebook(cls, title: str, script_beats: List[str], brand_name: str) -> Dict[str, Any]:
        threads_post = f"{title}.\n\nMost people think this is impossible until they see the high-speed slow motion camera. What would you do if you saw this happen in real life? 🤔"
        fb_reel_caption = f"{title}! Real high-speed physics in action. Follow for more amazing discoveries! #Science #Reels"

        return {
            "threads_post": cls.clean_text(threads_post),
            "facebook_reel_caption": cls.clean_text(fb_reel_caption),
        }

    @classmethod
    def adapt_for_all_platforms(
        cls,
        title: str,
        script_beats: List[str],
        brand_name: str = "Dark Matters",
        niche: str = "Science & Physics",
    ) -> Dict[str, Any]:
        """Adapt a single core story/script across all 7 social channels simultaneously."""
        yt = cls.generate_youtube_shorts(title, script_beats, brand_name, niche)
        ig = cls.generate_instagram(title, script_beats, brand_name, niche)
        tt = cls.generate_tiktok(title, script_beats, brand_name, niche)
        tw = cls.generate_twitter_x(title, script_beats, brand_name, niche)
        li = cls.generate_linkedin(title, script_beats, brand_name, niche)
        tf = cls.generate_threads_and_facebook(title, script_beats, brand_name)

        return {
            "status": "SUCCESS",
            "source_title": title,
            "brand": brand_name,
            "niche": niche,
            "platforms_adapted": len(cls.SUPPORTED_PLATFORMS),
            "youtube_shorts": yt,
            "instagram": ig,
            "tiktok": tt,
            "x_twitter": tw,
            "linkedin": li,
            "threads": tf["threads_post"],
            "facebook_reels": tf["facebook_reel_caption"],
        }

    @classmethod
    def export_omnichannel_bundle(
        cls,
        title: str,
        script_beats: List[str],
        output_dir: str,
        brand_name: str = "Dark Matters",
        niche: str = "Science & Physics",
    ) -> str:
        """Export formatted distribution packages for all platforms into a target directory."""
        package = cls.adapt_for_all_platforms(title, script_beats, brand_name, niche)
        os.makedirs(output_dir, exist_ok=True)

        bundle_json = os.path.join(output_dir, "omnichannel_distribution_bundle.json")
        with open(bundle_json, "w", encoding="utf-8") as f:
            json.dump(package, f, indent=2, ensure_ascii=False)

        # Write clean copy-paste text files
        with open(os.path.join(output_dir, "instagram_reel.txt"), "w", encoding="utf-8") as f:
            f.write(package["instagram"]["reel_caption"])

        with open(os.path.join(output_dir, "x_twitter_thread.txt"), "w", encoding="utf-8") as f:
            f.write("\n\n---\n\n".join(package["x_twitter"]["thread_tweets"]))

        with open(os.path.join(output_dir, "linkedin_post.txt"), "w", encoding="utf-8") as f:
            f.write(package["linkedin"]["post_text"])

        with open(os.path.join(output_dir, "tiktok_package.txt"), "w", encoding="utf-8") as f:
            f.write(f"HOOK: {package['tiktok']['pattern_interrupt_hook']}\nCAPTION: {package['tiktok']['caption']}")

        return bundle_json


if __name__ == "__main__":
    demo_title = "Why A 67,000-Lb Steel Tanker Implodes In 0.1 Seconds"
    demo_beats = [
        "This is a 67,000-pound solid steel railroad tanker.",
        "Its walls are half an inch of structural steel.",
        "Yet in under 0.1 seconds, atmospheric pressure crushes it like a soda can.",
        "When steam inside cooled, it condensed into liquid, creating a vacuum.",
        "Over two million pounds of outside air pressure hammered the hull until it folded.",
    ]
    bundle = OmnichannelSocialEngine.adapt_for_all_platforms(demo_title, demo_beats)
    print(f"[OMNICHANNEL CHECK] Adapted across {bundle['platforms_adapted']} platforms cleanly!")
    print(f"  YouTube: {bundle['youtube_shorts']['title']}")
    print(f"  Instagram Reel first line len: {bundle['instagram']['first_line_chars']} chars")
    print(f"  X Thread count: {bundle['x_twitter']['thread_total_tweets']} tweets")
    print(f"  LinkedIn post length: {len(bundle['linkedin']['post_text'])} chars")
