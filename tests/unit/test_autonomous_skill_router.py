"""
Unit tests for AutonomousSkillRouter & Dynamic Skill Execution Engine.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from agents.IVA.ecosystem.agent_registry.agent_contract import AgentContract
from agents.IVA.ecosystem.agent_registry.ecosystem_coordinator import EcosystemCoordinator
from agents.IVA.ecosystem.autonomous_skill_router import (
    AutonomousSkillRouter,
    SkillExecutionResult,
    SkillMatch,
    SkillPipeline,
    autonomous_skill_router,
)
from agents.IVA.ecosystem.iva_skills_registry import SkillCategory, iva_skills_registry


class TestAutonomousSkillRouter(unittest.TestCase):
    def setUp(self) -> None:
        self.router = AutonomousSkillRouter()

    def test_route_skills_social_intent(self) -> None:
        intent = "Generate an Instagram reel hook and humanize the caption"
        matches = self.router.route_skills(intent, limit=3)
        self.assertTrue(len(matches) > 0)
        top_skill = matches[0]
        self.assertIn("instagram", top_skill.skill.name)
        self.assertGreater(top_skill.score, 0.4)
        self.assertTrue(len(top_skill.matched_reasons) > 0)

    def test_route_skills_quant_intent(self) -> None:
        intent = "Calibrate Hawkes process and SSVI volatility surface for NIFTY options"
        matches = self.router.route_skills(intent, limit=3)
        self.assertTrue(len(matches) > 0)
        matched_names = [m.skill.name for m in matches]
        self.assertTrue(
            any("quant" in n or "volatility" in n or "option" in n for n in matched_names),
            f"Expected quant skill in matches: {matched_names}",
        )

    def test_route_skills_browser_intent(self) -> None:
        intent = "Automate browser navigation and inspect DOM accessibility"
        matches = self.router.route_skills(intent, limit=3)
        self.assertTrue(len(matches) > 0)
        matched_names = [m.skill.name for m in matches]
        self.assertTrue(
            any("playwright" in n or "browser" in n for n in matched_names),
            f"Expected browser skill in matches: {matched_names}",
        )

    def test_resolve_best_skill(self) -> None:
        best = self.router.resolve_best_skill("Execute multi-step sequential thinking step-by-step")
        self.assertIsNotNone(best)
        self.assertEqual(best.name, "sequential-thinking")

    def test_compose_pipeline_video_domain(self) -> None:
        pipeline = self.router.compose_pipeline("Create vertical YouTube shorts and adapt to instagram reels")
        self.assertIsInstance(pipeline, SkillPipeline)
        self.assertEqual(pipeline.name, "Omnichannel Media Production & Social Pipeline")
        self.assertEqual(len(pipeline.stages), 4)
        stage_skills = [s.skill_name for s in pipeline.stages]
        self.assertIn("iva-instagram-skill", stage_skills)
        self.assertIn("iva-omnichannel-social-skill", stage_skills)

    def test_compose_pipeline_bug_fix(self) -> None:
        pipeline = self.router.compose_pipeline("Fix broken exception and debug root-cause in backend")
        self.assertEqual(pipeline.name, "Autonomous Bug Triage & Minimal Refactoring Pipeline")
        self.assertEqual(len(pipeline.stages), 4)
        stage_skills = [s.skill_name for s in pipeline.stages]
        self.assertIn("gsd-debug", stage_skills)
        self.assertIn("ponytail", stage_skills)

    def test_compose_pipeline_quant_domain(self) -> None:
        pipeline = self.router.compose_pipeline("Backtest quant trading strategy on nifty with risk limits")
        self.assertEqual(pipeline.name, "Institutional Quantitative Execution & Risk Pipeline")
        self.assertEqual(len(pipeline.stages), 4)

    def test_execute_native_handler_sequential_thinking(self) -> None:
        res = self.router.execute_skill(
            "sequential-thinking",
            {"thought": "Decomposing task into steps", "thoughtNumber": 1, "totalThoughts": 3},
        )
        self.assertTrue(res.success)
        self.assertEqual(res.execution_mode, "native_handler")
        self.assertEqual(res.output["step"], 1)
        self.assertTrue(res.output["verified"])

    def test_execute_native_handler_risk_management(self) -> None:
        # Order within safety limits
        res_ok = self.router.execute_skill(
            "trading-risk-management",
            {"capital": 10000.0, "order_size": 1500.0, "max_daily_loss": 2500.0, "loss_so_far": 500.0},
        )
        self.assertTrue(res_ok.success)
        self.assertTrue(res_ok.output["approved"])

        # Order exceeding max allocation limit (> 20%)
        res_blocked = self.router.execute_skill(
            "trading-risk-management",
            {"capital": 10000.0, "order_size": 3000.0, "max_daily_loss": 2500.0, "loss_so_far": 500.0},
        )
        self.assertTrue(res_blocked.success)
        self.assertFalse(res_blocked.output["approved"])
        self.assertIn("exceeds 20% max allocation", res_blocked.output["reason"])

    def test_execute_mcp_fallback_for_catalog_skill(self) -> None:
        res = self.router.execute_skill("cloudrun", {"service_name": "api-service"})
        self.assertTrue(res.success)
        self.assertEqual(res.execution_mode, "mcp_fallback")
        self.assertEqual(res.output["status"], "ready_for_tool_invocation")
        self.assertIn("deploy_container_image", res.output["tools_available"])

    def test_execute_unknown_skill(self) -> None:
        res = self.router.execute_skill("non_existent_fake_skill_999", {})
        self.assertFalse(res.success)
        self.assertEqual(res.execution_mode, "error")
        self.assertIn("not registered", res.error)

    def test_coordinator_dynamic_skill_routing_integration(self) -> None:
        coordinator = EcosystemCoordinator()
        contract = AgentContract(
            agent_id="swe_python_runtime_engineer",
            display_name="Python Runtime Engineer",
            family="software_engineering",
            primary_capabilities=["python"],
            non_goals=[],
            required_tools=[],
            forbidden_tools=[],
            execution_mode="IN_PROCESS_TOOL_WORKER",
            resource_class="LIGHT",
            default_effort_tier="medium",
            max_token_budget=10000,
            max_wall_clock_seconds=60,
            max_retries=1,
            input_schema={},
            output_schema={},
            verification_hook="smoke",
        )

        # Baseline without task_intent
        baseline_railings = coordinator.build_coordination_railings(contract)
        self.assertEqual(len(baseline_railings["dynamic_skills_routed"]), 0)

        # Railings with task_intent requesting Instagram social adaptation
        dynamic_railings = coordinator.build_coordination_railings(
            contract,
            task_intent="Adapt our video reel for Instagram viral distribution",
        )
        self.assertGreater(len(dynamic_railings["dynamic_skills_routed"]), 0)
        self.assertIn("iva-instagram-skill", dynamic_railings["skills_applied"])


if __name__ == "__main__":
    unittest.main()
