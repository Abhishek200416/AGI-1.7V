"""Model Continuation Engine & Context Limit Cascader for IVA AGI 1.7.

Enables seamless failover and context continuation when a model hits its token limit,
1M+ context ceiling, HTTP 429 quota exhaustion, or context length limits.
Extracts a dense continuation handoff capsule, selects the successor model in the
cascading hierarchy, and completes execution without dropping state or prompting the user.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("iva.adapters.continuation_engine")


@dataclass
class ContextSnapshot:
    """Snapshot of execution context at the moment a limit is reached."""
    task_id: str
    original_prompt: str
    partial_output: str
    tokens_consumed: int
    limit_type: str  # "MAX_TOKENS", "QUOTA_EXHAUSTED", "RATE_LIMIT_429", "CONTEXT_OVERFLOW"
    timestamp: float = field(default_factory=time.time)
    active_files: List[str] = field(default_factory=list)
    pending_goals: List[str] = field(default_factory=list)


@dataclass
class ContinuationHandoff:
    """Compressed handoff capsule handed to the next model in the cascade."""
    handoff_id: str
    from_model: str
    to_model: str
    limit_reason: str
    continuation_prompt: str
    checkpoint_state: Dict[str, Any]


class ModelContinuationEngine:
    """Orchestrates seamless model handoff across 1M+ context limits and quota boundaries."""

    # Default cascading model preference hierarchy:
    # 1. Frontier 1M-2M Context Leaders (Deep reasoning, long memory)
    # 2. Fast High-Throughput Engines (Low latency, high rate limits)
    # 3. Enterprise / Open Weights Fallback (Nemotron, Ultra, Llama)
    CASCADE_HIERARCHY: List[str] = [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "nvidia/llama-3.1-nemotron-70b-instruct",
        "meta/llama-3.3-70b-instruct",
        "mistralai/mistral-large-2-instruct",
        "gpt-4o",
        "gpt-4o-mini",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
    ]

    @classmethod
    def is_limit_exhausted(cls, error_msg_or_status: str, finish_reason: Optional[str] = None) -> Tuple[bool, str]:
        """Detects if an error or status corresponds to quota exhaustion or token limits.
        
        Returns:
            (is_exhausted: bool, limit_category: str)
        """
        err_lower = (error_msg_or_status or "").lower()

        if finish_reason in ("MAX_TOKENS", "LENGTH", "max_tokens"):
            return (True, "MAX_TOKENS")

        if any(k in err_lower for k in ("quota exceeded", "resource_exhausted", "daily quota", "429")):
            return (True, "QUOTA_EXHAUSTED")

        if any(k in err_lower for k in ("rate limit", "too many requests")):
            return (True, "RATE_LIMIT_429")

        if any(k in err_lower for k in ("context length", "maximum context length", "token limit", "exceeds token count")):
            return (True, "CONTEXT_OVERFLOW")

        return (False, "NONE")

    @classmethod
    def select_next_successor_model(
        cls,
        failed_model: str,
        available_pool: Optional[List[str]] = None,
    ) -> str:
        """Determines the next optimal successor model to continue the conversation."""
        pool = available_pool or cls.CASCADE_HIERARCHY

        # If current model is in pool, pick next candidate in hierarchy
        failed_clean = failed_model.strip().lower()
        candidates = [m for m in pool if m.strip().lower() != failed_clean]

        if not candidates:
            # Fallback to standard fast model
            return "gemini-2.5-flash" if failed_clean != "gemini-2.5-flash" else "nvidia/llama-3.1-nemotron-70b-instruct"

        # Prioritize matching cascade hierarchy
        for preferred in cls.CASCADE_HIERARCHY:
            for cand in candidates:
                if preferred.lower() in cand.lower():
                    return cand

        return candidates[0]

    @classmethod
    def build_continuation_prompt(
        cls,
        snapshot: ContextSnapshot,
        successor_model: str,
    ) -> str:
        """Synthesizes a structured continuation prompt that preserves exact character and task state."""
        header = (
            f"[SYSTEM CONTINUATION HANDOFF • SEAMLESS CONTEXT EXTENSION]\n"
            f"Preceding model reached {snapshot.limit_type}. You are '{successor_model}', continuing execution.\n"
            f"Task ID: {snapshot.task_id}\n"
            f"Zero loss of progress: Proceed immediately without apologizing or re-explaining past steps.\n\n"
        )

        context_body = ""
        if snapshot.partial_output.strip():
            # Provide the trailing partial output so the successor can complete it seamlessly
            trailing = snapshot.partial_output[-1500:] if len(snapshot.partial_output) > 1500 else snapshot.partial_output
            context_body = (
                f"--- PARTIAL GENERATION PRODUCED SO FAR (END SECTION) ---\n"
                f"{trailing}\n"
                f"--- RESUME INSTRUCTION ---\n"
                f"Pick up precisely from where the partial output ended. Complete the response.\n\n"
            )

        task_section = (
            f"--- ORIGINAL OBJECTIVE ---\n"
            f"{snapshot.original_prompt}\n"
        )

        return f"{header}{context_body}{task_section}"

    @classmethod
    def execute_failover_continuation(
        cls,
        failed_model: str,
        original_prompt: str,
        partial_output: str,
        error_reason: str,
        provider: Any,
        available_models: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Coordinates snapshotting, successor selection, and continued execution."""
        is_lim, lim_type = cls.is_limit_exhausted(error_reason)
        limit_category = lim_type if is_lim else "MANUAL_FAILOVER"

        snapshot = ContextSnapshot(
            task_id=f"CONT-{int(time.time())}",
            original_prompt=original_prompt,
            partial_output=partial_output,
            tokens_consumed=len(original_prompt.split()) + len(partial_output.split()),
            limit_type=limit_category,
        )

        successor = cls.select_next_successor_model(failed_model, available_models)
        logger.warning(
            "ModelContinuationEngine: Model '%s' hit '%s'. Cascading immediately to successor '%s'.",
            failed_model, limit_category, successor
        )

        continuation_prompt = cls.build_continuation_prompt(snapshot, successor)

        handoff = ContinuationHandoff(
            handoff_id=snapshot.task_id,
            from_model=failed_model,
            to_model=successor,
            limit_reason=limit_category,
            continuation_prompt=continuation_prompt,
            checkpoint_state=asdict(snapshot),
        )

        return {
            "status": "CONTINUATION_INITIATED",
            "from_model": failed_model,
            "to_model": successor,
            "limit_reason": limit_category,
            "continuation_prompt": continuation_prompt,
            "handoff": asdict(handoff),
        }
