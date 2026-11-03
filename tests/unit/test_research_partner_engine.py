"""Unit test suite for IVA ResearchPartnerEngine & Architectural Scaffolding.
================================================================================
Tests:
1. Architectural scope deduction across intents.
2. Upfront questions generation (zero mid-turn stalling).
3. 5 bespoke aesthetic themes & CSS variable generation.
4. Generation of all 5 specification contracts.
5. Autonomous multi-scope project scaffolding without external pip dependencies.
================================================================================
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agents.IVA.engine.agi17.research.research_partner_engine import (
    ArchitecturalScope,
    DesignAestheticTheme,
    ResearchPartnerEngine,
)


class TestResearchPartnerEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="iva_research_test_"))

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_scope_deduction(self) -> None:
        self.assertEqual(
            ResearchPartnerEngine.deduce_architectural_scope("fix bug in ast parser"),
            ArchitecturalScope.BUG_DETECTION_CI,
        )
        self.assertEqual(
            ResearchPartnerEngine.deduce_architectural_scope("landing page with three.js only"),
            ArchitecturalScope.FRONTEND_ONLY,
        )
        self.assertEqual(
            ResearchPartnerEngine.deduce_architectural_scope("enterprise microservice with docker"),
            ArchitecturalScope.ENTERPRISE_SYSTEM,
        )
        self.assertEqual(
            ResearchPartnerEngine.deduce_architectural_scope("meetup tracking system"),
            ArchitecturalScope.FULL_STACK_APP,
        )

    def test_02_upfront_questions_intake(self) -> None:
        questions = ResearchPartnerEngine.generate_upfront_questions("build a spatial app")
        self.assertEqual(len(questions), 2)
        q_ids = [q.question_id for q in questions]
        self.assertIn("scope", q_ids)
        self.assertIn("aesthetic", q_ids)

    def test_03_design_tokens_and_anti_cliche_palettes(self) -> None:
        for theme in DesignAestheticTheme:
            tokens = ResearchPartnerEngine.DESIGN_PALETTES[theme]
            self.assertTrue(tokens.bg_primary)
            self.assertTrue(tokens.accent_primary)
            css_vars = tokens.to_css_variables()
            self.assertIn("--bg-primary:", css_vars)
            self.assertIn("--accent-primary:", css_vars)
            self.assertIn("--font-heading:", css_vars)

    def test_04_all_five_spec_contracts_generation(self) -> None:
        req = ResearchPartnerEngine.generate_requirements_specification(
            "TestNexus", "High speed execution", ArchitecturalScope.FULL_STACK_APP
        )
        self.assertIn("Requirements Specification Contract", req)
        self.assertIn("TestNexus", req)

        design = ResearchPartnerEngine.generate_design_specification(
            "TestNexus", DesignAestheticTheme.CYBER_TERMINAL
        )
        self.assertIn("Design Specification Contract", design)
        self.assertIn("Cyber-Terminal", design)

        media = ResearchPartnerEngine.generate_media_assets_spec(
            "TestNexus", "Spatial 3D canvas", DesignAestheticTheme.NEO_GLASS_SAAS
        )
        self.assertIn("Media Assets Specification", media)
        self.assertIn("DALL-E 3", media)
        self.assertIn("Gemini Omni", media)

        verif = ResearchPartnerEngine.generate_verification_plan(
            "TestNexus", ArchitecturalScope.FULL_STACK_APP
        )
        self.assertIn("Verification & Test Plan", verif)

        arch = ResearchPartnerEngine.generate_architecture_specification(
            "TestNexus", ArchitecturalScope.FULL_STACK_APP, ["server.py", "index.html"]
        )
        self.assertIn("System Architecture Specification Contract", arch)

    def test_05_scaffold_frontend_only(self) -> None:
        target = self.temp_dir / "frontend_proj"
        res = ResearchPartnerEngine.scaffold_project_files(
            target_dir=target,
            project_name="SpatialLanding",
            scope=ArchitecturalScope.FRONTEND_ONLY,
            theme=DesignAestheticTheme.CYBER_TERMINAL,
            vision="3D spatial showcase",
        )
        self.assertEqual(res["status"], "SCAFFOLDED_SUCCESSFULLY")
        self.assertTrue((target / "index.html").is_file())
        self.assertTrue((target / "css" / "styles.css").is_file())
        self.assertTrue((target / "js" / "app.js").is_file())
        self.assertTrue((target / "REQUIREMENTS_SPEC.md").is_file())
        self.assertTrue((target / "DESIGN_SPEC.md").is_file())
        self.assertTrue((target / "ARCH_SPEC.md").is_file())
        self.assertTrue((target / "VERIFICATION_PLAN.md").is_file())
        self.assertTrue((target / "MEDIA_ASSETS_SPEC.md").is_file())

    def test_06_scaffold_full_stack(self) -> None:
        target = self.temp_dir / "fullstack_proj"
        res = ResearchPartnerEngine.scaffold_project_files(
            target_dir=target,
            project_name="NexusStack",
            scope=ArchitecturalScope.FULL_STACK_APP,
            theme=DesignAestheticTheme.BRUTALIST_FINTECH,
            vision="Trading analytics dashboard",
        )
        self.assertEqual(res["status"], "SCAFFOLDED_SUCCESSFULLY")
        self.assertTrue((target / "backend" / "server.py").is_file())
        self.assertTrue((target / "frontend" / "index.html").is_file())
        self.assertTrue((target / "tests" / "test_api.py").is_file())


if __name__ == "__main__":
    unittest.main()
