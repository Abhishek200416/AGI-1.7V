"""IVA Autonomous Research Partner & Architectural Design Synthesis Engine.
================================================================================
Empowers IVA to operate as an elite research, systems architecture, and design partner:
1. Reconfigurable Architectural Scopes (Frontend-Only, Bug-Fixing CI, Full-Stack App, Enterprise System).
2. Upfront Adaptive Intake Protocol: clarifies ambiguities at the start, then runs end-to-end
   with zero mid-turn interruptions.
3. Anti-Cliché Design Synthesis: generates distinct, professional aesthetic systems rather than
   repetitive generic templates (Cyber-Terminal, Warm Minimalist, Brutalist FinTech, Neo-Glass SaaS).
4. Generates formal specifications: DESIGN_SPEC.md, ARCH_SPEC.md, COMPONENT_TREE.md.

Requires ZERO external PyPI dependencies (100% Python standard library).
================================================================================
"""

from __future__ import annotations

import enum
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("ResearchPartnerEngine")


class ArchitecturalScope(str, enum.Enum):
    FRONTEND_ONLY = "FRONTEND_ONLY"
    BUG_DETECTION_CI = "BUG_DETECTION_CI"
    FULL_STACK_APP = "FULL_STACK_APP"
    ENTERPRISE_SYSTEM = "ENTERPRISE_SYSTEM"


class DesignAestheticTheme(str, enum.Enum):
    CYBER_TERMINAL = "CYBER_TERMINAL"
    WARM_MINIMALIST = "WARM_MINIMALIST"
    BRUTALIST_FINTECH = "BRUTALIST_FINTECH"
    NEO_GLASS_SAAS = "NEO_GLASS_SAAS"
    SWISS_INTERNATIONAL = "SWISS_INTERNATIONAL"


@dataclass
class DesignSystemTokens:
    theme_name: str
    bg_primary: str
    bg_surface: str
    accent_primary: str
    accent_secondary: str
    text_primary: str
    text_secondary: str
    border_color: str
    font_heading: str
    font_body: str
    font_code: str
    border_radius: str
    aesthetic_rationale: str

    def to_css_variables(self) -> str:
        return (
            f":root {{\n"
            f"  --bg-primary: {self.bg_primary};\n"
            f"  --bg-surface: {self.bg_surface};\n"
            f"  --accent-primary: {self.accent_primary};\n"
            f"  --accent-secondary: {self.accent_secondary};\n"
            f"  --text-primary: {self.text_primary};\n"
            f"  --text-secondary: {self.text_secondary};\n"
            f"  --border-color: {self.border_color};\n"
            f"  --font-heading: {self.font_heading};\n"
            f"  --font-body: {self.font_body};\n"
            f"  --font-code: {self.font_code};\n"
            f"  --radius: {self.border_radius};\n"
            f"}}"
        )


@dataclass
class UpfrontQuestion:
    question_id: str
    prompt: str
    options: List[str]
    default_option: str
    context: str


@dataclass
class ArchitecturalPlan:
    project_name: str
    scope: ArchitecturalScope
    aesthetic_theme: DesignAestheticTheme
    design_tokens: DesignSystemTokens
    directory_structure: List[str]
    key_modules: List[str]
    testing_strategy: str
    verification_criteria: List[str]


class ResearchPartnerEngine:
    """Orchestrates scientific research, upfront requirements intake, and bespoke architectural design."""

    DESIGN_PALETTES: Dict[DesignAestheticTheme, DesignSystemTokens] = {
        DesignAestheticTheme.CYBER_TERMINAL: DesignSystemTokens(
            theme_name="Cyber-Terminal",
            bg_primary="#050811",
            bg_surface="rgba(11, 19, 38, 0.75)",
            accent_primary="#00f0ff",
            accent_secondary="#10b981",
            text_primary="#f8fafc",
            text_secondary="#94a3b8",
            border_color="rgba(0, 240, 255, 0.2)",
            font_heading="'JetBrains Mono', monospace",
            font_body="'Inter', sans-serif",
            font_code="'JetBrains Mono', monospace",
            border_radius="10px",
            aesthetic_rationale="Precision technical computing aesthetic for developer tools, quant models, and terminal platforms.",
        ),
        DesignAestheticTheme.WARM_MINIMALIST: DesignSystemTokens(
            theme_name="Warm Minimalist",
            bg_primary="#fafaf9",
            bg_surface="#ffffff",
            accent_primary="#18181b",
            accent_secondary="#d97706",
            text_primary="#18181b",
            text_secondary="#71717a",
            border_color="#e4e4e7",
            font_heading="'Newsreader', 'Georgia', serif",
            font_body="'Inter', sans-serif",
            font_code="'JetBrains Mono', monospace",
            border_radius="6px",
            aesthetic_rationale="Humanist editorial balance tailored for publishing, research dossiers, and calm productivity.",
        ),
        DesignAestheticTheme.BRUTALIST_FINTECH: DesignSystemTokens(
            theme_name="Brutalist FinTech",
            bg_primary="#000000",
            bg_surface="#111111",
            accent_primary="#facc15",
            accent_secondary="#ef4444",
            text_primary="#ffffff",
            text_secondary="#a3a3a3",
            border_color="#262626",
            font_heading="'Space Grotesk', sans-serif",
            font_body="'Inter', sans-serif",
            font_code="'JetBrains Mono', monospace",
            border_radius="0px",
            aesthetic_rationale="High-contrast, zero-fluff data density for trading desks, risk managers, and market infrastructure.",
        ),
        DesignAestheticTheme.NEO_GLASS_SAAS: DesignSystemTokens(
            theme_name="Neo-Glass SaaS",
            bg_primary="#070a13",
            bg_surface="rgba(15, 23, 42, 0.65)",
            accent_primary="#38bdf8",
            accent_secondary="#818cf8",
            text_primary="#f1f5f9",
            text_secondary="#94a3b8",
            border_color="rgba(255, 255, 255, 0.08)",
            font_heading="'Plus Jakarta Sans', 'Inter', sans-serif",
            font_body="'Inter', sans-serif",
            font_code="'JetBrains Mono', monospace",
            border_radius="16px",
            aesthetic_rationale="Depth-layered glassmorphism with acrylic blur for consumer web applications and modern portals.",
        ),
        DesignAestheticTheme.SWISS_INTERNATIONAL: DesignSystemTokens(
            theme_name="Swiss International Style",
            bg_primary="#ffffff",
            bg_surface="#f4f4f5",
            accent_primary="#e11d48",
            accent_secondary="#09090b",
            text_primary="#09090b",
            text_secondary="#52525b",
            border_color="#e4e4e7",
            font_heading="'Helvetica Neue', 'Arial', sans-serif",
            font_body="'Helvetica Neue', 'Arial', sans-serif",
            font_code="'JetBrains Mono', monospace",
            border_radius="4px",
            aesthetic_rationale="Strict geometric grid, objective hierarchy, and functional typography for enterprise systems.",
        ),
    }

    @classmethod
    def deduce_architectural_scope(cls, user_intent: str) -> ArchitecturalScope:
        """Determines whether user wants frontend-only, bug repair, full-stack, or enterprise system."""
        lower = (user_intent or "").lower()
        if any(k in lower for k in ("fix bug", "ci repair", "ast bug", "failing test", "traceback", "syntaxerror", "patch")):
            return ArchitecturalScope.BUG_DETECTION_CI
        elif any(k in lower for k in ("enterprise", "microservice", "docker-compose", "multi-service", "production system")):
            return ArchitecturalScope.ENTERPRISE_SYSTEM
        elif any(k in lower for k in ("landing page", "frontend only", "static site", "html only", "css only", "three.js only")):
            return ArchitecturalScope.FRONTEND_ONLY
        else:
            return ArchitecturalScope.FULL_STACK_APP

    @classmethod
    def generate_upfront_questions(cls, user_intent: str) -> List[UpfrontQuestion]:
        """Generates structured clarifying questions UPFRONT so execution never interrupts in the middle."""
        questions: List[UpfrontQuestion] = []
        lower = user_intent.lower()

        # 1. Architectural Scope Question
        questions.append(
            UpfrontQuestion(
                question_id="scope",
                prompt="Select target architectural scope for this engineering build:",
                options=[
                    "Full-Stack Application (Frontend WebGL/HTML5 + Backend REST API + JSON/SQLite DB + Automated Tests)",
                    "Frontend Only (Responsive Landing Page / Three.js 3D Viewport / Component Library)",
                    "Bug Detection & CI Repair (AST parse, failing test reproduction & minimal patch)",
                    "Enterprise Multi-Service System (Microservices, Docker sandbox, CI/CD pipelines)",
                ],
                default_option="Full-Stack Application (Frontend WebGL/HTML5 + Backend REST API + JSON/SQLite DB + Automated Tests)",
                context="Determines whether backend servers and database layers are created.",
            )
        )

        # 2. Design Aesthetic Question
        questions.append(
            UpfrontQuestion(
                question_id="aesthetic",
                prompt="Select design aesthetic system (avoids repetitive generic purple templates):",
                options=[
                    "Cyber-Terminal (Slate #050811, Electric Cyan #00f0ff, JetBrains Mono — High-Tech Precision)",
                    "Neo-Glass SaaS (Deep Navy, Acrylic Glassmorphism, Sky Blue #38bdf8 — Modern Product)",
                    "Brutalist FinTech (Pitch Black #000000, Canary Yellow #facc15, High Data Density)",
                    "Warm Minimalist (Clean Neutral #fafaf9, Charcoal & Ochre, Editorial Serif)",
                    "Swiss International (Pure White, Grid Alignment, Crimson #e11d48 Accent)",
                ],
                default_option="Cyber-Terminal (Slate #050811, Electric Cyan #00f0ff, JetBrains Mono — High-Tech Precision)",
                context="Guarantees custom CSS tokens, layout grid, and bespoke typography.",
            )
        )

        return questions

    @classmethod
    def generate_design_specification(
        cls,
        project_name: str,
        theme: DesignAestheticTheme,
    ) -> str:
        """Generates DESIGN_SPEC.md with tokens, typography, and component hierarchy."""
        tokens = cls.DESIGN_PALETTES.get(theme, cls.DESIGN_PALETTES[DesignAestheticTheme.CYBER_TERMINAL])
        return (
            f"# Design Specification Contract: {project_name}\n\n"
            f"## 1. Aesthetic Philosophy & Tone\n"
            f"**Theme**: {tokens.theme_name}\n\n"
            f"*{tokens.aesthetic_rationale}*\n\n"
            f"## 2. Design Tokens & CSS Variables\n"
            f"```css\n{tokens.to_css_variables()}\n```\n\n"
            f"## 3. Typography & Rhythm\n"
            f"- **Display / Headings**: {tokens.font_heading}\n"
            f"- **Body Text**: {tokens.font_body} (Line height 1.6, letter-spacing -0.01em)\n"
            f"- **Code & Data Points**: {tokens.font_code} (Tabular figures, high contrast)\n\n"
            f"## 4. Spacing & Layout Grid\n"
            f"- 8-point base grid system (`4px`, `8px`, `16px`, `24px`, `32px`, `48px`, `64px`).\n"
            f"- Responsive breakpoints: Mobile (`<768px`), Tablet (`768px-1024px`), Desktop (`>1024px`).\n"
            f"- Surface Elevation: Flat baseline with elevated interactive cards (0 20px 40px -15px rgba(0,0,0,0.5)).\n"
        )

    @classmethod
    def generate_architecture_specification(
        cls,
        project_name: str,
        scope: ArchitecturalScope,
        modules: List[str],
    ) -> str:
        """Generates ARCH_SPEC.md with system boundaries, data contracts, and failure modes."""
        return (
            f"# System Architecture Specification Contract: {project_name}\n\n"
            f"## 1. Architectural Scope\n"
            f"**Scope**: `{scope.value}`\n\n"
            f"## 2. Core Modules & Directory Layout\n"
            + "\n".join(f"- `{m}`" for m in modules) + "\n\n"
            f"## 3. Invariants & Non-Functional Requirements\n"
            f"- **Zero External Pip Dependencies**: 100% Python standard library (`http.server`, `json`, `sqlite3`).\n"
            f"- **Fail-Closed Execution**: Invalid inputs rejected at boundary with structured HTTP 400.\n"
            f"- **Thread Safety**: State mutators protected via re-entrant locks.\n"
            f"- **Observable Health**: Continuous `/api/health` heartbeat endpoint.\n"
            f"- **Automated Verification**: Complete pytest / unittest suite verifying all contracts.\n"
        )
