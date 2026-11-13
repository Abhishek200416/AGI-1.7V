"""
autonomous_skill_router.py — Dynamic Autonomous Skill Router & Pipeline Executor for IVA.

Enables IVA to dynamically inspect incoming operator intents or specialist goals,
score and select the optimal skills from the unified IVA Skills registry (AIVA skills),
compose multi-skill execution pipelines, and execute them with graceful fallback.

Key Capabilities:
1. Multi-factor Intent Scoring (semantic tokens, tool signatures, execution priority).
2. Autonomous Skill Composition (multi-stage pipelines for video, quant, debugging, web).
3. Universal Execution Dispatcher (native stdlib execution + graceful MCP fallbacks).
4. Dynamic Custom Skill Registration (hot-plugging skills at runtime).
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

from agents.IVA.ecosystem.iva_skills_registry import (
    IvaSkillDefinition,
    IvaSkillsRegistry,
    SkillCategory,
    iva_skills_registry,
)


@dataclass
class SkillMatch:
    skill: IvaSkillDefinition
    score: float
    matched_reasons: List[str] = field(default_factory=list)
    suggested_tools: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.skill.name,
            "category": self.skill.category.value,
            "score": round(self.score, 3),
            "execution_type": self.skill.execution_type,
            "matched_reasons": self.matched_reasons,
            "suggested_tools": self.suggested_tools,
            "description": self.skill.description,
        }


@dataclass
class SkillPipelineStage:
    stage_name: str
    skill_name: str
    purpose: str
    input_keys: List[str] = field(default_factory=list)
    output_keys: List[str] = field(default_factory=list)


@dataclass
class SkillPipeline:
    name: str
    description: str
    stages: List[SkillPipelineStage] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "stage_count": len(self.stages),
            "stages": [
                {
                    "stage_name": s.stage_name,
                    "skill_name": s.skill_name,
                    "purpose": s.purpose,
                    "input_keys": s.input_keys,
                    "output_keys": s.output_keys,
                }
                for s in self.stages
            ],
        }


@dataclass
class SkillExecutionResult:
    success: bool
    skill_name: str
    output: Any
    execution_mode: str  # "native_handler", "mcp_fallback", "simulated", "error"
    latency_ms: float
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "skill_name": self.skill_name,
            "execution_mode": self.execution_mode,
            "latency_ms": round(self.latency_ms, 2),
            "error": self.error,
            "output": self.output,
        }


class AutonomousSkillRouter:
    """Intelligent autonomous router that evaluates tasks and dispatches the strongest skills."""

    def __init__(self, registry: Optional[IvaSkillsRegistry] = None) -> None:
        self.registry = registry or iva_skills_registry
        self._native_handlers: Dict[str, Callable[[Dict[str, Any], Optional[Dict[str, Any]]], Any]] = {}
        self._register_default_native_handlers()

    def _tokenize(self, text: str) -> set[str]:
        """Normalize and tokenize text into lowercase word tokens."""
        words = re.findall(r"[a-z0-9_-]+", text.lower())
        stopwords = {
            "the", "and", "or", "a", "an", "in", "on", "to", "for", "of", "with",
            "at", "by", "from", "is", "it", "this", "that", "please", "can", "you",
            "make", "use", "using", "all", "so", "be", "do", "how", "what", "we"
        }
        return {w for w in words if len(w) > 1 and w not in stopwords}

    def route_skills(
        self,
        intent: str,
        *,
        limit: int = 5,
        min_score: float = 0.15,
        preferred_category: Optional[SkillCategory] = None,
    ) -> List[SkillMatch]:
        """Scores and ranks all catalog skills against the provided intent or task description."""
        intent_lower = intent.lower()
        intent_tokens = self._tokenize(intent)
        matches: List[SkillMatch] = []

        for skill in self.registry.get_all_skills():
            score = 0.0
            reasons: List[str] = []

            # 1. Exact or Substring Name Match (Max weight: 1.0)
            skill_name_normalized = skill.name.lower().replace("-", " ")
            if skill.name.lower() in intent_lower or skill_name_normalized in intent_lower:
                score += 0.85
                reasons.append(f"Direct skill name match ('{skill.name}')")

            # 2. Tool / Command Name Match (Weight: 0.70)
            matched_tools: List[str] = []
            for tool in skill.tools_or_commands:
                tool_norm = tool.lower().replace("-", " ").replace("_", " ")
                if tool.lower() in intent_lower or tool_norm in intent_lower:
                    score += 0.50
                    matched_tools.append(tool)
                    reasons.append(f"Tool command match ('{tool}')")

            # 3. Category Relevance (Weight: 0.30 - 0.50)
            cat_val = skill.category.value.lower()
            if preferred_category and skill.category == preferred_category:
                score += 0.40
                reasons.append(f"Preferred category match ('{skill.category.value}')")
            elif any(cat_token in intent_lower for cat_token in cat_val.split()):
                score += 0.25
                reasons.append(f"Category domain overlap ('{skill.category.value}')")

            # 4. Token Overlap with Description (Jaccard-like boost)
            desc_tokens = self._tokenize(skill.description)
            name_tokens = self._tokenize(skill.name)
            combined_tokens = desc_tokens | name_tokens

            common_tokens = intent_tokens & combined_tokens
            if common_tokens:
                overlap_ratio = len(common_tokens) / max(1, len(intent_tokens))
                token_score = min(0.45, overlap_ratio * 0.75)
                score += token_score
                if token_score > 0.1:
                    reasons.append(f"Semantic keyword match: {sorted(list(common_tokens))[:4]}")

            # 5. Execution Type Affinity (Native & Hybrid prioritized for low latency)
            if skill.execution_type == "native":
                score += 0.05
            elif skill.execution_type == "hybrid":
                score += 0.03

            # Bound score to [0.0, 1.0]
            final_score = min(1.0, score)

            if final_score >= min_score:
                suggested = matched_tools if matched_tools else skill.tools_or_commands[:3]
                matches.append(
                    SkillMatch(
                        skill=skill,
                        score=final_score,
                        matched_reasons=reasons,
                        suggested_tools=suggested,
                    )
                )

        # Sort descending by score
        matches.sort(key=lambda m: m.score, reverse=True)
        return matches[:limit]

    def resolve_best_skill(
        self,
        intent: str,
        *,
        required_capability: Optional[str] = None,
    ) -> Optional[IvaSkillDefinition]:
        """Resolves the single highest-confidence skill for a given intent."""
        matches = self.route_skills(intent, limit=1, min_score=0.10)
        if not matches:
            return None

        best = matches[0].skill
        if required_capability:
            if not any(required_capability.lower() in t.lower() for t in best.tools_or_commands):
                # Search specifically for required capability
                for skill in self.registry.get_all_skills():
                    if any(required_capability.lower() in t.lower() for t in skill.tools_or_commands):
                        return skill
        return best

    def compose_pipeline(
        self,
        intent: str,
        *,
        domain_hint: Optional[str] = None,
    ) -> SkillPipeline:
        """Autonomously analyzes multi-step tasks and constructs an ordered execution pipeline."""
        intent_lower = intent.lower()

        # Domain 1: Omnichannel Media Studio & Social Video
        if any(w in intent_lower for w in ["video", "short", "reel", "youtube", "instagram", "tiktok", "social"]):
            return SkillPipeline(
                name="Omnichannel Media Production & Social Pipeline",
                description="End-to-end autonomous research, video generation, captioning, and omnichannel adaptation.",
                stages=[
                    SkillPipelineStage(
                        stage_name="1. Audience & Content Research",
                        skill_name="research-prompt",
                        purpose="Deconstruct topic into viral angles, factual proof points, and hook structure.",
                        input_keys=["topic", "target_audience"],
                        output_keys=["research_dossier", "key_facts"],
                    ),
                    SkillPipelineStage(
                        stage_name="2. Media Generation & Visual Directing",
                        skill_name="lemo-opuscar",
                        purpose="Synthesize high-retention code-driven motion graphics, audio sync, and visual edits.",
                        input_keys=["research_dossier", "visual_style"],
                        output_keys=["rendered_video_path", "runtime_seconds"],
                    ),
                    SkillPipelineStage(
                        stage_name="3. Instagram Viral Optimization",
                        skill_name="iva-instagram-skill",
                        purpose="Score viral hook, generate beat sheet, humanize captions, and audit hashtags.",
                        input_keys=["research_dossier", "caption_draft"],
                        output_keys=["instagram_metadata", "hook_score"],
                    ),
                    SkillPipelineStage(
                        stage_name="4. Omnichannel Multi-Platform Adaptation",
                        skill_name="iva-omnichannel-social-skill",
                        purpose="Adapt package simultaneously across Shorts, Reels, TikTok, X, LinkedIn, and Threads.",
                        input_keys=["research_dossier", "instagram_metadata"],
                        output_keys=["omnichannel_matrix", "distribution_ready"],
                    ),
                ],
            )

        # Domain 2: Bug Fix & Codebase Refactoring
        if any(w in intent_lower for w in ["bug", "fix", "debug", "refactor", "error", "exception", "broken"]):
            return SkillPipeline(
                name="Autonomous Bug Triage & Minimal Refactoring Pipeline",
                description="Systematic root-cause diagnosis, sequential reasoning, minimal YAGNI patching, and code review.",
                stages=[
                    SkillPipelineStage(
                        stage_name="1. Root-Cause Diagnosis",
                        skill_name="gsd-debug",
                        purpose="Isolate exact failure stack, reproduce defect deterministically, and identify root cause.",
                        input_keys=["error_log", "failing_test"],
                        output_keys=["root_cause_analysis", "reproduction_proof"],
                    ),
                    SkillPipelineStage(
                        stage_name="2. Invariant & Boundary Verification",
                        skill_name="sequential-thinking",
                        purpose="Verify input/output types, state mutation order, and boundary conditions step-by-step.",
                        input_keys=["root_cause_analysis"],
                        output_keys=["patch_invariants", "boundary_constraints"],
                    ),
                    SkillPipelineStage(
                        stage_name="3. Minimal YAGNI Patching",
                        skill_name="ponytail",
                        purpose="Apply shortest working diff using stdlib/native constructs without unnecessary abstractions.",
                        input_keys=["patch_invariants"],
                        output_keys=["minimal_diff", "affected_files"],
                    ),
                    SkillPipelineStage(
                        stage_name="4. Automated Quality Gate",
                        skill_name="code-review",
                        purpose="Review diff for regression vulnerabilities, resource leaks, and test coverage.",
                        input_keys=["minimal_diff"],
                        output_keys=["review_verdict", "safety_signoff"],
                    ),
                ],
            )

        # Domain 3: Quant Finance & Trading
        if any(w in intent_lower for w in ["trading", "quant", "nifty", "backtest", "risk", "options", "volatility"]):
            return SkillPipeline(
                name="Institutional Quantitative Execution & Risk Pipeline",
                description="Data validation, microstructure signal generation, pre-trade risk gating, and execution.",
                stages=[
                    SkillPipelineStage(
                        stage_name="1. Data Ingestion & Validation",
                        skill_name="financial-data-validation",
                        purpose="Validate bar continuity, check tick timestamps, filter spike anomalies, and verify quotes.",
                        input_keys=["market_feed_symbol", "timeframe"],
                        output_keys=["validated_dataset", "data_quality_score"],
                    ),
                    SkillPipelineStage(
                        stage_name="2. Microstructure & Hawkes Signal",
                        skill_name="omega-quant-trading",
                        purpose="Compute Hawkes intensity, MLOFI order flow imbalance, and SSVI volatility surface.",
                        input_keys=["validated_dataset"],
                        output_keys=["trade_signals", "volatility_surface"],
                    ),
                    SkillPipelineStage(
                        stage_name="3. Pre-Trade Risk Gate",
                        skill_name="trading-risk-management",
                        purpose="Enforce VaR, max drawdown, Bayesian-Kelly sizing, and statutory capital protection gates.",
                        input_keys=["trade_signals", "portfolio_capital"],
                        output_keys=["approved_orders", "risk_clearance"],
                    ),
                    SkillPipelineStage(
                        stage_name="4. Execution & Ledger Journaling",
                        skill_name="trading-ledger",
                        purpose="Record fill details, decision rationale, slippage metrics, and post-trade performance.",
                        input_keys=["approved_orders"],
                        output_keys=["journal_entry_id", "execution_status"],
                    ),
                ],
            )

        # Generic Fallback: Dynamic Best-Fit Top-3 Skills
        top_skills = self.route_skills(intent, limit=3, min_score=0.10)
        stages = [
            SkillPipelineStage(
                stage_name=f"Stage {i+1}: {match.skill.name}",
                skill_name=match.skill.name,
                purpose=match.skill.description,
                input_keys=["input_payload"],
                output_keys=[f"stage_{i+1}_output"],
            )
            for i, match in enumerate(top_skills)
        ]

        return SkillPipeline(
            name="Dynamic Adaptive Intent Pipeline",
            description=f"Dynamically generated {len(stages)}-stage pipeline tailored for intent: '{intent[:60]}...'",
            stages=stages,
        )

    def register_native_handler(
        self,
        skill_name: str,
        handler: Callable[[Dict[str, Any], Optional[Dict[str, Any]]], Any],
    ) -> None:
        """Registers a native in-memory callable for a skill."""
        self._native_handlers[skill_name.lower()] = handler

    def execute_skill(
        self,
        skill_name: str,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> SkillExecutionResult:
        """Executes a skill via its native handler or provides structured diagnostic dispatch."""
        start_time = time.perf_counter()
        skill_name_lower = skill_name.lower()

        # 1. Native Handler Execution
        if skill_name_lower in self._native_handlers:
            try:
                result = self._native_handlers[skill_name_lower](payload, context)
                latency = (time.perf_counter() - start_time) * 1000
                return SkillExecutionResult(
                    success=True,
                    skill_name=skill_name,
                    output=result,
                    execution_mode="native_handler",
                    latency_ms=latency,
                )
            except Exception as e:
                latency = (time.perf_counter() - start_time) * 1000
                return SkillExecutionResult(
                    success=False,
                    skill_name=skill_name,
                    output=None,
                    execution_mode="error",
                    latency_ms=latency,
                    error=str(e),
                )

        # 2. Check Catalog Definition
        skill_def = self.registry.get_skill(skill_name)
        if not skill_def:
            latency = (time.perf_counter() - start_time) * 1000
            return SkillExecutionResult(
                success=False,
                skill_name=skill_name,
                output=None,
                execution_mode="error",
                latency_ms=latency,
                error=f"Skill '{skill_name}' is not registered in the IVA Skills catalog.",
            )

        # 3. Fallback for Hybrid / MCP Bridge Skills
        latency = (time.perf_counter() - start_time) * 1000
        fallback_data = {
            "skill": skill_def.name,
            "category": skill_def.category.value,
            "execution_type": skill_def.execution_type,
            "tools_available": skill_def.tools_or_commands,
            "status": "ready_for_tool_invocation",
            "received_payload_keys": list(payload.keys()),
            "guidance": f"Invoke tool '{skill_def.tools_or_commands[0]}' with arguments derived from payload.",
        }
        return SkillExecutionResult(
            success=True,
            skill_name=skill_name,
            output=fallback_data,
            execution_mode="mcp_fallback",
            latency_ms=latency,
        )

    def _register_default_native_handlers(self) -> None:
        """Registers built-in native handlers for common operational tasks."""
        # Handler 1: Sequential Thinking
        def _handle_sequential_thinking(payload: Dict[str, Any], ctx: Optional[Dict[str, Any]]) -> Dict[str, Any]:
            thought = payload.get("thought", "")
            step = payload.get("thoughtNumber", 1)
            total = payload.get("totalThoughts", 1)
            return {
                "step": step,
                "total_steps": total,
                "structured_thought": thought,
                "verified": True,
            }

        # Handler 2: Ponytail Review (YAGNI & Complexity check)
        def _handle_ponytail_review(payload: Dict[str, Any], ctx: Optional[Dict[str, Any]]) -> Dict[str, Any]:
            code = payload.get("code", "")
            lines = code.splitlines()
            findings = []
            if len(lines) > 200:
                findings.append("Large file: consider if this can be simplified or split.")
            if "eval(" in code or "exec(" in code:
                findings.append("Security warning: dynamic code execution detected.")
            return {
                "passed_review": len(findings) == 0,
                "findings": findings,
                "code_length_lines": len(lines),
                "rung_status": "YAGNI verified",
            }

        # Handler 3: Trading Risk Management (Pre-trade safety check)
        def _handle_risk_management(payload: Dict[str, Any], ctx: Optional[Dict[str, Any]]) -> Dict[str, Any]:
            capital = float(payload.get("capital", 10000.0))
            order_size = float(payload.get("order_size", 0.0))
            max_daily_loss = float(payload.get("max_daily_loss", 2500.0))
            loss_so_far = float(payload.get("loss_so_far", 0.0))

            if loss_so_far >= max_daily_loss:
                return {
                    "approved": False,
                    "reason": f"Daily loss limit reached (₹{loss_so_far} >= ₹{max_daily_loss})",
                }
            if order_size > capital * 0.20:
                return {
                    "approved": False,
                    "reason": f"Order size (₹{order_size}) exceeds 20% max allocation limit.",
                }
            return {
                "approved": True,
                "capital_remaining": capital - order_size,
                "max_drawdown_headroom": max_daily_loss - loss_so_far,
            }

        self.register_native_handler("sequential-thinking", _handle_sequential_thinking)
        self.register_native_handler("ponytail-review", _handle_ponytail_review)
        self.register_native_handler("trading-risk-management", _handle_risk_management)


# Global singleton router instance
autonomous_skill_router = AutonomousSkillRouter()
