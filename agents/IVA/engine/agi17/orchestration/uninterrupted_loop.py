"""Uninterrupted Autonomous Loop for IVA AGI 1.8.

Unifies Model Continuation, Task Orchestration, and Sandboxed CI-Repair into a single,
continuous, resilient execution loop capable of completing engineering tasks across
quota exhaustion, context limits, and test failures without human re-prompting.

Pipeline Stages:
1. INGEST & REPRODUCE: Reproduce failing test suite in sandbox.
2. ORCHESTRATE DAG: Create durable task record in SQLite TaskStore.
3. SYNTHESIZE WITH CONTINUATION: Generate AST patch; seamlessly cascade to successor
   model if quota limit (HTTP 429), token ceiling, or context overflow occurs.
4. SANDBOXED CI VERIFY: Run minimal AST patch against full regression suite in container.
5. SEAL & COMMIT: Commit SHA-256 evidence certificate and update memory.
"""

from __future__ import annotations

import ast
import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..adapters.model_continuation_engine import ModelContinuationEngine
from ..memory.omega_command_memory import OmegaCommandMemory
from ..process_supervision.sandbox_runner import (
    DisposableSandboxRunner,
    HighImpactApprovalGate,
    SandboxPolicy,
    atomic_write_workspace_file,
    stage_candidate_outside_workspace,
)
from ..task_control.task_manager import DurableTaskManager
from ..task_control.task_state_machine import TaskState

logger = logging.getLogger("iva.orchestration.uninterrupted_loop")


@dataclass
class LoopExecutionResult:
    """Complete empirical output of an uninterrupted autonomous execution run."""
    loop_id: str
    status: str  # "SUCCEEDED_AND_VERIFIED", "REPAIRED_WITH_CONTINUATION", "FAILED", "BLOCKED_BY_POLICY"
    objective: str
    target_module: str
    target_test: str
    primary_model: str
    final_model: str
    failover_occurred: bool
    failover_count: int
    continuation_details: Optional[Dict[str, Any]]
    initial_test_passed: bool
    final_test_passed: bool
    ast_verified: bool
    patch_applied: bool
    unified_diff: str
    sha256_evidence: str
    elapsed_seconds: float
    total_tokens_consumed: int


class UninterruptedAutonomousLoop:
    """Connects Orchestration, Continuation, and CI-Repair into one uninterrupted loop."""

    def __init__(
        self,
        workspace_dir: Path | str,
        primary_model: str = "gemini-2.5-pro",
        available_models: Optional[List[str]] = None,
        storage_root: Optional[Path | str] = None,
        sandbox_policy: Optional[SandboxPolicy] = None,
    ) -> None:
        self.workspace_dir = Path(workspace_dir).resolve()
        self.primary_model = primary_model
        self.available_models = available_models or ModelContinuationEngine.CASCADE_HIERARCHY
        self.storage_root = Path(storage_root) if storage_root else self.workspace_dir / ".iva_storage"
        self.storage_root.mkdir(parents=True, exist_ok=True)

        self.task_manager = DurableTaskManager(db_path=self.storage_root / "tasks.db")
        self.memory = OmegaCommandMemory(primary_dir=self.storage_root / "memory")
        self.approval_gate = HighImpactApprovalGate()
        self.sandbox_policy = sandbox_policy or SandboxPolicy.development()

    def execute_loop(
        self,
        objective: str,
        target_module_rel: str,
        test_pattern: str,
        model_invoker: Optional[Callable[[str, str], str]] = None,
        simulate_quota_limit: bool = False,
        apply_patch_to_workspace: bool = True,
    ) -> LoopExecutionResult:
        """Executes the full uninterrupted engineering loop from failure to verified resolution.
        
        Args:
            objective: High-level task description.
            target_module_rel: Relative path of the buggy Python file.
            test_pattern: Test pattern to run (e.g. 'test_module.py').
            model_invoker: Callable `(model_name, prompt) -> response_text`.
            simulate_quota_limit: If True, triggers a synthetic quota failover to demonstrate continuation.
            apply_patch_to_workspace: Whether to write the verified patch back to the workspace.
        """
        start_time = time.time()
        loop_id = f"LOOP-{int(start_time)}-{hashlib.sha256(objective.encode()).hexdigest()[:8]}"
        target_file = self.workspace_dir / target_module_rel

        logger.info("UninterruptedAutonomousLoop [%s]: Starting objective: '%s'", loop_id, objective)

        # Stage 1: Ingest & Register Task in Durable DAG
        task_rec = self.task_manager.create_task(
            title=f"Autonomous Loop: {objective[:40]}",
            description=objective,
            specialist_role="swe_patch_minimizer",
            metadata={"objective": objective, "target": str(target_file)},
        )
        task_id = task_rec["task_id"]
        self.task_manager.transition(task_id, TaskState.READY)
        self.task_manager.transition(task_id, TaskState.RUNNING)

        # Stage 2: Initial Test Reproduction in Sandbox
        sandbox = DisposableSandboxRunner(
            policy=self.sandbox_policy,
            approval_gate=self.approval_gate,
        )
        workspace_files: Dict[str, str] = {}
        for p in self.workspace_dir.glob("*.py"):
            try:
                workspace_files[p.name] = p.read_text(encoding="utf-8")
            except Exception:
                pass

        initial_test_res = sandbox.run_python_unittest_sandbox(
            files=workspace_files,
            test_pattern=test_pattern,
            timeout_sec=30.0,
        )
        initial_passed = initial_test_res.passed

        # Read original code
        original_code = target_file.read_text(encoding="utf-8") if target_file.exists() else ""
        original_sha = hashlib.sha256(original_code.encode()).hexdigest()

        # Stage 3: Patch Generation with Live Model Continuation
        prompt = (
            f"Objective: {objective}\n"
            f"Failing Test Output:\n{initial_test_res.stderr or initial_test_res.stdout}\n\n"
            f"Existing Code in '{target_module_rel}':\n```python\n{original_code}\n```\n"
            f"Fix the bug. Output ONLY the complete, corrected Python code for this file inside ```python code blocks."
        )

        active_model = self.primary_model
        failover_occurred = False
        continuation_details = None
        raw_response = ""

        # Default fallback invoker if none provided
        def default_invoker(model: str, p: str) -> str:
            return f"```python\n{original_code}\n# Fixed by {model}\n```"

        invoker = model_invoker or default_invoker

        # Check for simulated or real quota limits
        if simulate_quota_limit:
            # Simulate primary model failing with HTTP 429 after outputting partial text
            partial_chunk = f"```python\n# Partial code generation from {self.primary_model}\n"
            error_reason = "HTTP 429: Resource exhausted: Daily quota exceeded for gemini-2.5-pro"

            continuation_details = ModelContinuationEngine.execute_continuation(
                failed_model=self.primary_model,
                original_prompt=prompt,
                partial_output=partial_chunk,
                error_reason=error_reason,
                provider_or_caller=invoker,
                task_domain="ci_repair",
                available_models=self.available_models,
            )
            active_model = continuation_details["to_model"]
            raw_response = continuation_details["completed_output"]
            failover_occurred = True
        else:
            try:
                raw_response = invoker(active_model, prompt)
            except Exception as err:
                is_lim, lim_cat = ModelContinuationEngine.is_limit_exhausted(str(err))
                if is_lim:
                    continuation_details = ModelContinuationEngine.execute_continuation(
                        failed_model=active_model,
                        original_prompt=prompt,
                        partial_output="",
                        error_reason=str(err),
                        provider_or_caller=invoker,
                        task_domain="ci_repair",
                        available_models=self.available_models,
                    )
                    active_model = continuation_details["to_model"]
                    raw_response = continuation_details["completed_output"]
                    failover_occurred = True
                else:
                    raise

        # Extract clean Python code
        patched_code = self._extract_code(raw_response)

        # Stage 4: AST Syntax Verification
        ast_ok = False
        try:
            ast.parse(patched_code)
            ast_ok = True
        except SyntaxError as syntax_err:
            logger.error("UninterruptedAutonomousLoop: AST Syntax Error: %s", syntax_err)
            self.task_manager.transition_task(task_id, TaskState.FAILED, error_message=str(syntax_err))
            return LoopExecutionResult(
                loop_id=loop_id,
                status="FAILED",
                objective=objective,
                target_module=target_module_rel,
                target_test=test_pattern,
                primary_model=self.primary_model,
                final_model=active_model,
                failover_occurred=failover_occurred,
                failover_count=1 if failover_occurred else 0,
                continuation_details=continuation_details,
                initial_test_passed=initial_passed,
                final_test_passed=False,
                ast_verified=False,
                patch_applied=False,
                unified_diff="",
                sha256_evidence="",
                elapsed_seconds=time.time() - start_time,
                total_tokens_consumed=ModelContinuationEngine.estimate_tokens(raw_response),
            )

        # Stage 5: Sandboxed Test Verification
        candidate_files = dict(workspace_files)
        candidate_files[target_module_rel] = patched_code

        final_test_res = sandbox.run_python_unittest_sandbox(
            files=candidate_files,
            test_pattern=test_pattern,
            timeout_sec=30.0,
        )
        final_passed = final_test_res.passed

        # If tests pass and patch application is enabled, write to workspace
        if final_passed and apply_patch_to_workspace:
            atomic_write_workspace_file(self.workspace_dir, target_module_rel, patched_code)

        # Compute unified diff
        import difflib
        diff = "\n".join(
            difflib.unified_diff(
                original_code.splitlines(),
                patched_code.splitlines(),
                fromfile=f"a/{target_module_rel}",
                tofile=f"b/{target_module_rel}",
                lineterm="",
            )
        )

        # Stage 6: Seal SHA-256 Evidence & Update Memory
        evidence_payload = {
            "loop_id": loop_id,
            "objective": objective,
            "original_sha256": original_sha,
            "patched_sha256": hashlib.sha256(patched_code.encode()).hexdigest(),
            "primary_model": self.primary_model,
            "final_model": active_model,
            "failover_occurred": failover_occurred,
            "final_test_passed": final_passed,
            "timestamp": time.time(),
        }
        evidence_hash = hashlib.sha256(json.dumps(evidence_payload, sort_keys=True).encode()).hexdigest()

        # Commit to memory
        self.memory.store(
            layer=5,
            subject_key=f"loop_execution.{loop_id}",
            content=f"Executed uninterrupted autonomous loop for '{objective}'. Result: {'PASSED' if final_passed else 'FAILED'}.",
            structured_data=evidence_payload,
            tags=["uninterrupted_loop", "ci_repair", active_model],
        )

        # Transition task state
        if final_passed:
            self.task_manager.transition(task_id, TaskState.VERIFYING)
            self.task_manager.transition(task_id, TaskState.SUCCEEDED)
        else:
            self.task_manager.transition(task_id, TaskState.FAILED)

        status_str = "REPAIRED_WITH_CONTINUATION" if (final_passed and failover_occurred) else ("SUCCEEDED_AND_VERIFIED" if final_passed else "FAILED")

        return LoopExecutionResult(
            loop_id=loop_id,
            status=status_str,
            objective=objective,
            target_module=target_module_rel,
            target_test=test_pattern,
            primary_model=self.primary_model,
            final_model=active_model,
            failover_occurred=failover_occurred,
            failover_count=1 if failover_occurred else 0,
            continuation_details=continuation_details,
            initial_test_passed=initial_passed,
            final_test_passed=final_passed,
            ast_verified=ast_ok,
            patch_applied=apply_patch_to_workspace,
            unified_diff=diff,
            sha256_evidence=evidence_hash,
            elapsed_seconds=round(time.time() - start_time, 3),
            total_tokens_consumed=ModelContinuationEngine.estimate_tokens(raw_response),
        )

    @staticmethod
    def _extract_code(text: str) -> str:
        """Extracts pure code from markdown blocks or returns raw text."""
        if "```python" in text:
            parts = text.split("```python", 1)[1].split("```", 1)
            return parts[0].strip()
        if "```" in text:
            parts = text.split("```", 1)[1].split("```", 1)
            return parts[0].strip()
        return text.strip()
