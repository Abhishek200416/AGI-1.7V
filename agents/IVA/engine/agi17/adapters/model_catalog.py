"""IVA Model Metadata Catalog & Intelligent Action Swapper.
================================================================================
Provides parameter size parsing (in Billions), company/provider attribution,
use-case & specialty recommendation badges, and dynamic action-based model swapping.

Features:
1. Strict parameter-count ordering (Highest $B$ params -> Lowest $B$ params: 550B -> 1B).
2. Explicit company attribution (NVIDIA, Meta, Mistral AI, DeepSeek, Writer, Google, IBM, OpenAI, etc.).
3. Domain specialty & recommendation badges (Recommended Workhorse, Frontier Reasoning,
   Quant & Volatility, Multimodal Vision, Specialized Coding, Ultra-Fast Routing).
4. Autonomous Action-Based Dynamic Model Swapper: auto-swaps to the optimal/fastest model
   in the user's API key based on the task (micro routing, vision, code, quant, reasoning).

Requires ZERO external PyPI dependencies (100% Python standard library).
================================================================================
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple


class ModelMetadataCatalog:
    """Authoritative catalog for model parameter sizes, providers, and task specialties."""

    # Explicit parameter mappings for models without unambiguous 'B' in name
    EXPLICIT_PARAMS_B: Dict[str, float] = {
        "nvidia/nemotron-3-ultra-550b-a55b": 550.0,
        "nvidia/nemotron-4-340b-instruct": 340.0,
        "nvidia/nemotron-4-340b-reward": 340.0,
        "nvidia/llama-3.1-nemotron-ultra-253b-v1": 253.0,
        "mistralai/mixtral-8x22b-v0.1": 176.0,
        "mistralai/mixtral-8x22b-instruct-v0.1": 176.0,
        "snowflake/arctic": 480.0,
        "databricks/dbrx-instruct": 132.0,
        "mistralai/mistral-large-2-instruct": 123.0,
        "mistralai/mistral-large": 123.0,
        "writer/palmyra-creative-122b": 122.0,
        "nvidia/nemotron-3-super-120b-a12b": 120.0,
        "ai21labs/jamba-1.5-large-instruct": 94.0,
        "ai21labs/jamba-1.5-mini-instruct": 12.0,
        "meta/llama-3.2-90b-vision-instruct": 90.0,
        "nvidia/llama-3.1-nemotron-70b-instruct": 70.0,
        "meta/llama-3.1-70b-instruct": 70.0,
        "writer/palmyra-fin-70b-32k": 70.0,
        "writer/palmyra-med-70b-32k": 70.0,
        "nvidia/llama-3.1-nemotron-51b-instruct": 51.0,
        "stepfun-ai/step-5-preview": 50.0,
        "mistralai/mixtral-8x7b-instruct-v0.1": 47.0,
        "ibm/granite-34b-code-instruct": 34.0,
        "01-ai/yi-large": 34.0,
        "mistralai/codestral-22b-instruct-v0.1": 22.0,
        "mistralai/mistral-small-instruct": 22.0,
        "openai/gpt-oss-20b": 20.0,
        "meta/llama-3.2-11b-vision-instruct": 11.0,
        "ibm/granite-3.0-8b-instruct": 8.0,
        "meta/llama-3.1-8b-instruct": 8.0,
        "mistralai/mistral-7b-instruct-v0.3": 7.0,
        "deepseek-ai/deepseek-coder-6.7b-instruct": 6.7,
        "deepseek-ai/deepseek-v4.1-flash": 8.0,
        "google/gemma-3-12b-it": 12.0,
        "google/gemma-2b": 2.0,
        "meta/llama-3.2-3b-instruct": 3.0,
        "meta/llama-3.2-1b-instruct": 1.0,
        "microsoft/phi-3.5-moe-instruct": 42.0,
        "microsoft/phi-3-mini-128k-instruct": 3.8,
        # Gemini / Claude / OpenAI cloud models
        "gemini-2.5-pro": 200.0,
        "gemini-1.5-pro": 175.0,
        "gemini-2.5-flash": 30.0,
        "gemini-2.0-flash": 20.0,
        "gemini-1.5-flash": 15.0,
        "gemini-1.5-flash-8b": 8.0,
        "gpt-4o": 200.0,
        "gpt-4o-mini": 8.0,
        "o1-preview": 200.0,
        "o1-mini": 20.0,
        "claude-3-5-sonnet-20241022": 175.0,
        "claude-3-opus-20240229": 200.0,
        "claude-3-5-haiku-20241022": 20.0,
    }

    # Explicit company prefix mappings
    COMPANY_MAP: Dict[str, str] = {
        "nvidia": "NVIDIA",
        "meta": "Meta",
        "mistralai": "Mistral AI",
        "deepseek-ai": "DeepSeek",
        "deepseek": "DeepSeek",
        "writer": "Writer",
        "google": "Google",
        "ibm": "IBM",
        "microsoft": "Microsoft",
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "ai21labs": "AI21 Labs",
        "databricks": "Databricks",
        "moonshotai": "Moonshot AI",
        "minimaxai": "MiniMax",
        "01-ai": "01.AI (Yi)",
        "snowflake": "Snowflake",
        "zyphra": "Zyphra",
        "stepfun-ai": "StepFun",
        "baichuan-inc": "Baichuan",
        "qwen": "Alibaba Qwen",
        "groq": "Groq",
        "cohere": "Cohere",
        "upstage": "Upstage",
        "rakuten": "Rakuten",
    }

    @classmethod
    def parse_parameter_billions(cls, model_id: str) -> float:
        """Extracts parameter count in billions (B) from model name with high precision."""
        clean = (model_id or "").strip().lower()
        if not clean:
            return 7.0

        # 1. Exact match in explicit catalog
        if clean in cls.EXPLICIT_PARAMS_B:
            return cls.EXPLICIT_PARAMS_B[clean]

        # 2. Check suffix or key in explicit catalog
        for k, v in cls.EXPLICIT_PARAMS_B.items():
            if k in clean or clean.endswith(k.split("/")[-1]):
                return v

        # 3. MoE Multiplier pattern: e.g. 8x22b, 8x7b, 16x12b
        moe_match = re.search(r"(\d+)x(\d+(?:\.\d+)?)b", clean)
        if moe_match:
            experts = int(moe_match.group(1))
            size = float(moe_match.group(2))
            return round(experts * size, 1)

        # 4. Standard parameter count: e.g. 550b, 340b, 253b, 120b, 70b, 6.7b, 8b, 1b
        param_match = re.search(r"(?<![a-zA-Z0-9])(\d+(?:\.\d+)?)\s*b(?![a-zA-Z0-9])", clean)
        if param_match:
            try:
                val = float(param_match.group(1))
                # Protect against years or dimensions like 2024 or 32768
                if 0.1 <= val <= 2000.0:
                    return val
            except ValueError:
                pass

        # 5. Semantic size hints
        if "ultra" in clean or "550" in clean:
            return 250.0
        elif "large" in clean or "super" in clean:
            return 70.0
        elif "medium" in clean or "mid" in clean:
            return 34.0
        elif "small" in clean or "mini" in clean or "flash" in clean or "nano" in clean:
            return 8.0
        elif "tiny" in clean or "micro" in clean:
            return 2.0

        return 7.0  # Default gracefully to common open-weights base size

    @classmethod
    def extract_company(cls, model_id: str) -> str:
        """Extracts organization or company that built the model."""
        clean = (model_id or "").strip()
        if "/" in clean:
            prefix = clean.split("/")[0].lower()
            if prefix in cls.COMPANY_MAP:
                return cls.COMPANY_MAP[prefix]
            return prefix.capitalize()

        lower = clean.lower()
        if "gemini" in lower or "gemma" in lower:
            return "Google"
        elif "claude" in lower:
            return "Anthropic"
        elif "gpt" in lower or "o1" in lower or "o3" in lower:
            return "OpenAI"
        elif "nemotron" in lower:
            return "NVIDIA"
        elif "llama" in lower or "codellama" in lower:
            return "Meta"
        elif "mistral" in lower or "mixtral" in lower or "codestral" in lower:
            return "Mistral AI"
        elif "deepseek" in lower:
            return "DeepSeek"
        elif "granite" in lower:
            return "IBM"
        elif "phi" in lower:
            return "Microsoft"
        elif "command" in lower:
            return "Cohere"
        elif "palmyra" in lower:
            return "Writer"
        elif "qwen" in lower:
            return "Alibaba Qwen"
        elif "jamba" in lower:
            return "AI21 Labs"

        return "Independent"

    @classmethod
    def get_specialty_metadata(cls, model_id: str) -> Dict[str, Any]:
        """Returns structured metadata: parameter size, company, specialty badge, description, and speed tier."""
        clean = (model_id or "").strip()
        lower = clean.lower()
        params_b = cls.parse_parameter_billions(clean)
        company = cls.extract_company(clean)

        # Flagship Nemotron 70B is the designated recommended workhorse
        is_recommended = ("nemotron-70b" in lower) or (clean == "nvidia/llama-3.1-nemotron-70b-instruct")

        # Speed Tier
        if params_b <= 25.0:
            speed_tier = "[⚡ ULTRA-FAST]"
            speed_desc = "Instant response (<150ms), high token streaming rate"
        elif params_b <= 90.0:
            speed_tier = "[⚖️ BALANCED]"
            speed_desc = "Optimal balance of deep reasoning and rapid throughput"
        else:
            speed_tier = "[🧠 DEEP-THINKING]"
            speed_desc = "Massive parameter reasoning, high-capacity architectural synthesis"

        # Explicit known models
        if clean == "nvidia/llama-3.1-nemotron-70b-instruct":
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "70B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ RECOMMENDED WORKHORSE",
                "specialty": "Optimal balance of speed, code synthesis, refactoring, and multi-turn stability",
                "is_recommended": True,
            }
        elif "550b" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "550B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ FRONTIER REASONING",
                "specialty": "Flagship mega-scale architecture, theoretical proofs & high-dimensional planning",
                "is_recommended": False,
            }
        elif "340b" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "340B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ FRONTIER REASONING",
                "specialty": "Massive synthetic data generation, complex alignment & deep reasoning",
                "is_recommended": False,
            }
        elif "253b" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "253B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ DEEP REFACTORING",
                "specialty": "Ultra multi-agent architectural refactoring, AST transformations & system logic",
                "is_recommended": False,
            }
        elif "mixtral-8x22b" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "176B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ SPARSE MOE REASONING",
                "specialty": "High-capacity sparse mixture-of-experts for enterprise code and multilingual logic",
                "is_recommended": False,
            }
        elif "dbrx" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "132B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ OPEN MOE ARCHITECTURE",
                "specialty": "MoE architecture optimized for enterprise knowledge synthesis and logical tasks",
                "is_recommended": False,
            }
        elif "mistral-large" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "123B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ ENTERPRISE REASONING",
                "specialty": "Flagship multilingual reasoning, complex code generation and mathematical analysis",
                "is_recommended": False,
            }
        elif "palmyra-creative" in lower or "122b" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "122B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ EXPANSIVE SYNTHESIS",
                "specialty": "High-coherence creative synthesis, expansive technical docs & structured writing",
                "is_recommended": False,
            }
        elif "120b" in lower or "super-120b" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "120B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ QUANT & VOLATILITY",
                "specialty": "Super-scale quantitative research, econometric modeling & volatility forecasting",
                "is_recommended": False,
            }
        elif "jamba-1.5-large" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "94B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ HYBRID SSM-TRANSFORMER",
                "specialty": "Hybrid Mamba-Transformer architecture for ultra-long context reasoning and retrieval",
                "is_recommended": False,
            }
        elif "vision" in lower and "90b" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "90B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ MULTIMODAL VISION",
                "specialty": "Flagship visual reasoning, high-res chart inspection, DOM screenshot analysis",
                "is_recommended": False,
            }
        elif "palmyra-fin" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "70B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ FINANCIAL INTELLIGENCE",
                "specialty": "Financial statements, SEC filings, economic disclosures & quant valuation",
                "is_recommended": False,
            }
        elif "palmyra-med" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "70B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ CLINICAL & BIOMEDICAL",
                "specialty": "Biomedical research, clinical pharmacology & life science literature synthesis",
                "is_recommended": False,
            }
        elif "51b" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "51B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ HIGH-THROUGHPUT REASONING",
                "specialty": "Optimized compute-density for low-latency reasoning and multi-step workflows",
                "is_recommended": False,
            }
        elif "step-5" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "50B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ MULTIMODAL REASONING",
                "specialty": "Advanced cross-modal alignment and complex reasoning preview",
                "is_recommended": False,
            }
        elif "mixtral-8x7b" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "47B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ FAST MOE REASONING",
                "specialty": "High-efficiency sparse MoE routing with balanced throughput and quality",
                "is_recommended": False,
            }
        elif "granite-34b-code" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "34B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ ENTERPRISE CODE",
                "specialty": "Enterprise code synthesis, legacy migration, and test coverage generation",
                "is_recommended": False,
            }
        elif "codestral-22b" in lower or "codestral" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "22B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ SPECIALIZED CODING",
                "specialty": "Dedicated code synthesis, completion, and AST patch generation with low latency",
                "is_recommended": False,
            }
        elif "gpt-oss-20b" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "20B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ FAST OSS REASONING",
                "specialty": "Open-source GPT architecture for rapid conversational logic and code parsing",
                "is_recommended": False,
            }
        elif "vision" in lower and "11b" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "11B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ FAST VISION",
                "specialty": "High-throughput screenshot and DOM element identification with sub-second response",
                "is_recommended": False,
            }
        elif "granite-3.0-8b" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "8B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ ULTRA-FAST ROUTING",
                "specialty": "Ultra-low latency micro-task parsing, regex extraction, and event dispatch (<150ms)",
                "is_recommended": False,
            }
        elif "mistral-7b" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": "7B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ ULTRA-FAST ROUTING",
                "specialty": "High-velocity routing, micro-task execution and fast conversational replies",
                "is_recommended": False,
            }
        elif "deepseek-coder" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": f"{params_b:g}B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ FAST CODE REPAIR",
                "specialty": "Rapid function synthesis, AST bug isolation, and code review sweeps",
                "is_recommended": False,
            }
        elif "deepseek-v4" in lower or "deepseek-chat" in lower:
            return {
                "model_id": clean,
                "company": company,
                "params_b": params_b,
                "params_label": f"{params_b:g}B",
                "speed_tier": speed_tier,
                "speed_desc": speed_desc,
                "badge": "★ DEEP REASONING & MATH",
                "specialty": "Mathematical derivation, algorithmic problem solving & dense logic",
                "is_recommended": False,
            }

        # Heuristic categorization for any unlisted model
        params_label = f"{params_b:g}B"
        if "vision" in lower or "image" in lower or "multimodal" in lower:
            badge = "★ MULTIMODAL VISION"
            specialty = "High-resolution screenshot inspection, chart reading & DOM element mapping"
        elif "code" in lower or "coder" in lower or "coding" in lower:
            badge = "★ SPECIALIZED CODING"
            specialty = "Code generation, AST refactoring, bug fixes, and unit test generation"
        elif "fin" in lower or "finance" in lower or "econ" in lower:
            badge = "★ QUANT & FINANCE"
            specialty = "Quantitative finance modeling, volatility forecasting & economic analysis"
        elif "med" in lower or "bio" in lower or "health" in lower:
            badge = "★ CLINICAL & BIOLOGY"
            specialty = "Medical sciences, biomedical literature analysis, and clinical protocols"
        elif params_b >= 200.0:
            badge = "★ FRONTIER REASONING"
            specialty = "Mega-scale architectural synthesis, multi-step proofs, and complex planning"
        elif params_b >= 90.0:
            badge = "★ DEEP ARCHITECTURE"
            specialty = "High-capacity multi-agent coordination, long-context reasoning & system design"
        elif params_b >= 40.0:
            badge = "★ BALANCED WORKHORSE"
            specialty = "General high-throughput reasoning, code reviews & autonomous execution"
        elif params_b >= 15.0:
            badge = "★ FAST INFERENCE"
            specialty = "Low latency, responsive chat, and mid-tier analytical workflows"
        else:
            badge = "★ ULTRA-FAST ROUTING"
            specialty = "Sub-150ms response, micro-task parsing, JSON formatting & event routing"

        return {
            "model_id": clean,
            "company": company,
            "params_b": params_b,
            "params_label": params_label,
            "speed_tier": speed_tier,
            "speed_desc": speed_desc,
            "badge": badge,
            "specialty": specialty,
            "is_recommended": is_recommended,
        }

    @classmethod
    def rank_and_sort_models(cls, models: List[str]) -> List[Dict[str, Any]]:
        """Sorts models strictly descending by parameter count (B).
        
        Ordering:
        1. Parameter Count (Highest B -> Lowest B: 550B -> 340B -> 253B -> 176B ... -> 1B).
        2. Recommended status (True before False within identical parameter bucket).
        3. Model Identifier (Alphabetical tie-breaker).
        """
        parsed = [cls.get_specialty_metadata(m) for m in set(models)]
        # Sort key: (-params_b, -int(is_recommended), model_id)
        sorted_meta = sorted(
            parsed,
            key=lambda d: (-d["params_b"], -1 if d["is_recommended"] else 0, d["model_id"]),
        )
        return sorted_meta

    @classmethod
    def get_action_model(cls, available_models: List[str], action_type: str = "default") -> str:
        """Autonomously selects the fastest and most specialized model from the available pool for a given action.
        
        Action Types:
        - 'fast' / 'micro' / 'routing' / 'parser': Selects the lowest latency model (<150ms).
        - 'vision' / 'multimodal' / 'screenshot' / 'dom': Selects top multimodal vision model.
        - 'coding' / 'code' / 'ast' / 'refactor': Selects dedicated coding specialist.
        - 'reasoning' / 'architecture' / 'frontier': Selects largest parameter frontier model (550B/253B/340B).
        - 'finance' / 'quant' / 'volatility': Selects specialized finance/volatility model.
        - 'default': Selects balanced workhorse (Nemotron 70B).
        """
        if not available_models:
            return "nvidia/llama-3.1-nemotron-70b-instruct"

        action = (action_type or "default").lower().strip()
        models_lower = {m.lower(): m for m in available_models}

        # 1. Vision / Multimodal Action
        if action in ("vision", "multimodal", "screenshot", "dom", "browser"):
            vision_prefs = [
                "meta/llama-3.2-90b-vision-instruct",
                "meta/llama-3.2-11b-vision-instruct",
                "stepfun-ai/step-5-preview",
                "gemini-2.5-flash",
                "gpt-4o",
            ]
            for vp in vision_prefs:
                for ml, original in models_lower.items():
                    if vp in ml or ml.endswith(vp.split("/")[-1]):
                        return original
            # Fallback: any model with 'vision' in name
            for ml, original in models_lower.items():
                if "vision" in ml:
                    return original

        # 2. Fast Routing / Micro-Task / Parser (<150ms response)
        elif action in ("fast", "micro", "routing", "parser", "classify", "triage"):
            fast_prefs = [
                "ibm/granite-3.0-8b-instruct",
                "mistralai/mistral-7b-instruct-v0.3",
                "meta/llama-3.1-8b-instruct",
                "deepseek-ai/deepseek-coder-6.7b-instruct",
                "deepseek-ai/deepseek-v4.1-flash",
                "google/gemma-3-12b-it",
                "meta/llama-3.2-3b-instruct",
                "google/gemma-2b",
                "meta/llama-3.2-1b-instruct",
                "gemini-2.5-flash",
                "gpt-4o-mini",
            ]
            for fp in fast_prefs:
                for ml, original in models_lower.items():
                    if fp in ml or ml.endswith(fp.split("/")[-1]):
                        return original
            # Fallback: pick model with smallest parameter size
            ranked = cls.rank_and_sort_models(available_models)
            if ranked:
                return ranked[-1]["model_id"]

        # 3. Dedicated Coding & AST Refactoring Action
        elif action in ("coding", "code", "ast", "refactor", "debug", "patch"):
            code_prefs = [
                "nvidia/llama-3.1-nemotron-70b-instruct",
                "deepseek-ai/deepseek-coder-6.7b-instruct",
                "mistralai/codestral-22b-instruct-v0.1",
                "ibm/granite-34b-code-instruct",
                "nvidia/llama-3.1-nemotron-ultra-253b-v1",
                "meta/codellama-70b",
            ]
            for cp in code_prefs:
                for ml, original in models_lower.items():
                    if cp in ml or ml.endswith(cp.split("/")[-1]):
                        return original

        # 4. Quantitative Modeling & Volatility Action
        elif action in ("finance", "quant", "volatility", "hawkes", "svi", "derivatives"):
            quant_prefs = [
                "nvidia/nemotron-3-super-120b-a12b",
                "writer/palmyra-fin-70b-32k",
                "nvidia/llama-3.1-nemotron-70b-instruct",
                "nvidia/llama-3.1-nemotron-ultra-253b-v1",
            ]
            for qp in quant_prefs:
                for ml, original in models_lower.items():
                    if qp in ml or ml.endswith(qp.split("/")[-1]):
                        return original

        # 5. Frontier Reasoning & Mega Architecture Action
        elif action in ("reasoning", "architecture", "frontier", "complex", "math"):
            reasoning_prefs = [
                "nvidia/llama-3.1-nemotron-ultra-253b-v1",
                "nvidia/nemotron-4-340b-instruct",
                "nvidia/nemotron-3-ultra-550b-a55b",
                "mistralai/mixtral-8x22b-v0.1",
                "mistralai/mistral-large-2-instruct",
                "nvidia/llama-3.1-nemotron-70b-instruct",
                "claude-3-5-sonnet-20241022",
                "gpt-4o",
            ]
            for rp in reasoning_prefs:
                for ml, original in models_lower.items():
                    if rp in ml or ml.endswith(rp.split("/")[-1]):
                        return original
            # Fallback: pick model with largest parameter size
            ranked = cls.rank_and_sort_models(available_models)
            if ranked:
                return ranked[0]["model_id"]

        # Default fallback: prefer recommended workhorse
        workhorse_prefs = [
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "gemini-2.5-flash",
            "gpt-4o",
            "claude-3-5-sonnet-20241022",
            "llama-3.3-70b-versatile",
            "deepseek-chat",
        ]
        for wp in workhorse_prefs:
            for ml, original in models_lower.items():
                if wp in ml or ml.endswith(wp.split("/")[-1]):
                    return original

        return available_models[0]
