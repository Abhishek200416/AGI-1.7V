import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "studio", "system"))
from iva_omnichannel_social_engine import OmnichannelSocialEngine


class TestIvaOmnichannelSocialEngine(unittest.TestCase):
    def setUp(self):
        self.title = "Why A 67,000-Lb Steel Tanker Implodes In 0.1 Seconds"
        self.beats = [
            "This is a 67,000-pound solid steel railroad tanker.",
            "Its walls are half an inch of structural steel.",
            "Yet in under 0.1 seconds, atmospheric pressure crushes it like a soda can.",
            "When steam inside cooled, it condensed into liquid, creating a vacuum.",
            "Over two million pounds of outside air pressure hammered the hull until it folded.",
        ]
        self.brand = "Dark Matters"
        self.niche = "Science & Physics"

    def test_adapt_for_all_platforms(self):
        res = OmnichannelSocialEngine.adapt_for_all_platforms(
            self.title, self.beats, self.brand, self.niche
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["platforms_adapted"], 7)

        # YouTube Shorts verification
        yt = res["youtube_shorts"]
        self.assertIn("#Shorts", yt["title"])
        self.assertIn("tags", yt)
        self.assertIn("pinned_comment", yt)

        # Instagram verification
        ig = res["instagram"]
        self.assertLessEqual(ig["first_line_chars"], 125)
        self.assertLessEqual(len(ig["hashtags"]), 5)
        self.assertEqual(len(ig["carousel_slides"]), 4)
        self.assertIn("poll_question", ig["story_strategy"])

        # TikTok verification
        tt = res["tiktok"]
        self.assertIn("pattern_interrupt_hook", tt)
        self.assertIn("caption", tt)

        # X / Twitter verification
        tw = res["x_twitter"]
        self.assertGreaterEqual(tw["thread_total_tweets"], 5)
        self.assertIn("standalone_tweet", tw)

        # LinkedIn verification
        li = res["linkedin"]
        self.assertIn("post_text", li)
        self.assertIn("Engineering", li["post_text"])

        # Threads and FB verification
        self.assertIn("threads", res)
        self.assertIn("facebook_reels", res)

    def test_export_bundle(self):
        import tempfile
        import shutil
        tdir = tempfile.mkdtemp(prefix="omni_test_")
        try:
            bundle_file = OmnichannelSocialEngine.export_omnichannel_bundle(
                self.title, self.beats, tdir, self.brand, self.niche
            )
            self.assertTrue(os.path.isfile(bundle_file))
            self.assertTrue(os.path.isfile(os.path.join(tdir, "instagram_reel.txt")))
            self.assertTrue(os.path.isfile(os.path.join(tdir, "x_twitter_thread.txt")))
            self.assertTrue(os.path.isfile(os.path.join(tdir, "linkedin_post.txt")))
            self.assertTrue(os.path.isfile(os.path.join(tdir, "tiktok_package.txt")))
        finally:
            shutil.rmtree(tdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
