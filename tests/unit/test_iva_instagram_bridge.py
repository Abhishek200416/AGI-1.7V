import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "studio", "system"))
import iva_instagram_bridge as bridge


class TestIvaInstagramBridge(unittest.TestCase):
    def test_installation_check(self):
        installed = bridge.is_iva_instagram_skill_installed()
        self.assertTrue(installed, "iva-instagram-skill should be installed and recognized")

    def test_hook_scoring(self):
        hook = "I lost $18,000 on one missing contract."
        res = bridge.score_reel_hook(hook)
        self.assertIn("score", res)
        self.assertIn("verdict", res)
        self.assertGreater(res["score"], 50.0)

    def test_humanize_slop_stripping(self):
        dirty = "Furthermore, it is crucial to leverage cutting-edge AI."
        res = bridge.humanize_draft(dirty)
        clean = res.get("text", "")
        self.assertNotIn("cutting-edge", clean)
        self.assertNotIn("furthermore", clean.lower())

    def test_caption_linting(self):
        cap = (
            "Why a 67,000-pound train tanker was crushed by air pressure.\n\n"
            "Save this video for later! #science #physics #engineering"
        )
        res = bridge.lint_caption(cap)
        self.assertIn("verdict", res)
        self.assertIn("visible", res)
        self.assertIn(res["verdict"], ("READY", "REVIEW", "REWRITE", "PASS", "WARN", "OK"))

    def test_repurpose_short_to_ig(self):
        res = bridge.repurpose_short_to_ig(
            short_title="Why A 67,000-Lb Steel Tanker Implodes In 0.1 Seconds",
            script_beats=[
                "This is a 67,000-pound solid steel railroad tanker.",
                "Its cylindrical walls are half an inch of structural steel.",
                "Yet in less than 0.1 seconds, atmospheric pressure crushes it like a soda can.",
            ],
            niche_tags=["#science", "#physics", "#shorts"],
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("hooks", res)
        self.assertGreaterEqual(len(res["hooks"]), 3)
        self.assertIn("carousel_slides", res)
        self.assertEqual(len(res["carousel_slides"]), 4)
        self.assertIn("story_poll", res)


if __name__ == "__main__":
    unittest.main()
