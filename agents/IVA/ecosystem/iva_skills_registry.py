"""
iva_skills_registry.py — Unified Master Registry for All IVA Skills and MCP Capabilities.

Unifies all external MCP servers, workflow skills, media directorship tools, and quant engines
into a clean, high-performance, and categorized ecosystem: "IVA Skills".

10 Distinct Operational Categories:
1. CORE_INTELLIGENCE_AND_REASONING
2. QUANT_FINANCE_AND_ALGO_TRADING
3. MEDIA_STUDIO_AND_OMNICHANNEL
4. BROWSER_AUTOMATION_AND_WEB
5. MOBILE_AND_DEVICE_TESTING
6. CLOUD_AND_INFRASTRUCTURE
7. ENGINEERING_HYGIENE_AND_WORKFLOW
8. GEMINI_AND_MULTIMODAL_API
9. RESEARCH_AND_DEEP_EVIDENCE
10. SYSTEM_OS_AND_STORAGE
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class SkillCategory(str, Enum):
    CORE_INTELLIGENCE = "Core Intelligence & Reasoning"
    QUANT_FINANCE = "Quantitative Finance & Algorithmic Trading"
    MEDIA_STUDIO = "Media Studio, Video Directing & Omnichannel Social"
    BROWSER_AUTOMATION = "Browser Automation & Web Operations"
    MOBILE_DEVICE = "Mobile & Device Testing"
    CLOUD_INFRASTRUCTURE = "Cloud Deployment & Infrastructure"
    ENGINEERING_WORKFLOW = "Engineering Hygiene & Workflow Mastery"
    GEMINI_MULTIMODAL = "Gemini API & Multimodal Tooling"
    RESEARCH_EVIDENCE = "Research & Deep Evidence Synthesis"
    SYSTEM_STORAGE = "System, OS & Storage Stewards"


@dataclass
class IvaSkillDefinition:
    name: str
    category: SkillCategory
    description: str
    execution_type: str  # "native", "mcp_bridge", "hybrid"
    tools_or_commands: List[str]
    author_or_source: str
    primary_file_or_spec: str


# Complete Unified Catalog of IVA Skills & MCP Tools
IVA_SKILLS_CATALOG: List[IvaSkillDefinition] = [
    # 1. Core Intelligence & Reasoning
    IvaSkillDefinition(
        name="sequential-thinking",
        category=SkillCategory.CORE_INTELLIGENCE,
        description="Dynamic multi-step reflective thinking, hypothesis generation, and step-by-step invariant validation.",
        execution_type="hybrid",
        tools_or_commands=["sequentialthinking"],
        author_or_source="Antigravity / MCP Sequential Thinking",
        primary_file_or_spec="mcp/sequential-thinking/sequentialthinking.json",
    ),
    IvaSkillDefinition(
        name="context7",
        category=SkillCategory.CORE_INTELLIGENCE,
        description="Upstream library documentation resolution and real-time SDK signature inspection.",
        execution_type="hybrid",
        tools_or_commands=["resolve-library-id", "query-docs"],
        author_or_source="Context7 MCP Server",
        primary_file_or_spec="mcp/context7/query-docs.json",
    ),
    IvaSkillDefinition(
        name="clean-code",
        category=SkillCategory.CORE_INTELLIGENCE,
        description="Clean code architecture, SOLID refactoring principles, and Uncle Bob design heuristics.",
        execution_type="native",
        tools_or_commands=["refactor_code", "audit_cleanliness"],
        author_or_source="IVA Core Clean Code Heuristics",
        primary_file_or_spec="skills/clean-code/SKILL.md",
    ),
    IvaSkillDefinition(
        name="codegraphcontext",
        category=SkillCategory.CORE_INTELLIGENCE,
        description="Code graph dependency analysis, AST relationship traversal, and project symbol graphs.",
        execution_type="mcp_bridge",
        tools_or_commands=["query_graph", "find_callers", "trace_dependencies"],
        author_or_source="Antigravity CodeGraphContext MCP",
        primary_file_or_spec="mcp/codegraphcontext/",
    ),

    # 2. Quantitative Finance & Algorithmic Trading
    IvaSkillDefinition(
        name="omega-quant-trading",
        category=SkillCategory.QUANT_FINANCE,
        description="Institutional quantitative trading engineering: Hawkes point processes, MLOFI, SSVI volatility surfaces.",
        execution_type="native",
        tools_or_commands=["calibrate_ssvi", "compute_mlofi", "simulate_hawkes"],
        author_or_source="IVA Quantitative Research Division",
        primary_file_or_spec="skills/omega-quant-trading/SKILL.md",
    ),
    IvaSkillDefinition(
        name="quant-analyst",
        category=SkillCategory.QUANT_FINANCE,
        description="Institutional quantitative analyst playbook: friction-aware Bayesian-Kelly allocation, liquidity modeling.",
        execution_type="native",
        tools_or_commands=["analyze_market_microstructure", "estimate_slippage"],
        author_or_source="IVA Quantitative Research Division",
        primary_file_or_spec="skills/quant-analyst/SKILL.md",
    ),
    IvaSkillDefinition(
        name="strategy-backtesting",
        category=SkillCategory.QUANT_FINANCE,
        description="Event-driven backtesting with realistic fill assumptions, exchange fees, and short borrow modeling.",
        execution_type="native",
        tools_or_commands=["run_event_backtest", "calculate_sharpe_deflated"],
        author_or_source="IVA Quantitative Research Division",
        primary_file_or_spec="skills/strategy-backtesting/SKILL.md",
    ),
    IvaSkillDefinition(
        name="backtest-integrity-audit",
        category=SkillCategory.QUANT_FINANCE,
        description="Adversarial audit of backtest code, lookahead bias, fill assumptions, fee deductions, and cash accounting.",
        execution_type="native",
        tools_or_commands=["audit_lookahead_bias", "verify_cash_drag"],
        author_or_source="IVA Trading Risk Stewards",
        primary_file_or_spec="skills/backtest-integrity-audit/SKILL.md",
    ),
    IvaSkillDefinition(
        name="trading-risk-management",
        category=SkillCategory.QUANT_FINANCE,
        description="Real-time risk limits: Value at Risk (VaR), Conditional VaR, Hawkes jump-diffusion volatility projection.",
        execution_type="native",
        tools_or_commands=["calculate_var", "enforce_max_drawdown_gate"],
        author_or_source="IVA Trading Risk Stewards",
        primary_file_or_spec="skills/trading-risk-management/SKILL.md",
    ),
    IvaSkillDefinition(
        name="options-flow-analyzer",
        category=SkillCategory.QUANT_FINANCE,
        description="Real vs lottery call separation for options Put/Call ratio analysis, preventing OTM noise inversion.",
        execution_type="native",
        tools_or_commands=["filter_otm_noise", "compute_institutional_pc_ratio"],
        author_or_source="IVA Quantitative Research Division",
        primary_file_or_spec="skills/options-flow-analyzer/SKILL.md",
    ),
    IvaSkillDefinition(
        name="order-pretrade-validation",
        category=SkillCategory.QUANT_FINANCE,
        description="Pre-trade sanity checks: fat-finger prevention, price collars, notional size limits, lot size rounding.",
        execution_type="native",
        tools_or_commands=["validate_pretrade_gates", "check_price_collars"],
        author_or_source="IVA Trading Safety Stewards",
        primary_file_or_spec="skills/order-pretrade-validation/SKILL.md",
    ),
    IvaSkillDefinition(
        name="paper-trading-execution",
        category=SkillCategory.QUANT_FINANCE,
        description="Simulate real-time paper trading on live exchange feeds with simulated order books and fill probability.",
        execution_type="native",
        tools_or_commands=["execute_paper_order", "reconcile_paper_ledger"],
        author_or_source="IVA Paper Execution Engine",
        primary_file_or_spec="skills/paper-trading-execution/SKILL.md",
    ),

    # 3. Media Studio, Video Directing & Omnichannel Social
    IvaSkillDefinition(
        name="iva-video-skill",
        category=SkillCategory.MEDIA_STUDIO,
        description="Autonomous video directing, 1080p-4K real footage sourcing, ASS kinetic subtitles, and -14 LUFS mastering.",
        execution_type="native",
        tools_or_commands=["compile_real_footage", "render_montage", "audit_media_gates"],
        author_or_source="IVA Media Studio",
        primary_file_or_spec="skills/iva-video-skill/SKILL.md",
    ),
    IvaSkillDefinition(
        name="iva-instagram-skill",
        category=SkillCategory.MEDIA_STUDIO,
        description="13-skill Instagram growth suite: Reels, 26 hook formulas, 125-char caption linter, carousel design, humanizer.",
        execution_type="native",
        tools_or_commands=["/ig-reel", "/ig-viral", "/ig-caption", "/ig-carousel", "/ig-human", "/ig-repurpose"],
        author_or_source="Jakeschincariol / Integrated by IVA",
        primary_file_or_spec="skills/iva-instagram-skill/SKILL.md",
    ),
    IvaSkillDefinition(
        name="iva-omnichannel-social-skill",
        category=SkillCategory.MEDIA_STUDIO,
        description="Universal multi-platform social media adaptation engine across YouTube, Instagram, TikTok, X, LinkedIn, Threads.",
        execution_type="native",
        tools_or_commands=["adapt_for_all_platforms", "export_omnichannel_bundle"],
        author_or_source="IVA Media Studio",
        primary_file_or_spec="skills/iva-omnichannel-social-skill/SKILL.md",
    ),
    IvaSkillDefinition(
        name="lemo-opuscar",
        category=SkillCategory.MEDIA_STUDIO,
        description="Autonomous code-driven animation, cinematic directing, and motion-graphics film creation system.",
        execution_type="native",
        tools_or_commands=["generate_animation_script", "direct_motion_film"],
        author_or_source="Lemo-OpusCar Team / IVA",
        primary_file_or_spec="skills/lemo-opuscar/SKILL.md",
    ),

    # 4. Browser Automation & Web Operations
    IvaSkillDefinition(
        name="playwright",
        category=SkillCategory.BROWSER_AUTOMATION,
        description="CDP and Playwright browser session controller for headless/headed web navigation, DOM inspection, and form workflows.",
        execution_type="hybrid",
        tools_or_commands=["browser_navigate", "browser_click", "browser_type", "browser_snapshot", "browser_take_screenshot"],
        author_or_source="Antigravity Playwright MCP / Native Playwright",
        primary_file_or_spec="mcp/playwright/",
    ),
    IvaSkillDefinition(
        name="browser-harness",
        category=SkillCategory.BROWSER_AUTOMATION,
        description="Drive existing persistent Chrome instances through CDP for authenticated, visual web automation.",
        execution_type="native",
        tools_or_commands=["connect_cdp_session", "inspect_active_tab"],
        author_or_source="IVA Browser Automation Division",
        primary_file_or_spec="skills/browser-harness/SKILL.md",
    ),
    IvaSkillDefinition(
        name="chrome-devtools-mcp",
        category=SkillCategory.BROWSER_AUTOMATION,
        description="Direct Chrome DevTools Protocol controller for network request inspection, performance metrics, and console evaluation.",
        execution_type="mcp_bridge",
        tools_or_commands=["evaluate_script", "capture_network_har"],
        author_or_source="Chrome DevTools MCP",
        primary_file_or_spec="mcp/chrome-devtools-mcp/",
    ),

    # 5. Mobile & Device Testing
    IvaSkillDefinition(
        name="maestro",
        category=SkillCategory.MOBILE_DEVICE,
        description="Mobile device automation and UI test execution on Android/iOS via local emulator or cloud device farms.",
        execution_type="hybrid",
        tools_or_commands=["list_devices", "take_screenshot", "run", "inspect_screen", "run_on_cloud"],
        author_or_source="Maestro MCP / Mobile Testing",
        primary_file_or_spec="mcp/maestro/",
    ),
    IvaSkillDefinition(
        name="mobile-mcp",
        category=SkillCategory.MOBILE_DEVICE,
        description="Mobile UI test harness, device orientation control, and gesture simulation.",
        execution_type="mcp_bridge",
        tools_or_commands=["tap_element", "swipe_gesture", "input_text"],
        author_or_source="Mobile MCP Server",
        primary_file_or_spec="mcp/mobile-mcp/",
    ),
    IvaSkillDefinition(
        name="screenshots",
        category=SkillCategory.MOBILE_DEVICE,
        description="Marketing and documentation screenshot capture engine with framing and device mockups.",
        execution_type="native",
        tools_or_commands=["generate_marketing_screenshot"],
        author_or_source="IVA Design & Marketing Division",
        primary_file_or_spec="skills/screenshots/SKILL.md",
    ),

    # 6. Cloud Deployment & Infrastructure
    IvaSkillDefinition(
        name="cloudrun",
        category=SkillCategory.CLOUD_INFRASTRUCTURE,
        description="Google Cloud Run service deployment, container management, and real-time execution log inspection.",
        execution_type="hybrid",
        tools_or_commands=["list_projects", "list_services", "deploy_local_folder", "deploy_container_image", "get_service_log"],
        author_or_source="Google Cloud Run MCP",
        primary_file_or_spec="mcp/cloudrun/",
    ),
    IvaSkillDefinition(
        name="firebase-mcp-server",
        category=SkillCategory.CLOUD_INFRASTRUCTURE,
        description="Firebase web app deployment, security rules validation, and serverless Cloud Functions management.",
        execution_type="mcp_bridge",
        tools_or_commands=["deploy_firebase_hosting", "update_firestore_rules"],
        author_or_source="Firebase MCP Server",
        primary_file_or_spec="mcp/firebase-mcp-server/",
    ),
    IvaSkillDefinition(
        name="docker-sandbox",
        category=SkillCategory.CLOUD_INFRASTRUCTURE,
        description="Disposable Docker container runner, container isolation verification, and ephemeral temp directory sandboxing.",
        execution_type="native",
        tools_or_commands=["execute_in_container", "verify_image_digest"],
        author_or_source="IVA Container & Security Stewards",
        primary_file_or_spec="agents/IVA/engine/agi17/process_supervision/sandbox_runner.py",
    ),

    # 7. Engineering Hygiene & Workflow Mastery
    IvaSkillDefinition(
        name="gsd-suite",
        category=SkillCategory.ENGINEERING_WORKFLOW,
        description="Spec-Driven Development suite: 30+ phase commands, autonomous execution, milestone audits, atomic commits.",
        execution_type="hybrid",
        tools_or_commands=["/gsd-spec-phase", "/gsd-plan-phase", "/gsd-execute-phase", "/gsd-verify-work", "/gsd-autonomous", "/gsd-ship"],
        author_or_source="GSD Spec-Driven Development / MCP",
        primary_file_or_spec="mcp/gsd/ and .gemini/config/skills/gsd-*",
    ),
    IvaSkillDefinition(
        name="ponytail",
        category=SkillCategory.ENGINEERING_WORKFLOW,
        description="Lazy senior developer discipline: YAGNI, standard library over custom code, minimal diffs, anti-bloat audits.",
        execution_type="hybrid",
        tools_or_commands=["/ponytail", "/ponytail-review", "/ponytail-audit", "/ponytail-debt", "/ponytail-gain"],
        author_or_source="Ponytail Plugin / MCP",
        primary_file_or_spec="mcp/ponytail/ and .gemini/config/plugins/ponytail/",
    ),
    IvaSkillDefinition(
        name="code-review",
        category=SkillCategory.ENGINEERING_WORKFLOW,
        description="Automated CodeRabbit review runner, AST linting, security vulnerability checks, and PR feedback verification.",
        execution_type="native",
        tools_or_commands=["run_coderabbit_review", "audit_pull_request"],
        author_or_source="CodeRabbit CLI Plugin",
        primary_file_or_spec="skills/code-review/SKILL.md",
    ),
    IvaSkillDefinition(
        name="autofix",
        category=SkillCategory.ENGINEERING_WORKFLOW,
        description="Safely review and apply automated fix feedback with per-change approval gate.",
        execution_type="native",
        tools_or_commands=["apply_autofix_patch"],
        author_or_source="CodeRabbit Plugin",
        primary_file_or_spec="skills/autofix/SKILL.md",
    ),
    IvaSkillDefinition(
        name="pytest-skill",
        category=SkillCategory.ENGINEERING_WORKFLOW,
        description="Production-grade pytest generation with fixtures, parametrize, mocking, and conftest architectures.",
        execution_type="native",
        tools_or_commands=["generate_pytest_suite"],
        author_or_source="IVA Testing & QA Division",
        primary_file_or_spec="skills/pytest-skill/SKILL.md",
    ),

    # 8. Gemini API & Multimodal Tooling
    IvaSkillDefinition(
        name="gemini-api_gemini-api-docs",
        category=SkillCategory.GEMINI_MULTIMODAL,
        description="Official upstream Google Gemini API & SDK documentation search and chunk retrieval.",
        execution_type="mcp_bridge",
        tools_or_commands=["gemini_search_docs", "gemini_get_doc"],
        author_or_source="Google Gemini API Docs MCP",
        primary_file_or_spec="mcp/gemini-api_gemini-api-docs/",
    ),
    IvaSkillDefinition(
        name="gemini-api-dev",
        category=SkillCategory.GEMINI_MULTIMODAL,
        description="Gemini API SDK best practices: structured output schemas, function calling, TTS, multimodal understanding.",
        execution_type="native",
        tools_or_commands=["build_gemini_client", "generate_structured_output"],
        author_or_source="Gemini API Plugin Suite",
        primary_file_or_spec="skills/gemini-api-dev/SKILL.md",
    ),
    IvaSkillDefinition(
        name="gemini-live-api-dev",
        category=SkillCategory.GEMINI_MULTIMODAL,
        description="Bidirectional streaming applications with Gemini Live API: WebSockets, voice activity detection (VAD), live audio.",
        execution_type="native",
        tools_or_commands=["connect_live_session", "stream_audio_bidirectional"],
        author_or_source="Gemini Live API Plugin Suite",
        primary_file_or_spec="skills/gemini-live-api-dev/SKILL.md",
    ),
    IvaSkillDefinition(
        name="prompt-master",
        category=SkillCategory.GEMINI_MULTIMODAL,
        description="Generates optimized prompts for LLMs, Cursor, Midjourney, and generative video systems.",
        execution_type="native",
        tools_or_commands=["optimize_prompt", "synthesize_system_instruction"],
        author_or_source="Prompt Master Plugin Suite",
        primary_file_or_spec="skills/prompt-master/SKILL.md",
    ),

    # 9. Research & Deep Evidence Synthesis
    IvaSkillDefinition(
        name="deep-research",
        category=SkillCategory.RESEARCH_EVIDENCE,
        description="Autonomous research tasks that plan, search, read, and synthesize multi-source information into cited reports.",
        execution_type="native",
        tools_or_commands=["plan_deep_research", "compile_citation_ledger"],
        author_or_source="IVA Research & Evidence Division",
        primary_file_or_spec="skills/deep-research/SKILL.md",
    ),
    IvaSkillDefinition(
        name="go-in-depth",
        category=SkillCategory.RESEARCH_EVIDENCE,
        description="Fan-out web searches, primary source fetch, adversarial claim verification, and factual contradiction checks.",
        execution_type="native",
        tools_or_commands=["fanout_web_search", "verify_adversarial_claims"],
        author_or_source="IVA Research & Evidence Division",
        primary_file_or_spec="skills/go-in-depth/SKILL.md",
    ),
    IvaSkillDefinition(
        name="tavily-web",
        category=SkillCategory.RESEARCH_EVIDENCE,
        description="Web search, content extraction, crawling, and research capabilities using Tavily API.",
        execution_type="native",
        tools_or_commands=["tavily_search", "tavily_extract"],
        author_or_source="Tavily Web Skill Suite",
        primary_file_or_spec="skills/tavily-web/SKILL.md",
    ),

    # 10. System, OS & Storage Stewards
    IvaSkillDefinition(
        name="filesystem",
        category=SkillCategory.SYSTEM_STORAGE,
        description="Safe local filesystem reading, writing, and directory tree operations with path traversal protection.",
        execution_type="mcp_bridge",
        tools_or_commands=["read_file", "write_file", "list_dir", "create_directory"],
        author_or_source="Antigravity Core Filesystem MCP",
        primary_file_or_spec="mcp/filesystem/",
    ),
    IvaSkillDefinition(
        name="windows-shell-reliability",
        category=SkillCategory.SYSTEM_STORAGE,
        description="Reliable PowerShell Windows command execution, encoding guards, and path quoting conventions.",
        execution_type="native",
        tools_or_commands=["execute_powershell_safe"],
        author_or_source="IVA OS & Terminal Division",
        primary_file_or_spec="skills/windows-shell-reliability/SKILL.md",
    ),
    IvaSkillDefinition(
        name="gonkarouter",
        category=SkillCategory.SYSTEM_STORAGE,
        description="Universal multi-provider LLM routing: NVIDIA Build, OpenRouter, Groq, Cerebras, DeepSeek.",
        execution_type="mcp_bridge",
        tools_or_commands=["gonkarouter_list_models", "gonkarouter_chat", "gonkarouter_ask"],
        author_or_source="GonkaRouter MCP Server",
        primary_file_or_spec="mcp/gonkarouter/",
    ),
    IvaSkillDefinition(
        name="memory",
        category=SkillCategory.SYSTEM_STORAGE,
        description="Persistent SQLite WAL memory and knowledge graph storage across multi-session agent operations.",
        execution_type="hybrid",
        tools_or_commands=["store_fact", "recall_memory", "prune_superseded"],
        author_or_source="Omega Memory Architecture / MCP",
        primary_file_or_spec="mcp/memory/",
    ),
]


class IvaSkillsRegistry:
    """Master manager and query engine for the unified IVA Skills ecosystem."""

    def __init__(self, catalog: Optional[List[IvaSkillDefinition]] = None):
        self._catalog = catalog or IVA_SKILLS_CATALOG
        self._by_name: Dict[str, IvaSkillDefinition] = {s.name: s for s in self._catalog}

    def total_count(self) -> int:
        return len(self._catalog)

    def get_all_skills(self) -> List[IvaSkillDefinition]:
        return list(self._catalog)

    def list_categories(self) -> List[str]:
        return [c.value for c in SkillCategory]

    def get_skill(self, name: str) -> Optional[IvaSkillDefinition]:
        return self._by_name.get(name)

    def get_skills_by_category(self, category: SkillCategory | str) -> List[IvaSkillDefinition]:
        cat_val = category.value if isinstance(category, SkillCategory) else category
        return [s for s in self._catalog if s.category.value == cat_val]

    def get_unified_summary(self) -> Dict[str, Any]:
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for cat in SkillCategory:
            grouped[cat.value] = []

        for skill in self._catalog:
            grouped[skill.category.value].append({
                "name": skill.name,
                "execution_type": skill.execution_type,
                "tools": skill.tools_or_commands,
                "description": skill.description,
            })

        return {
            "total_skills_count": len(self._catalog),
            "total_categories_count": len(SkillCategory),
            "categories": grouped,
        }

    def search_skills(self, query: str) -> List[IvaSkillDefinition]:
        q = query.lower()
        results = []
        for s in self._catalog:
            if (
                q in s.name.lower()
                or q in s.description.lower()
                or q in s.category.value.lower()
                or any(q in t.lower() for t in s.tools_or_commands)
            ):
                results.append(s)
        return results

    def generate_markdown_catalog(self) -> str:
        lines = [
            "# IVA Skills Master Catalog (AIVA Skills)",
            "",
            "Unified ecosystem unifying all MCP servers, external tools, quant modules, and media workflows into organized, first-class skills.",
            "",
            f"**Total Registered Skills**: {len(self._catalog)} across {len(SkillCategory)} distinct operational categories.",
            "",
        ]

        for cat in SkillCategory:
            skills = self.get_skills_by_category(cat)
            lines.append(f"## {cat.value} ({len(skills)} Skills)")
            lines.append("")
            lines.append("| Skill Name | Execution Type | Primary Tools / Commands | Description |")
            lines.append("| :--- | :---: | :--- | :--- |")
            for s in skills:
                tools_str = ", ".join([f"`{t}`" for t in s.tools_or_commands[:3]])
                if len(s.tools_or_commands) > 3:
                    tools_str += f" (+{len(s.tools_or_commands)-3} more)"
                lines.append(f"| **`{s.name}`** | `{s.execution_type}` | {tools_str} | {s.description} |")
            lines.append("")

        return "\n".join(lines)


# Singleton instance for direct import
iva_skills_registry = IvaSkillsRegistry()
AivaSkillsCatalog = IvaSkillsRegistry  # Alias matching user query
