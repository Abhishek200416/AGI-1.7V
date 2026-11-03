"""Unit Tests for UserProspectErgonomicsAnalyzer."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agents.IVA.engine.agi17.capabilities.user_experience_heuristics import (
    UserProspectErgonomicsAnalyzer,
    evaluate_ui_perspective
)


class TestUserExperienceHeuristics(unittest.TestCase):
    """Verifies that the UX Heuristics Engine detects friction, calculates thumb scores, and rates immersion."""

    def test_01_detects_heavy_header_friction(self) -> None:
        """Verifies that a heavy fixed header triggers a friction warning."""
        html = "<header class='hud-header'><h1>Test</h1></header>"
        css = ".hud-header { height: 80px; position: fixed; top: 0; }"
        js = "console.log('init');"

        report = UserProspectErgonomicsAnalyzer.audit_interface_code(html, css, js)
        self.assertGreater(report.friction_score, 20.0)
        self.assertTrue(any("Heavy fixed header" in w for w in report.friction_warnings))

    def test_02_rewards_dynamic_capsule_and_zen_mode(self) -> None:
        """Verifies that dynamic island/capsule and auto-hide zen mode earn top grades."""
        html = """
        <div id='canvas-container'></div>
        <nav class='floating-capsule-island'>
            <span>🪐 AETHERIA</span>
            <button id='audio-btn'>🔊</button>
        </nav>
        <div id='bottom-dock'></div>
        """
        css = """
        touch-action: none;
        .floating-capsule-island { height: 42px; border-radius: 24px; position: fixed; top: 16px; }
        .collapsed { transform: translateY(120%); opacity: 0; }
        #bottom-dock { position: fixed; bottom: 16px; }
        @media (max-width: 768px) { .floating-capsule-island { top: 10px; } }
        @media (max-width: 480px) { #bottom-dock { bottom: 10px; } }
        """
        js = """
        const isMobile = window.innerWidth <= 768;
        // Ingress warp fly-to
        camera.position.lerp(target, 0.05);
        // Idle autohide timeout
        let idleTimer = setTimeout(() => { document.body.classList.add('idle-fade'); }, 4000);
        gain.exponentialRampToValueAtTime(0.3, now + 1.0);
        """

        report = UserProspectErgonomicsAnalyzer.audit_interface_code(html, css, js)
        self.assertGreaterEqual(report.immersion_ratio, 0.94)
        self.assertGreaterEqual(report.hook_score, 85.0)
        self.assertGreaterEqual(report.thumb_ergonomics_score, 85.0)
        self.assertIn(report.overall_ux_grade, ["A", "A+"])

    def test_03_evaluate_convenience_helper(self) -> None:
        """Verifies the dictionary format of evaluate_ui_perspective."""
        res = evaluate_ui_perspective("<div></div>", "body { margin: 0; }", "console.log(1);")
        self.assertIn("overall_ux_grade", res)
        self.assertIn("hook_score", res)
        self.assertIn("friction_score", res)


if __name__ == "__main__":
    unittest.main()
