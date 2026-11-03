"""Unit tests for Frontier Design Engine, Git Ingestion, and Adaptive Ambiguity Evaluator.
================================================================================
AGI 1.7 / IVA Autonomous Capability Module
Tests:
1. Mathematical color calculations & WCAG contrast ratio (AA/AAA).
2. Dynamic design synthesis from arbitrary natural language vibes.
3. Git repository and directory design token extraction.
4. Persistent design system store (save, get, list, delete, export).
5. Frontier living application synthesis (Emergent & Lovable grade) and anti-AI-slop verification.
6. Adaptive ambiguity evaluation & Strategic Fork generation on serious dilemmas.
================================================================================
"""

import tempfile
import unittest
from pathlib import Path

from agents.IVA.engine.agi17.capabilities.frontier_design_engine import (
    BespokeDesignSystem,
    DesignSystemStore,
    DynamicDesignSynthesizer,
    FrontierApplicationSynthesizer,
    GitDesignExtractor,
    contrast_ratio,
    hex_to_rgb,
    relative_luminance,
    rgb_to_hex,
)
from agents.IVA.engine.agi17.research.adaptive_ambiguity_evaluator import (
    AdaptiveAmbiguityEvaluator,
    AmbiguityDimension,
)


class TestFrontierDesignEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="iva_design_test_"))

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_color_and_wcag_contrast_math(self) -> None:
        # Pure black and pure white should have maximum 21:1 contrast
        cr_max = contrast_ratio("#ffffff", "#000000")
        self.assertAlmostEqual(cr_max, 21.0, places=1)

        # Same colors should have 1:1 contrast
        cr_min = contrast_ratio("#123456", "#123456")
        self.assertAlmostEqual(cr_min, 1.0, places=1)

        # Hex conversions
        self.assertEqual(rgb_to_hex(255, 0, 128), "#ff0080")
        self.assertEqual(hex_to_rgb("#ff0080"), (255, 0, 128))
        self.assertEqual(hex_to_rgb("#fff"), (255, 255, 255))

    def test_02_dynamic_vibe_synthesis(self) -> None:
        # Test space cyber vibe
        sys = DynamicDesignSynthesizer.synthesize_from_vibe(
            name="Quantum_Void",
            vibe_description="Space dark synthwave cyber terminal with neon cyan accents",
        )
        self.assertIn("Quantum_Void", sys.name)
        self.assertEqual(sys.source, "dynamic_prompt")
        self.assertTrue(sys.contrast_ratio >= 4.5)  # Must meet WCAG AA
        self.assertIn(sys.wcag_rating, ("AA", "AAA"))

        css_vars = sys.to_css_variables()
        self.assertIn("--bg-primary:", css_vars)
        self.assertIn("--accent-primary:", css_vars)
        self.assertIn("--font-mono:", css_vars)

        tw = sys.to_tailwind_theme()
        self.assertIn("colors", tw["extend"])

    def test_03_git_directory_design_extraction(self) -> None:
        # Create a mock repo directory with CSS & HTML files
        mock_repo = self.temp_dir / "sample_app"
        mock_repo.mkdir()
        (mock_repo / "styles.css").write_text(
            """
            :root {
              --bg-primary: #050a14;
              --accent-primary: #00ffcc;
              --text-primary: #f0fdf4;
            }
            body {
              font-family: 'Space Grotesk', sans-serif;
              border-radius: 12px;
            }
            """,
            encoding="utf-8",
        )

        extracted = GitDesignExtractor.extract_from_directory(mock_repo, system_name="SampleAppDesign")
        self.assertEqual(extracted.source, "git_repo")
        self.assertEqual(extracted.name, "SampleAppDesign")
        self.assertEqual(extracted.bg_primary, "#050a14")
        self.assertEqual(extracted.accent_primary, "#00ffcc")
        self.assertIn("Space Grotesk", extracted.font_body)
        self.assertTrue(extracted.contrast_ratio >= 4.5)

    def test_04_persistent_design_store(self) -> None:
        store_dir = self.temp_dir / "design_store"
        store = DesignSystemStore(storage_dir=store_dir)

        # Baseline seed archetypes must be present
        systems = store.list_systems()
        self.assertGreaterEqual(len(systems), 6)

        # Create & save custom system
        custom = DynamicDesignSynthesizer.synthesize_from_vibe("Editorial_Autumn", "Warm editorial paper with ochre ink")
        sys_id = store.save_system(custom)
        self.assertTrue((store_dir / f"{sys_id}.json").exists())

        # Retrieve
        fetched = store.get_system(sys_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, "Editorial_Autumn")

        # Delete
        self.assertTrue(store.delete_system(sys_id))
        self.assertFalse((store_dir / f"{sys_id}.json").exists())

    def test_05_emergent_lovable_application_synthesizer(self) -> None:
        sys = DynamicDesignSynthesizer.synthesize_from_vibe(
            name="SaaS_Telemetry",
            vibe_description="Modern high-density data analytics dashboard with micro-interactions",
        )
        html = FrontierApplicationSynthesizer.synthesize_application(
            design=sys,
            app_title="ApexTelemetry",
            problem_statement="Autonomous streaming infrastructure metrics with live search and filter",
        )

        self.assertIn("ApexTelemetry", html)
        self.assertIn("spatial-canvas", html)
        self.assertIn("data-table", html)
        self.assertIn("filterMetrics", html)
        self.assertIn("modal-container", html)
        self.assertIn("WCAG", html)

    def test_06_adaptive_ambiguity_evaluator(self) -> None:
        # Routine prompt -> not serious, no fork
        r1 = AdaptiveAmbiguityEvaluator.evaluate("Create a helper function to format currency in INR")
        self.assertFalse(r1.is_serious)
        self.assertIsNone(r1.fork)

        # Destructive prompt -> serious fork
        r2 = AdaptiveAmbiguityEvaluator.evaluate("Drop all database tables and purge workspace history")
        self.assertTrue(r2.is_serious)
        self.assertEqual(r2.primary_dimension, AmbiguityDimension.DESTRUCTIVE_RISK)
        self.assertIsNotNone(r2.fork)
        self.assertGreaterEqual(len(r2.fork.options), 2)
        self.assertEqual(r2.fork.options[0].is_recommended, True)

        # Architectural fork prompt -> serious fork
        r3 = AdaptiveAmbiguityEvaluator.evaluate("Should we use Three.js WebGL or pure 2D Canvas for the visualization layer?")
        self.assertTrue(r3.is_serious)
        self.assertEqual(r3.primary_dimension, AmbiguityDimension.ARCHITECTURAL_FORK)
        self.assertIsNotNone(r3.fork)
        prompt_text = r3.fork.format_interactive_prompt()
        self.assertIn("Rendering Engine Dilemma", prompt_text)
        self.assertIn("Recommended", prompt_text)


if __name__ == "__main__":
    unittest.main()
