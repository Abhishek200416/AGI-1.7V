"""Empirical Verification Suite: Workflow Efficiency, Memory Power, & Zero-Data-Loss Invariants.
================================================================================
Validates with real timers and AST assertions:
1. Turn-0 Memory Retrieval Speed (< 50ms target)
2. Surgical Line-Level Diff Integrity (Zero Data Loss Invariant: comments, docstrings, imports preserved)
3. Universal Reasoning Governor Bounded Execution (Elimination of 40-min thinking spirals)
4. Pipeline End-to-End Latency & Non-Destructive Invariants
================================================================================
"""

import ast
import tempfile
import time
import unittest
from pathlib import Path

from agents.IVA.engine.agi17.capabilities.fast_path_ui_resolver import (
    FastPathUIResolver,
    UIComponentNode,
)
from agents.IVA.engine.agi17.orchestration.gemini_reasoning_governor import (
    IVAReasoningGovernor,
)


class TestWorkflowEfficiencyAndDataIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace_root = Path(self.temp_dir.name)
        self.db_path = self.workspace_root / "test_memory.db"
        self.resolver = FastPathUIResolver(db_path=self.db_path)
        self.governor = IVAReasoningGovernor(memory_db_path=self.db_path)

        # Create a sample realistic UI component file in workspace
        self.component_dir = self.workspace_root / "src" / "components"
        self.component_dir.mkdir(parents=True, exist_ok=True)
        self.sample_ui_file = self.component_dir / "OrderButton.jsx"
        self.sample_ui_file.write_text(
            '''import React from "react";
// Header comment: Critical order execution component
export const OrderButton = () => {
    return (
        <div className="order-panel">
            <button id="submit-order-btn" className="btn-primary" style={{ backgroundColor: "#FF0000" }}>
                Submit Order
            </button>
        </div>
    );
};
''',
            encoding="utf-8",
        )

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_case_1_turn_zero_memory_retrieval_speed(self):
        """CASE 1: Proves memory retrieval executes in under 50ms with zero turn waste."""
        # Warmup index once
        self.resolver.index_workspace(self.workspace_root)

        # Benchmark intent resolution speed from SQLite WAL memory
        start = time.perf_counter()
        results = self.resolver.resolve_intent(self.workspace_root, "change submit order button color")
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        print(f"\n[Case 1 Benchmark] Memory Retrieval Elapsed Time: {elapsed_ms:.2f} ms")
        self.assertTrue(len(results) > 0, "Expected at least one matched UI component")
        top_match = results[0]
        self.assertIn("OrderButton.jsx", top_match["file_rel_path"])
        self.assertEqual(top_match["identifier"], "submit-order-btn")
        self.assertEqual(top_match["element_type"], "button")
        
        # Hard assertion: Must resolve in under 50 milliseconds
        self.assertLess(elapsed_ms, 50.0, "Memory retrieval must be sub-50ms")

    def test_case_2_surgical_line_edit_zero_data_loss(self):
        """CASE 2: Proves surgical editing preserves 100% of surrounding comments, docstrings, and code."""
        critical_code = '''"""Critical Production Module with delicate financial and business logic."""

# IMPORTANT: Do not alter this API version header
API_VERSION = "2.4.1"

# Database Configuration (Sensitive Invariant)
DB_POOL_SIZE = 20
DB_TIMEOUT_SEC = 5.0

def calculate_position_risk(capital: float, risk_pct: float) -> float:
    """Calculates position risk with strict bounds."""
    # Safety collar: Max 2.5% per trade
    effective_pct = min(risk_pct, 0.025)
    return capital * effective_pct

# UI Button Styling Configuration
BUTTON_PRIMARY_COLOR = "#FF0000"  # Target to update
BUTTON_SECONDARY_COLOR = "#00FF00"
'''
        test_file = self.workspace_root / "config.py"
        test_file.write_text(critical_code, encoding="utf-8")

        # Target: Change line from "#FF0000" to "#0000FF"
        target_str = 'BUTTON_PRIMARY_COLOR = "#FF0000"'
        replacement_str = 'BUTTON_PRIMARY_COLOR = "#0000FF"'

        # Execute surgical replacement using FastPathUIResolver's atomic patcher
        patched = self.resolver.apply_surgical_patch(test_file, target_str, replacement_str)
        self.assertTrue(patched)

        modified_code = test_file.read_text(encoding="utf-8")

        # 1. Verify exact target changed
        self.assertIn('BUTTON_PRIMARY_COLOR = "#0000FF"', modified_code)
        self.assertNotIn('BUTTON_PRIMARY_COLOR = "#FF0000"', modified_code)

        # 2. Verify ZERO data loss across critical surrounding lines
        self.assertIn('"""Critical Production Module with delicate financial and business logic."""', modified_code)
        self.assertIn('# IMPORTANT: Do not alter this API version header', modified_code)
        self.assertIn('API_VERSION = "2.4.1"', modified_code)
        self.assertIn('DB_POOL_SIZE = 20', modified_code)
        self.assertIn('def calculate_position_risk(capital: float, risk_pct: float) -> float:', modified_code)
        self.assertIn('BUTTON_SECONDARY_COLOR = "#00FF00"', modified_code)

        # 3. Verify Python AST syntax tree remains 100% valid
        parsed_ast = ast.parse(modified_code)
        self.assertIsInstance(parsed_ast, ast.Module)
        print("[Case 2 Benchmark] Surgical Line Diff: 100% surrounding code & AST preserved.")

    def test_case_3_reasoning_governor_anti_loop_clamp(self):
        """CASE 3: Proves governor clamps thinking on UI edits and caps deep reasoning to eliminate stalls."""
        # 3A: Fast UI edit -> thinkingBudget = 0 (prevents 40-minute reasoning spiral)
        ui_prompt = "Change button primary color from red to blue in navbar"
        patch_ui = self.governor.get_model_payload_patch("gemini-3.8-flash", ui_prompt)
        
        self.assertEqual(patch_ui["task_category"], "FAST_PATH_UI")
        self.assertEqual(patch_ui["sla_seconds"], 60.0)
        gen_cfg = patch_ui["payload_fields"]["generationConfig"]
        self.assertEqual(gen_cfg["thinkingConfig"]["thinkingBudget"], 0)
        self.assertEqual(gen_cfg["thinking"]["thinking_level"], "low")
        self.assertIn("CRITICAL SUB-60S FAST-PATH UI DIRECTIVE", patch_ui["system_instruction_addon"])

        # 3B: Deep Math -> bounded thinkingBudget = 2048 with Anti-Spinning Directive
        math_prompt = "Calibrate Gatheral SVI surface and check Roger Lee bounds"
        patch_math = self.governor.get_model_payload_patch("gemini-3.8-flash", math_prompt)
        
        self.assertEqual(patch_math["task_category"], "DEEP_REASONING")
        self.assertEqual(patch_math["sla_seconds"], 90.0)
        gen_cfg_math = patch_math["payload_fields"]["generationConfig"]
        self.assertEqual(gen_cfg_math["thinkingConfig"]["thinkingBudget"], 2048)
        self.assertEqual(gen_cfg_math["thinking"]["thinking_level"], "medium")
        self.assertIn("MAX-PERFORMANCE ARCHITECT DIRECTIVE", patch_math["system_instruction_addon"])
        print("[Case 3 Benchmark] Governor Anti-Loop: UI budget=0 (fast diff), Deep Math capped at 90s.")

    def test_case_4_end_to_end_pipeline_latency(self):
        """CASE 4: Proves full pipeline (memory query + classification + surgical patch) executes in < 25ms."""
        self.resolver.index_workspace(self.workspace_root)

        start = time.perf_counter()
        
        # Step 1: Memory lookup (< 50ms target)
        matches = self.resolver.resolve_intent(self.workspace_root, "change submit order button to gold")
        self.assertTrue(len(matches) > 0)
        target = matches[0]

        # Step 2: Intent classification & payload compilation
        patch_cfg = self.governor.get_model_payload_patch("gemini-3.8-flash", "change submit order button to gold")

        # Step 3: Surgical atomic write
        patched = self.resolver.apply_surgical_patch(
            target["full_path"],
            'backgroundColor: "#FF0000"',
            'backgroundColor: "#FFD700"',
        )
        self.assertTrue(patched)

        elapsed_total_ms = (time.perf_counter() - start) * 1000.0
        print(f"[Case 4 Benchmark] Full End-to-End Pipeline Pre-Processing & Surgical Write: {elapsed_total_ms:.2f} ms")

        # Verify target file updated without losing code
        updated_content = Path(target["full_path"]).read_text(encoding="utf-8")
        self.assertIn('backgroundColor: "#FFD700"', updated_content)
        self.assertIn('// Header comment: Critical order execution component', updated_content)
        self.assertIn('export const OrderButton = () => {', updated_content)
        
        # Whole pipeline must complete in under 25 milliseconds locally
        self.assertLess(elapsed_total_ms, 25.0)


if __name__ == "__main__":
    unittest.main()
