"""Adaptive Ambiguity Evaluator & Strategic Fork Protocol.
================================================================================
AGI 1.7 / IVA Autonomous Capability Module

Implements the "Ask When Serious" Protocol:
1. Routine execution steps (creating files, running tests, applying AST patches)
   run autonomously with ZERO baby-sitting.
2. When a prompt presents a genuinely serious architectural dilemma, destructive
   operation risk, or mutually exclusive technical path (ambiguity >= 0.70), IVA
   triggers a structured Strategic Fork.
3. The Strategic Fork clearly explains the trade-off and presents 2-3 concrete
   options with a (Recommended) default, allowing the operator to steer with a
   single keypress or proceed with the recommended path.

Requires ZERO external PyPI dependencies (100% Python standard library).
================================================================================
"""

from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


class AmbiguityDimension(str, enum.Enum):
    ARCHITECTURAL_FORK = "ARCHITECTURAL_FORK"
    DESTRUCTIVE_RISK = "DESTRUCTIVE_RISK"
    CONFLICTING_CONSTRAINTS = "CONFLICTING_CONSTRAINTS"
    DOMAIN_AUTH_GAP = "DOMAIN_AUTH_GAP"


@dataclass
class StrategicOption:
    option_id: str
    label: str
    description: str
    is_recommended: bool = False


@dataclass
class StrategicFork:
    fork_id: str
    question: str
    tradeoff_rationale: str
    options: List[StrategicOption] = field(default_factory=list)
    default_option_id: str = "1"

    def format_interactive_prompt(self) -> str:
        """Formats the strategic fork for display in the interactive terminal."""
        lines = [
            f"\n   🤔 ARCHITECTURAL STRATEGIC FORK: {self.question}",
            f"   Rationale: {self.tradeoff_rationale}\n",
        ]
        for opt in self.options:
            rec_tag = " ★ (Recommended)" if opt.is_recommended else ""
            lines.append(f"   [{opt.option_id}] {opt.label}{rec_tag}")
            lines.append(f"       • {opt.description}")
        lines.append(f"\n   Choose option [1-{len(self.options)}, default: {self.default_option_id}]: ")
        return "\n".join(lines)


@dataclass
class AmbiguityAssessment:
    ambiguity_score: float  # 0.0 (crystal clear) to 1.0 (deeply ambiguous/serious)
    is_serious: bool  # True if ambiguity_score >= 0.70
    primary_dimension: Optional[AmbiguityDimension] = None
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    fork: Optional[StrategicFork] = None


class AdaptiveAmbiguityEvaluator:
    """Evaluates whether an incoming task requires autonomous sprint or a Strategic Fork."""

    SERIOUS_THRESHOLD = 0.70

    # Pattern triggers for serious forks
    DESTRUCTIVE_PATTERNS = [
        re.compile(r"\b(delete|drop|wipe|purge|remove all|clean reset|destroy|overwrite all)\b", re.IGNORECASE),
        re.compile(r"\b(rm -rf|del /f|drop table|format drive)\b", re.IGNORECASE),
    ]

    ARCHITECTURAL_FORK_PATTERNS = [
        (
            re.compile(r"\b(three\.js|webgl)\b.*\b(2d canvas|pure css|svg)\b|\b(2d canvas|pure css|svg)\b.*\b(three\.js|webgl)\b", re.IGNORECASE),
            "Rendering Engine Dilemma",
            "3D spatial WebGL vs lightweight 2D DOM",
            [
                StrategicOption("1", "High-Performance Three.js WebGL", "Spatial 3D depth, particle starfields, dynamic camera rigging (modern big-tech look).", is_recommended=True),
                StrategicOption("2", "Ultra-Lightweight 2D Canvas & CSS", "Zero WebGL overhead, instant 60fps rendering, sub-10ms first paint.", is_recommended=False),
            ],
        ),
        (
            re.compile(r"\b(sqlite|wal)\b.*\b(postgres|mongodb|mysql)\b|\b(postgres|mongodb|mysql)\b.*\b(sqlite|wal)\b", re.IGNORECASE),
            "Database Persistence Strategy",
            "Embedded zero-dependency SQLite WAL vs external database server",
            [
                StrategicOption("1", "Embedded SQLite WAL (Zero-Dependency)", "Native Python standard library, instant local persistence, zero Docker required.", is_recommended=True),
                StrategicOption("2", "External PostgreSQL / Client Connection", "High-concurrency multi-user database server (requires DB credentials).", is_recommended=False),
            ],
        ),
        (
            re.compile(r"\b(vanilla|pure stdlib)\b.*\b(react|vue|next\.js|angular)\b|\b(react|vue|next\.js|angular)\b.*\b(vanilla|pure stdlib)\b", re.IGNORECASE),
            "Frontend Framework Architecture",
            "Zero-build Vanilla Web Components vs Node.js React/Next.js toolchain",
            [
                StrategicOption("1", "Zero-Build Vanilla HTML5/ES6+", "Runs out of the box in any browser without npm, node_modules, or Webpack build pipelines.", is_recommended=True),
                StrategicOption("2", "Modern React/Next.js Architecture", "Component-driven framework ecosystem (requires Node.js & npm toolchain).", is_recommended=False),
            ],
        ),
    ]

    CONFLICTING_CONSTRAINTS = [
        re.compile(r"\b(zero dependency|no dependencies|stdlib only)\b.*\b(install|pip|npm|docker)\b", re.IGNORECASE),
        re.compile(r"\b(completely offline|no network|air-gapped)\b.*\b(scrape|crawl|fetch|api)\b", re.IGNORECASE),
    ]

    @classmethod
    def evaluate(
        cls,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AmbiguityAssessment:
        """Evaluates whether the prompt presents serious ambiguity requiring a strategic fork."""
        p_clean = prompt.strip()
        if not p_clean:
            return AmbiguityAssessment(ambiguity_score=0.0, is_serious=False)

        scores: Dict[str, float] = {
            AmbiguityDimension.DESTRUCTIVE_RISK.value: 0.0,
            AmbiguityDimension.ARCHITECTURAL_FORK.value: 0.0,
            AmbiguityDimension.CONFLICTING_CONSTRAINTS.value: 0.0,
            AmbiguityDimension.DOMAIN_AUTH_GAP.value: 0.0,
        }

        # Check Destructive Risk
        for pat in cls.DESTRUCTIVE_PATTERNS:
            if pat.search(p_clean):
                scores[AmbiguityDimension.DESTRUCTIVE_RISK.value] = 0.85
                fork = StrategicFork(
                    fork_id="destructive_risk_gate",
                    question="Confirm Potentially Irreversible or Destructive Operation",
                    tradeoff_rationale="The requested operation matches destructive patterns that could delete files, drop tables, or overwrite code.",
                    options=[
                        StrategicOption("1", "Safe Non-Destructive Dry Run & Backup", "Simulate changes, preview diffs, and create safety rollback archive first.", is_recommended=True),
                        StrategicOption("2", "Execute Destructive Change Directly", "Apply irreversible deletions/overwrites immediately without dry-run.", is_recommended=False),
                        StrategicOption("3", "Cancel Operation", "Abort the command and keep existing files untouched.", is_recommended=False),
                    ],
                    default_option_id="1",
                )
                return AmbiguityAssessment(
                    ambiguity_score=0.85,
                    is_serious=True,
                    primary_dimension=AmbiguityDimension.DESTRUCTIVE_RISK,
                    dimension_scores=scores,
                    fork=fork,
                )

        # Check Architectural Forks
        for pat, title, rationale, options in cls.ARCHITECTURAL_FORK_PATTERNS:
            if pat.search(p_clean):
                scores[AmbiguityDimension.ARCHITECTURAL_FORK.value] = 0.80
                fork = StrategicFork(
                    fork_id="arch_fork_" + title.lower().replace(" ", "_"),
                    question=title,
                    tradeoff_rationale=rationale,
                    options=options,
                    default_option_id="1",
                )
                return AmbiguityAssessment(
                    ambiguity_score=0.80,
                    is_serious=True,
                    primary_dimension=AmbiguityDimension.ARCHITECTURAL_FORK,
                    dimension_scores=scores,
                    fork=fork,
                )

        # Check Conflicting Constraints
        for pat in cls.CONFLICTING_CONSTRAINTS:
            if pat.search(p_clean):
                scores[AmbiguityDimension.CONFLICTING_CONSTRAINTS.value] = 0.75
                fork = StrategicFork(
                    fork_id="conflicting_constraints_resolution",
                    question="Mutually Conflicting Constraints Detected",
                    tradeoff_rationale="Prompt specifies contradictory constraints (e.g. strict zero-dependency vs external npm/pip requirement).",
                    options=[
                        StrategicOption("1", "Standard Library Zero-Dependency Mode", "Adhere strictly to zero external dependencies; build with native Python/HTML/JS.", is_recommended=True),
                        StrategicOption("2", "Permit External Packages", "Authorize pulling 3rd-party dependencies via pip/npm.", is_recommended=False),
                    ],
                    default_option_id="1",
                )
                return AmbiguityAssessment(
                    ambiguity_score=0.75,
                    is_serious=True,
                    primary_dimension=AmbiguityDimension.CONFLICTING_CONSTRAINTS,
                    dimension_scores=scores,
                    fork=fork,
                )

        # Routine task -> autonomous sprint with zero baby-sitting
        max_score = max(scores.values()) if scores else 0.0
        return AmbiguityAssessment(
            ambiguity_score=max_score,
            is_serious=max_score >= cls.SERIOUS_THRESHOLD,
            dimension_scores=scores,
            fork=None,
        )
