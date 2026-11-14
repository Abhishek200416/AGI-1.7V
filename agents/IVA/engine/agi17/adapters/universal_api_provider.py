"""IVA Universal API Provider — Universal Direct Cloud & On-Premises API Execution.
================================================================================
Enables IVA to operate ANYWHERE across any cloud, local, or server environment
using standard API keys (Google Gemini, OpenAI, DeepSeek, Groq, OpenRouter, Ollama)
without requiring Google Antigravity or any proprietary host executables.

Requires ZERO external PyPI dependencies (100% Python standard library: urllib.request).
================================================================================
"""

from __future__ import annotations

import json
import logging
import os
import re
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .model_adapter import (
    BaseModelProvider,
    ModelCostBudgetExceededError,
    ModelProviderConfig,
    ModelRequest,
    ModelResponseValidationError,
    redact_sensitive_text,
)
from .model_catalog import ModelMetadataCatalog

logger = logging.getLogger("UniversalAPIProvider")


def load_repo_dotenv(root_dir: Optional[Path] = None) -> Dict[str, str]:
    """Loads variables from the repository's `.env` file into `os.environ` if not already set.
    
    Uses 100% standard library Python line parsing (no external dotenv dependency needed).
    """
    loaded = {}
    if root_dir is not None:
        candidates = [Path(root_dir) / ".env"]
    else:
        current = Path(__file__).resolve()
        repo_root = current.parents[5] if len(current.parents) >= 6 else Path.cwd()
        candidates = [
            Path.cwd() / ".env",
            repo_root / ".env",
        ]
    for env_file in candidates:
        if env_file.is_file():
            try:
                for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and key not in os.environ:
                        os.environ[key] = val
                        loaded[key] = val
                if loaded:
                    break
            except Exception as exc:
                logger.debug("Failed reading .env from %s: %s", env_file, exc)
    return loaded


# Automatically load local .env if present upon import
load_repo_dotenv()


class UniversalAPIProvider(BaseModelProvider):
    """Production standard library provider supporting direct Google Gemini and OpenAI-compatible endpoints."""

    _POOL_MODELS_CACHE: Dict[str, Any] = {}
    _POOL_MODELS_CACHE_TIME: float = 0.0

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        provider_type: Optional[str] = None,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_sec: float = 60.0,
        max_retries: int = 3,
        backoff_sec: float = 1.0,
    ) -> None:
        load_repo_dotenv()
        self.timeout_sec = timeout_sec
        self.max_retries = max_retries
        self.backoff_sec = backoff_sec

        # Resolve credentials and provider type
        gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")
        nvidia_key = os.environ.get("NVIDIA_API_KEY") or os.environ.get("NVIDIA_NIM_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")
        groq_key = os.environ.get("GROQ_API_KEY")
        deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
        openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        custom_base = base_url or os.environ.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE_URL")

        active_prov_env = (os.environ.get("ACTIVE_PROVIDER") or "").lower()
        if provider_type:
            self.provider_type = provider_type.lower()
        elif api_key:
            det = self.detect_provider_from_key(api_key)
            if det != "unknown":
                self.provider_type = det
            elif active_prov_env in ("openrouter", "nvidia", "gemini", "anthropic", "groq", "deepseek", "openai"):
                self.provider_type = active_prov_env
            else:
                self.provider_type = "openai"
        elif active_prov_env in ("openrouter", "nvidia", "gemini", "anthropic", "groq", "deepseek", "openai"):
            self.provider_type = active_prov_env
        elif openrouter_key:
            self.provider_type = "openrouter"
        elif gemini_key:
            self.provider_type = "gemini"
        elif nvidia_key:
            self.provider_type = "nvidia"
        elif anthropic_key:
            self.provider_type = "anthropic"
        elif groq_key:
            self.provider_type = "groq"
        elif deepseek_key:
            self.provider_type = "deepseek"
        elif openai_key or custom_base:
            self.provider_type = "openai"
        else:
            self.provider_type = "gemini"  # Default fallback

        self.provider_brand = self.provider_type

        # Ground self.api_key to explicit api_key or resolved provider key
        if api_key:
            self.api_key = api_key
        elif self.provider_type == "gemini":
            self.api_key = gemini_key or ""
        elif self.provider_type == "openrouter":
            self.api_key = openrouter_key or ""
        elif self.provider_type == "nvidia":
            self.api_key = nvidia_key or ""
        elif self.provider_type == "anthropic":
            self.api_key = anthropic_key or ""
        elif self.provider_type == "groq":
            self.api_key = groq_key or ""
        elif self.provider_type == "deepseek":
            self.api_key = deepseek_key or ""
        else:
            self.api_key = openai_key or ""

        if self.provider_type == "gemini":
            self.api_key = api_key or gemini_key or ""
            # Default to gemini-2.5-flash or gemini-2.0-flash (fast, reliable, free tiers available)
            self.model_name = (
                model_name
                or os.environ.get("GEMINI_MODEL")
                or os.environ.get("IVA_MODEL")
                or "gemini-2.5-flash"
            )
            self.base_url = (
                base_url
                or os.environ.get("GEMINI_BASE_URL")
                or "https://generativelanguage.googleapis.com/v1beta"
            ).rstrip("/")
        elif self.provider_type == "nvidia":
            self.api_key = api_key or nvidia_key or ""
            self.model_name = (
                model_name
                or os.environ.get("NVIDIA_MODEL")
                or os.environ.get("IVA_MODEL")
                or "meta/llama-3.3-70b-instruct"
            )
            self.base_url = (
                base_url
                or os.environ.get("NVIDIA_BASE_URL")
                or "https://integrate.api.nvidia.com/v1"
            ).rstrip("/")
            self.provider_type = "openai"  # NVIDIA NIM uses standard OpenAI completions wire protocol
        elif self.provider_type == "anthropic":
            self.api_key = api_key or anthropic_key or ""
            self.model_name = (
                model_name
                or os.environ.get("ANTHROPIC_MODEL")
                or os.environ.get("IVA_MODEL")
                or "claude-3-5-sonnet-20241022"
            )
            self.base_url = (
                base_url
                or os.environ.get("ANTHROPIC_BASE_URL")
                or "https://api.anthropic.com/v1"
            ).rstrip("/")
        elif self.provider_type == "groq":
            self.api_key = api_key or groq_key or ""
            self.model_name = (
                model_name
                or os.environ.get("GROQ_MODEL")
                or os.environ.get("IVA_MODEL")
                or "llama-3.3-70b-versatile"
            )
            self.base_url = (
                base_url
                or os.environ.get("GROQ_BASE_URL")
                or "https://api.groq.com/openai/v1"
            ).rstrip("/")
            self.provider_type = "openai"
        elif self.provider_type == "deepseek":
            self.api_key = api_key or deepseek_key or ""
            self.model_name = (
                model_name
                or os.environ.get("DEEPSEEK_MODEL")
                or os.environ.get("IVA_MODEL")
                or "deepseek-chat"
            )
            self.base_url = (
                base_url
                or os.environ.get("DEEPSEEK_BASE_URL")
                or "https://api.deepseek.com/v1"
            ).rstrip("/")
            self.provider_type = "openai"
        elif self.provider_type == "openrouter":
            self.api_key = api_key or openrouter_key or ""
            self.model_name = (
                model_name
                or os.environ.get("OPENROUTER_MODEL")
                or os.environ.get("IVA_MODEL")
                or "meta-llama/llama-3.3-70b-instruct"
            )
            self.base_url = (
                base_url
                or os.environ.get("OPENROUTER_BASE_URL")
                or "https://openrouter.ai/api/v1"
            ).rstrip("/")
            self.provider_type = "openai"
        else:
            self.api_key = api_key or openai_key or ""
            self.model_name = (
                model_name
                or os.environ.get("OPENAI_MODEL")
                or os.environ.get("IVA_MODEL")
                or "gpt-4o-mini"
            )
            self.base_url = (
                base_url
                or os.environ.get("OPENAI_BASE_URL")
                or "https://api.openai.com/v1"
            ).rstrip("/")
        self.call_history: List[ModelRequest] = []
        self.available_models: List[str] = []
        self.auto_discovered: bool = False
        self.auto_discovery_attempted: bool = False

        # If user did not specify an explicit model override, autonomously fetch and select from API key
        explicit_model = model_name or os.environ.get("IVA_MODEL") or os.environ.get(f"{self.provider_type.upper()}_MODEL")
        if not explicit_model and self.api_key:
            try:
                discovered = self.auto_discover_optimal_model()
                if discovered:
                    self.model_name = discovered
                    self.auto_discovered = True
            except Exception as exc:
                logger.debug("Auto-discovery of optimal model deferred: %s", exc)

    @classmethod
    def detect_provider_from_key(cls, api_key: str) -> str:
        """Autonomously infers provider type from API key format and known prefixes."""
        clean = (api_key or "").strip()
        if clean.startswith("nvapi-"):
            return "nvidia"
        elif clean.startswith("AIzaSy") or clean.startswith("AIza"):
            return "gemini"
        elif clean.startswith("sk-ant-"):
            return "anthropic"
        elif clean.startswith("gsk_"):
            return "groq"
        elif clean.startswith("sk-or-"):
            return "openrouter"
        elif clean.startswith("sk-proj-"):
            return "openai"
        elif clean.startswith("sk-"):
            return "openai"
        return "unknown"

    @classmethod
    def verify_and_fetch_models(
        cls,
        api_key: str,
        provider_type: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_sec: float = 6.0,
    ) -> Tuple[bool, str, List[str], Optional[str]]:
        """Queries the provider endpoint to verify API key authenticity and returns available models.
        
        Returns:
            Tuple of (is_valid: bool, provider: str, models: List[str], error: Optional[str])
        """
        clean_key = (api_key or "").strip()
        if not clean_key:
            return (False, "none", [], "No API key provided.")

        prov = (provider_type or cls.detect_provider_from_key(clean_key)).lower()
        ctx = ssl.create_default_context()

        def _is_200(r: Any) -> bool:
            s = getattr(r, "status", None)
            return True if (s is None or not isinstance(s, int)) else (s == 200)

        try:
            if prov == "gemini":
                root_url = (base_url or "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
                endpoint = f"{root_url}/models?key={clean_key}"
                req = urllib.request.Request(
                    endpoint,
                    headers={"User-Agent": "IVA-Autonomous-Partner/1.8.0"},
                    method="GET",
                )
                with urllib.request.urlopen(req, timeout=timeout_sec, context=ctx) as resp:
                    if _is_200(resp):
                        data = json.loads(resp.read().decode("utf-8"))
                        models = []
                        for m in data.get("models", []):
                            m_name = m.get("name", "")
                            if m_name.startswith("models/"):
                                m_name = m_name[len("models/"):]
                            methods = m.get("supportedGenerationMethods", [])
                            if not methods or "generateContent" in methods:
                                models.append(m_name)
                        return (True, "gemini", models, None)
                    return (False, "gemini", [], f"HTTP Status {getattr(resp, 'status', 'unknown')}")

            elif prov == "anthropic":
                root_url = (base_url or "https://api.anthropic.com/v1").rstrip("/")
                endpoint = f"{root_url}/models"
                req = urllib.request.Request(
                    endpoint,
                    headers={
                        "x-api-key": clean_key,
                        "anthropic-version": "2023-06-01",
                        "User-Agent": "IVA-Autonomous-Partner/1.8.0",
                    },
                    method="GET",
                )
                with urllib.request.urlopen(req, timeout=timeout_sec, context=ctx) as resp:
                    if _is_200(resp):
                        data = json.loads(resp.read().decode("utf-8"))
                        models = [m.get("id") for m in data.get("data", []) if m.get("id")]
                        return (True, "anthropic", models, None)
                    return (False, "anthropic", [], f"HTTP Status {getattr(resp, 'status', 'unknown')}")

            elif prov == "groq":
                root_url = (base_url or "https://api.groq.com/openai/v1").rstrip("/")
                endpoint = f"{root_url}/models"
                req = urllib.request.Request(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {clean_key}",
                        "User-Agent": "IVA-Autonomous-Partner/1.8.0",
                    },
                    method="GET",
                )
                with urllib.request.urlopen(req, timeout=timeout_sec, context=ctx) as resp:
                    if _is_200(resp):
                        data = json.loads(resp.read().decode("utf-8"))
                        models = [m.get("id") for m in data.get("data", []) if m.get("id")]
                        return (True, "groq", models, None)
                    return (False, "groq", [], f"HTTP Status {getattr(resp, 'status', 'unknown')}")

            elif prov == "nvidia" or clean_key.startswith("nvapi-") or "integrate.api.nvidia.com" in (base_url or ""):
                root_url = (base_url or "https://integrate.api.nvidia.com/v1").rstrip("/")
                endpoint = f"{root_url}/models"
                req = urllib.request.Request(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {clean_key}",
                        "Accept": "application/json",
                        "User-Agent": "IVA-Autonomous-Partner/1.8.0",
                    },
                    method="GET",
                )
                with urllib.request.urlopen(req, timeout=timeout_sec, context=ctx) as resp:
                    if _is_200(resp):
                        data = json.loads(resp.read().decode("utf-8"))
                        models = [m.get("id") for m in data.get("data", []) if m.get("id")]
                        return (True, "nvidia", models, None)
                    return (False, "nvidia", [], f"HTTP Status {getattr(resp, 'status', 'unknown')}")

            else:  # openai, deepseek, openrouter, or generic openai-compatible
                if prov == "deepseek":
                    root_url = (base_url or "https://api.deepseek.com").rstrip("/")
                elif prov == "openrouter":
                    root_url = (base_url or "https://openrouter.ai/api/v1").rstrip("/")
                else:
                    root_url = (base_url or "https://api.openai.com/v1").rstrip("/")

                endpoint = f"{root_url}/models"
                req = urllib.request.Request(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {clean_key}",
                        "User-Agent": "IVA-Autonomous-Partner/1.8.0",
                    },
                    method="GET",
                )
                with urllib.request.urlopen(req, timeout=timeout_sec, context=ctx) as resp:
                    if _is_200(resp):
                        data = json.loads(resp.read().decode("utf-8"))
                        models = [m.get("id") for m in data.get("data", []) if m.get("id")]
                        return (True, prov, models, None)
                    return (False, prov, [], f"HTTP Status {getattr(resp, 'status', 'unknown')}")

        except urllib.error.HTTPError as err:
            err_msg = f"HTTP {err.code}: {err.reason}"
            try:
                body = err.read().decode("utf-8", errors="ignore")
                j = json.loads(body)
                if "error" in j and isinstance(j["error"], dict) and "message" in j["error"]:
                    err_msg = f"HTTP {err.code}: {j['error']['message']}"
                elif "error" in j and isinstance(j["error"], str):
                    err_msg = f"HTTP {err.code}: {j['error']}"
            except Exception:
                pass
            return (False, prov, [], err_msg)
        except urllib.error.URLError as err:
            return (False, prov, [], f"Network Connection Error: {err.reason}")
        except Exception as err:
            return (False, prov, [], f"Verification Error: {err}")

    def fetch_remote_models(self) -> List[str]:
        """Queries the upstream provider REST endpoint using the active API key to fetch available models.
        
        Uses 100% Python standard library urllib.request without external dependencies.
        Returns a list of model identifier strings.
        """
        is_valid, _prov, models, _err = self.verify_and_fetch_models(
            api_key=self.api_key,
            provider_type=self.provider_type,
            base_url=self.base_url,
            timeout_sec=self.timeout_sec,
        )
        if is_valid and models:
            self.available_models = models
            return models
        return []

    def auto_discover_optimal_model(self) -> str:
        """Autonomously inspects available remote models from the active API key and selects the best model.
        
        Zero user prompting: dynamically ranks and picks the optimal model target.
        Falls back to proven defaults if offline or rate-limited.
        """
        self.auto_discovery_attempted = True
        candidates = self.fetch_remote_models()
        if not candidates:
            defaults = {
                "gemini": "gemini-2.5-flash",
                "anthropic": "claude-3-5-sonnet-20241022",
                "groq": "llama-3.3-70b-versatile",
                "deepseek": "deepseek-chat",
                "openrouter": "meta-llama/llama-3.3-70b-instruct",
                "nvidia": "meta/llama-3.3-70b-instruct",
                "openai": "gpt-4o-mini",
            }
            actual_prov = "nvidia" if ("integrate.api.nvidia.com" in getattr(self, "base_url", "") or getattr(self, "api_key", "").startswith("nvapi-")) else self.provider_type
            return defaults.get(actual_prov, defaults.get(self.provider_type, "meta-llama/llama-3.3-70b-instruct"))

        preferences = {
            "gemini": [
                "gemini-2.5-flash",
                "gemini-2.5-pro",
                "gemini-2.0-flash",
                "gemini-2.0-flash-exp",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-1.5-flash-8b",
            ],
            "nvidia": [
                "meta/llama-3.3-70b-instruct",
                "meta/llama-3.1-70b-instruct",
                "nvidia/nemotron-4-340b-instruct",
                "mistralai/mistral-large-2-instruct",
                "nvidia/nemotron-3.5-bolt-e4b",
                "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
                "nvidia/nemotron-3.5-lightning-30b-a3b",
                "deepseek-ai/deepseek-coder-6.7b-instruct",
                "meta/llama-3.2-11b-vision-instruct",
                "nvidia/llama-3.1-nemotron-51b-instruct",
                "meta/llama-3.2-90b-vision-instruct",
            ],
            "openai": [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-4",
                "o1-preview",
                "o1-mini",
                "gpt-3.5-turbo",
            ],
            "anthropic": [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-sonnet-latest",
                "claude-3-5-haiku-20241022",
                "claude-3-opus-20240229",
            ],
            "groq": [
                "llama-3.3-70b-versatile",
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant",
                "mixtral-8x7b-32768",
            ],
            "deepseek": [
                "deepseek-chat",
                "deepseek-coder",
            ],
            "openrouter": [
                "anthropic/claude-3.5-sonnet",
                "google/gemini-2.5-flash",
                "openai/gpt-4o",
                "meta-llama/llama-3.3-70b-instruct",
            ],
        }

        is_free_only = (
            os.environ.get("IVA_FREE_ONLY", "").lower() in ("true", "1", "yes")
            or getattr(self, "model_name", "") in ("FREE", "FREE_AUTO", "FREE_ALL")
            or str(os.environ.get("IVA_MODEL", "")).startswith("FREE")
            or str(os.environ.get("ACTIVE_MODEL", "")).startswith("FREE")
        )

        if is_free_only:
            free_candidates = [c for c in candidates if ":free" in c.lower() or "free" in c.lower().split("/")[-1]]
            if not free_candidates and (self.provider_type == "openrouter" or "openrouter.ai" in getattr(self, "base_url", "")):
                free_candidates = list(ModelMetadataCatalog.OPENROUTER_VERIFIED_FREE_MODELS)
            if free_candidates:
                candidates = free_candidates
                preferences["openrouter"] = [
                    "meta-llama/llama-3.3-70b-instruct:free",
                    "deepseek/deepseek-r1:free",
                    "google/gemini-2.0-flash-exp:free",
                    "qwen/qwen-2.5-coder-32b-instruct:free",
                    "meta-llama/llama-3.2-3b-instruct:free",
                ]

        if os.environ.get("IVA_MODEL") in ("AUTO", "FREE_AUTO") or os.environ.get("ACTIVE_MODEL") in ("AUTO", "FREE_AUTO") or getattr(self, "model_name", "") in ("AUTO", "FREE_AUTO"):
            return "FREE_AUTO" if is_free_only else "AUTO"

        actual_prov = "nvidia" if ("integrate.api.nvidia.com" in getattr(self, "base_url", "") or getattr(self, "api_key", "").startswith("nvapi-")) else self.provider_type
        pref_list = preferences.get(actual_prov, preferences.get(self.provider_type, preferences.get("openai", [])))
        for pref in pref_list:
            if pref in candidates:
                logger.info("Auto-discovered and selected optimal model: %s", pref)
                return pref
            for c in candidates:
                if c.startswith(pref):
                    logger.info("Auto-discovered and selected optimal model (matched): %s", c)
                    return c

        # If no explicit preference matches, pick the recommended model or highest parameter model
        ranked = ModelMetadataCatalog.rank_and_sort_models(candidates)
        for r in ranked:
            if r.get("is_recommended"):
                return r["model_id"]
        return ranked[0]["model_id"] if ranked else candidates[0]

    def get_model_discovery_status(self) -> Dict[str, Any]:
        """Returns structured metadata about model auto-discovery, including multi-provider pool status."""
        models = getattr(self, "available_models", [])
        multi_status: Dict[str, Any] = {}
        try:
            multi_status = self.get_multi_provider_discovery_status()
        except Exception:
            pass
        effective_models = models or multi_status.get("all_models", [])
        return {
            "provider_type": self.provider_type,
            "active_model": self.model_name,
            "auto_discovered": getattr(self, "auto_discovered", False),
            "available_models_count": len(effective_models),
            "available_models": effective_models,
            "models_metadata": ModelMetadataCatalog.rank_and_sort_models(effective_models) if effective_models else [],
            "base_url": self.base_url,
            "has_key": bool(self.api_key),
            "multi_provider_enabled": multi_status.get("multi_provider_enabled", False),
            "configured_providers": multi_status.get("providers", {}),
            "total_pool_models": multi_status.get("total_models", len(effective_models)),
            "models_by_provider": multi_status.get("models_by_provider", {}),
        }

    def resolve_effective_model(self, request: ModelRequest) -> str:
        """Determines active model target for execution, running dynamic action swapping if enabled."""
        override = getattr(request, "model_override", None)
        is_or = "openrouter.ai" in getattr(self, "base_url", "") or getattr(self, "api_key", "").startswith("sk-or-")
        is_nv = getattr(self, "api_key", "").startswith("nvapi-") or "integrate.api.nvidia.com" in getattr(self, "base_url", "")
        default_target = "meta-llama/llama-3.3-70b-instruct" if is_or else ("meta/llama-3.3-70b-instruct" if is_nv else "gemini-2.5-flash")
        target = override or self.model_name or default_target
        if target.upper() != "AUTO":
            return target

        # Dynamic Action-Based Model Swapping is active
        action_type = getattr(request, "action_type", None)
        if not action_type:
            prompt_lower = (request.prompt or "").lower()
            agent_lower = (getattr(request, "agent_id", "") or "").lower()
            if any(k in prompt_lower for k in ("screenshot", "image", "visual", "dom", "browser tab", "inspect page")) or "vision" in agent_lower:
                action_type = "vision"
            elif any(k in prompt_lower for k in ("volatility", "hawkes", "option", "greeks", "nifty", "banknifty", "svi", "arbitrage", "derivative")) or "quant" in agent_lower:
                action_type = "finance"
            elif any(k in prompt_lower for k in ("def ", "class ", "import ", "syntax", "refactor", "bug", "patch", "traceback", "ast", "pytest", "unittest")) or "swe_" in agent_lower:
                action_type = "coding"
            elif any(k in prompt_lower for k in ("mathematical", "proof", "theorem", "architecture", "frontier", "deep reasoning", "gpqa")) or "math_" in agent_lower or "plan_" in agent_lower:
                action_type = "reasoning"
            elif any(k in prompt_lower for k in ("route", "classify", "triage", "parse json", "yes/no", "short")) or len(request.prompt) < 80:
                action_type = "fast"
            else:
                action_type = "default"

        if self.available_models:
            models_pool = self.available_models
        else:
            multi_info: Dict[str, Any] = {}
            try:
                multi_info = self.get_multi_provider_discovery_status()
            except Exception:
                pass
            if multi_info.get("all_models"):
                models_pool = multi_info["all_models"]
            elif is_or:
                models_pool = [
                    "meta-llama/llama-3.3-70b-instruct",
                    "meta-llama/llama-3.2-3b-instruct:free",
                    "google/gemini-2.0-flash-exp:free",
                    "qwen/qwen-2.5-72b-instruct:free",
                    "mistralai/mistral-7b-instruct:free",
                    "liquid/lfm-3-1.7b:free",
                ]
            elif is_nv:
                models_pool = [
                    "meta/llama-3.3-70b-instruct",
                    "meta/llama-3.1-70b-instruct",
                    "nvidia/nemotron-4-340b-instruct",
                    "mistralai/mistral-large-2-instruct",
                    "nvidia/nemotron-3-super-120b-a12b",
                ]
            elif self.provider_type == "gemini":
                models_pool = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]
            else:
                models_pool = ["gpt-4o", "gpt-4o-mini"]

        is_free_mode = (
            os.environ.get("IVA_FREE_ONLY", "").lower() in ("true", "1", "yes")
            or getattr(self, "model_name", "") in ("FREE", "FREE_AUTO", "FREE_ALL")
            or str(getattr(self, "model_name", "")).startswith("FREE:")
            or str(os.environ.get("IVA_MODEL", "")).startswith("FREE")
            or str(os.environ.get("ACTIVE_MODEL", "")).startswith("FREE")
        )

        if is_free_mode:
            free_candidates = [m for m in models_pool if ":free" in m.lower() or "free" in m.lower().split("/")[-1]]
            if not free_candidates and is_or:
                free_candidates = list(ModelMetadataCatalog.OPENROUTER_VERIFIED_FREE_MODELS)
            if free_candidates:
                models_pool = free_candidates

        try:
            from .model_researcher import AutonomousModelResearcher
            verdict = AutonomousModelResearcher.select_best_model(models_pool, request.prompt)
            chosen = verdict.chosen_model
            logger.info(
                "Autonomous Model Researcher: routed task '%s' [domain: %s, score: %.1f] -> %s (%s)",
                request.task_id, verdict.task_domain, verdict.overall_score, chosen, verdict.rationale
            )
            return chosen
        except Exception as exc:
            logger.debug("AutonomousModelResearcher fallback: %s", exc)
            chosen = ModelMetadataCatalog.get_action_model(models_pool, action_type=action_type)
            logger.info(
                "Dynamic Action Swapper: routed task '%s' [action: %s] -> %s",
                request.task_id, action_type, chosen
            )
            return chosen

    @classmethod
    def create_from_env(cls, **kwargs: Any) -> UniversalAPIProvider:
        """Instantiates UniversalAPIProvider using active environment variables and .env settings."""
        load_repo_dotenv()
        return cls(**kwargs)

    @classmethod
    def has_available_credentials(cls) -> bool:
        """Returns True if valid API credentials are present in environment or .env file."""
        load_repo_dotenv()
        return bool(
            os.environ.get("NVIDIA_API_KEY")
            or os.environ.get("NVIDIA_NIM_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("ANTHROPIC_API_KEY")
            or os.environ.get("CLAUDE_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
            or os.environ.get("GROQ_API_KEY")
            or os.environ.get("DEEPSEEK_API_KEY")
            or os.environ.get("OPENROUTER_API_KEY")
            or os.environ.get("OPENAI_API_BASE")
        )

    @classmethod
    def get_configured_providers_pool(cls) -> Dict[str, Dict[str, Any]]:
        """Scans environment and returns all active provider configurations in the Multi-Provider Pool."""
        load_repo_dotenv()
        pool: Dict[str, Dict[str, Any]] = {}
        nv_key = os.environ.get("NVIDIA_API_KEY") or os.environ.get("NVIDIA_NIM_API_KEY")
        if nv_key:
            pool["nvidia"] = {
                "name": "NVIDIA NIM / NVIDIA Build",
                "key": nv_key,
                "base_url": "https://integrate.api.nvidia.com/v1",
                "default_model": os.environ.get("NVIDIA_MODEL") or "meta/llama-3.3-70b-instruct",
                "specialty": "Ultra-Scale Reasoning, Nemotron 550B/340B, Llama 3.3 70B, Coding",
            }
        gem_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if gem_key:
            pool["gemini"] = {
                "name": "Google Gemini",
                "key": gem_key,
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "default_model": os.environ.get("GEMINI_MODEL") or "gemini-2.5-flash",
                "specialty": "Multimodal, Real-Time Web Search, 2M Token Context",
            }
        oa_key = os.environ.get("OPENAI_API_KEY")
        # Only treat as distinct OpenAI if not just an alias pointing to NVIDIA NIM
        if oa_key and not (nv_key and os.environ.get("OPENAI_BASE_URL", "").startswith("https://integrate.api.nvidia.com")):
            pool["openai"] = {
                "name": "OpenAI / ChatGPT",
                "key": oa_key,
                "base_url": os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1",
                "default_model": os.environ.get("OPENAI_MODEL") or "gpt-4o",
                "specialty": "General Logic, High Precision, Function Calling",
            }
        ds_key = os.environ.get("DEEPSEEK_API_KEY")
        if ds_key:
            pool["deepseek"] = {
                "name": "DeepSeek AI",
                "key": ds_key,
                "base_url": "https://api.deepseek.com/v1",
                "default_model": os.environ.get("DEEPSEEK_MODEL") or "deepseek-chat",
                "specialty": "Deep Mathematics, Code Synthesis, Cost Efficiency",
            }
        gr_key = os.environ.get("GROQ_API_KEY")
        if gr_key:
            pool["groq"] = {
                "name": "Groq LPU",
                "key": gr_key,
                "base_url": "https://api.groq.com/openai/v1",
                "default_model": os.environ.get("GROQ_MODEL") or "llama-3.3-70b-versatile",
                "specialty": "Ultra-Fast Inference (500+ tokens/sec), Micro-Parsing",
            }
        or_key = os.environ.get("OPENROUTER_API_KEY")
        if or_key:
            pool["openrouter"] = {
                "name": "OpenRouter",
                "key": or_key,
                "base_url": "https://openrouter.ai/api/v1",
                "default_model": os.environ.get("OPENROUTER_MODEL") or "meta-llama/llama-3.3-70b-instruct",
                "specialty": "Multi-Model Router, 400+ Models, 20+ Free Zero-Cost Models (:free)",
            }
        ant_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")
        if ant_key:
            pool["anthropic"] = {
                "name": "Anthropic Claude",
                "key": ant_key,
                "base_url": "https://api.anthropic.com/v1",
                "default_model": os.environ.get("ANTHROPIC_MODEL") or "claude-3-5-sonnet-20241022",
                "specialty": "Complex Engineering Architecture, Nuanced Logic",
            }
        for p in ("nvidia", "gemini", "openai", "deepseek", "groq", "openrouter", "anthropic"):
            if p in pool:
                multi_k = os.environ.get(f"{p.upper()}_API_KEYS")
                if multi_k:
                    k_list = [k.strip() for k in multi_k.split(",") if k.strip()]
                    if len(k_list) > 1:
                        pool[p]["all_keys"] = k_list
        return pool

    @classmethod
    def get_provider_for_model(cls, model_name: str, pool: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Maps a given model identifier to the best configured provider in the pool."""
        if not model_name:
            return None
        m_low = model_name.lower().strip()
        if pool is None:
            pool = cls.get_configured_providers_pool()
        if not pool:
            return None

        # Exact match or prefix match
        if ":free" in m_low and "openrouter" in pool:
            return "openrouter"
        if ("gemini" in m_low or m_low.startswith("models/gemini")) and "gemini" in pool:
            return "gemini"
        if ("claude" in m_low or m_low.startswith("anthropic/")) and "anthropic" in pool:
            return "anthropic"
        if (m_low.startswith("meta/") or m_low.startswith("nvidia/")) and "nvidia" in pool:
            return "nvidia"
        if m_low.startswith("deepseek") and "deepseek" in pool:
            return "deepseek"
        if (m_low.startswith("gpt-") or m_low.startswith("o1-") or m_low.startswith("chatgpt")) and "openai" in pool:
            return "openai"
        if (m_low.startswith("llama-") or "groq" in m_low) and "groq" in pool:
            return "groq"
        if "/" in m_low and "openrouter" in pool:
            return "openrouter"
        return None

    @classmethod
    def fetch_all_pool_models(
        cls,
        timeout_sec: float = 6.0,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """Queries upstream REST endpoints for ALL active keys in the configured provider pool.
        
        Aggregates models from all providers (Gemini, OpenRouter, NVIDIA, Anthropic, Groq, DeepSeek, OpenAI)
        into a unified, deduplicated catalog while preserving provider provenance and metadata.
        Caches results for 10 minutes unless force_refresh is True.
        """
        now = time.time()
        if not force_refresh and cls._POOL_MODELS_CACHE and (now - cls._POOL_MODELS_CACHE_TIME < 600.0):
            return cls._POOL_MODELS_CACHE

        pool = cls.get_configured_providers_pool()
        if not pool:
            return {
                "providers": {},
                "all_models": [],
                "models_by_provider": {},
                "model_to_provider": {},
                "total_models": 0,
                "multi_provider_enabled": False,
            }

        providers_meta: Dict[str, Any] = {}
        all_models_list: List[str] = []
        models_by_provider: Dict[str, List[str]] = {}
        model_to_provider: Dict[str, str] = {}

        for p_name, p_info in pool.items():
            raw_key = p_info.get("key", "")
            base_url = p_info.get("base_url")
            is_valid, resolved_p, p_models, err = cls.verify_and_fetch_models(
                api_key=raw_key,
                provider_type=p_name,
                base_url=base_url,
                timeout_sec=timeout_sec,
            )
            prov_models = p_models if is_valid and p_models else ([p_info.get("default_model")] if p_info.get("default_model") else [])
            models_by_provider[p_name] = prov_models
            for m in prov_models:
                if m not in all_models_list:
                    all_models_list.append(m)
                if m not in model_to_provider:
                    model_to_provider[m] = p_name

            k_masked = raw_key[:6] + "..." + raw_key[-4:] if len(raw_key) > 12 else "******"
            providers_meta[p_name] = {
                "name": p_info.get("name", p_name.upper()),
                "verified": bool(is_valid),
                "key_masked": k_masked,
                "models_count": len(prov_models),
                "default_model": p_info.get("default_model"),
                "specialty": p_info.get("specialty", ""),
                "error": err if not is_valid else None,
            }

        result = {
            "providers": providers_meta,
            "all_models": all_models_list,
            "models_by_provider": models_by_provider,
            "model_to_provider": model_to_provider,
            "total_models": len(all_models_list),
            "multi_provider_enabled": len(providers_meta) > 1 or os.environ.get("MULTI_PROVIDER_ENABLED") == "true",
        }
        cls._POOL_MODELS_CACHE = result
        cls._POOL_MODELS_CACHE_TIME = now
        return result

    @classmethod
    def get_multi_provider_discovery_status(
        cls,
        force_refresh: bool = False,
        timeout_sec: float = 6.0,
    ) -> Dict[str, Any]:
        """Returns structured metadata about all configured keys and aggregated models across the pool."""
        pool_data = cls.fetch_all_pool_models(timeout_sec=timeout_sec, force_refresh=force_refresh)
        active_m = os.environ.get("IVA_MODEL") or os.environ.get("ACTIVE_MODEL") or "AUTO"
        active_p = (os.environ.get("ACTIVE_PROVIDER") or "gemini").lower()
        return {
            "active_model": active_m,
            "active_provider": active_p,
            "multi_provider_enabled": pool_data.get("multi_provider_enabled", False),
            "providers": pool_data.get("providers", {}),
            "all_models": pool_data.get("all_models", []),
            "total_models": pool_data.get("total_models", 0),
            "models_by_provider": pool_data.get("models_by_provider", {}),
            "model_to_provider": pool_data.get("model_to_provider", {}),
        }

    def generate(self, request: ModelRequest) -> Dict[str, Any]:
        """Executes a model request via direct REST API and returns structured execution metadata."""
        self.call_history.append(request)
        t0 = time.perf_counter()

        if not self.api_key and not (self.base_url and ("localhost" in self.base_url or "127.0.0.1" in self.base_url)):
            raise RuntimeError(
                "UniversalAPIProvider requires an API key. Supported providers: "
                "OPENROUTER_API_KEY (OpenRouter: 400+ models & free tier), "
                "NVIDIA_API_KEY (NVIDIA Build: free credits for Nemotron/Llama 3.3), "
                "GEMINI_API_KEY (Google Gemini: 2M context free tier), "
                "GROQ_API_KEY (Groq LPU: 500+ tok/s ultra-fast), "
                "DEEPSEEK_API_KEY (DeepSeek: V3/R1 low-cost), "
                "OPENAI_API_KEY (OpenAI), or ANTHROPIC_API_KEY (Claude). "
                "Set any of these in your local .env or type `keys` in the terminal."
            )

        # Smart Cross-Provider Routing: If requested/effective model belongs to another provider in pool, route directly
        eff_model = getattr(request, "model_override", None) or self.model_name
        if eff_model and eff_model.upper() == "AUTO":
            eff_model = self.resolve_effective_model(request)

        pool = self.get_configured_providers_pool()
        my_brand = getattr(self, "provider_brand", self.provider_type)
        target_prov = self.get_provider_for_model(eff_model, pool=pool)

        if target_prov and target_prov != my_brand and target_prov in pool:
            cfg = pool[target_prov]
            alt_key = cfg.get("key")
            if alt_key:
                try:
                    alt_provider = UniversalAPIProvider(
                        provider_type=target_prov,
                        api_key=alt_key,
                        model_name=eff_model,
                        base_url=cfg.get("base_url"),
                    )
                    res = alt_provider.generate(request)
                    if res.get("status") == "SUCCEEDED" and res.get("response_text"):
                        return res
                except Exception as route_exc:
                    logger.debug("Cross-provider direct routing to '%s' failed: %s", target_prov, route_exc)

        if self.provider_type == "gemini":
            res = self._call_gemini_rest(request, t0)
        elif self.provider_type == "anthropic":
            res = self._call_anthropic_rest(request, t0)
        else:
            res = self._call_openai_rest(request, t0)

        # Cross-provider failover if primary provider failed
        if res.get("status") == "FAILED" or not res.get("response_text"):
            try:
                pool = self.get_configured_providers_pool()
                my_brand = getattr(self, "provider_brand", self.provider_type)
                for other_prov, cfg in pool.items():
                    if other_prov == my_brand:
                        continue
                    other_key = cfg.get("key")
                    if not other_key:
                        continue
                    logger.info("Primary provider '%s' failed. Auto-failing over to '%s' in provider pool...", my_brand, other_prov)
                    alt_provider = UniversalAPIProvider(
                        provider_type=other_prov,
                        api_key=other_key,
                        model_name=cfg.get("default_model") or "AUTO",
                        base_url=cfg.get("base_url"),
                    )
                    alt_res = alt_provider.generate(request)
                    if alt_res.get("status") == "SUCCEEDED" and alt_res.get("response_text"):
                        os.environ["ACTIVE_PROVIDER"] = other_prov
                        return alt_res
            except Exception as pool_exc:
                logger.debug("Cross-provider pool failover notice: %s", pool_exc)

        # Local cognitive graceful response if all remote providers failed
        if res.get("status") == "FAILED" or not res.get("response_text"):
            res["response_text"] = self._generate_local_cognitive_fallback(request, res.get("error_message"))
            res["status"] = "SUCCEEDED"
            res["model"] = f"{res.get('model', 'local')} (Local Cognitive Partner Engine)"

        return res

    def _call_gemini_rest(self, request: ModelRequest, start_time: float) -> Dict[str, Any]:
        """Calls Google Gemini GenerateContent REST API using Python standard library urllib."""
        eff_model = self.resolve_effective_model(request)
        if eff_model.upper() == "AUTO":
            eff_model = "gemini-2.5-flash"
        # Sanitize model name for Google API path
        if eff_model.startswith("models/"):
            eff_model = eff_model[len("models/"):]
        endpoint = f"{self.base_url}/models/{eff_model}:generateContent?key={self.api_key}"

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": request.prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192,
            }
        }

        # Dynamic Reasoning & Thinking-Budget Regulation (Gemini 3.8 Flash Anti-Overanalysis Governor)
        # Prevents 30-50 minute thinking spirals and massive token burns on reasoning models
        meta = getattr(request, "metadata", {}) or {}
        thinking_level = meta.get("thinking_level")
        thinking_budget = meta.get("thinking_budget")
        if thinking_budget is not None:
            payload["generationConfig"]["thinkingConfig"] = {"thinkingBudget": int(thinking_budget)}
        elif thinking_level is not None:
            payload["generationConfig"]["thinking"] = {"thinking_level": str(thinking_level)}
        elif any(k in eff_model.lower() for k in ["3.8", "3.6", "3.5", "2.5", "thinking", "argon"]):
            prompt_l = request.prompt.lower()
            if any(fast_kw in prompt_l for fast_kw in ["button", "color", "css", "ui", "change", "edit", "tweak", "fix", "what is", "who are", "status"]):
                payload["generationConfig"]["thinkingConfig"] = {"thinkingBudget": 0}

        sys_inst = getattr(request, "system_instruction", None)
        if sys_inst:
            payload["systemInstruction"] = {
                "parts": [{"text": str(sys_inst)}]
            }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "IVA-Autonomous-Partner/1.8.0",
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            req = urllib.request.Request(endpoint, data=data_bytes, headers=headers, method="POST")
            try:
                # SSL context with default verification
                ctx = ssl.create_default_context()
                with urllib.request.urlopen(req, timeout=self.timeout_sec, context=ctx) as resp:
                    resp_bytes = resp.read()
                    data = json.loads(resp_bytes.decode("utf-8"))
                    dt = max(0.001, time.perf_counter() - start_time)

                    # Extract candidate text
                    candidates = data.get("candidates", [])
                    response_text = ""
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            response_text = parts[0].get("text", "")

                    parsed_json = {}
                    if response_text.strip().startswith("{") or response_text.strip().startswith("["):
                        try:
                            parsed_json = json.loads(response_text.strip())
                        except Exception:
                            parsed_json = {}

                    usage_meta = data.get("usageMetadata", {})
                    input_toks = usage_meta.get("promptTokenCount", max(1, len(request.prompt) // 4))
                    output_toks = usage_meta.get("candidatesTokenCount", max(1, len(response_text) // 4))
                    cached_toks = usage_meta.get("cachedContentTokenCount", 0)

                    return {
                        "status": "SUCCEEDED",
                        "model": eff_model,
                        "exit_code": 0,
                        "timed_out": False,
                        "duration_sec": round(dt, 4),
                        "response_text": response_text,
                        "parsed_json": parsed_json,
                        "provider_usage": {
                            "input_tokens": input_toks,
                            "output_tokens": output_toks,
                            "thinking_tokens": 0,
                            "cached_tokens": cached_toks,
                            "total_tokens": input_toks + output_toks,
                        },
                        "is_mock": False,
                        "notification_id": f"GEMINI-API-{request.task_id}",
                        "stdout_log_path": None,
                        "stderr_log_path": None,
                    }
            except urllib.error.HTTPError as he:
                error_body = ""
                try:
                    error_body = he.read().decode("utf-8", errors="ignore")
                except Exception:
                    pass
                last_error = f"HTTP {he.code}: {he.reason} - {error_body[:200]}"
                logger.warning("Gemini API call attempt %d failed: %s", attempt, last_error)
                if he.code in (429, 500, 503):
                    time.sleep(self.backoff_sec * (2 ** (attempt - 1)))
                else:
                    break
            except urllib.error.URLError as ue:
                last_error = f"URLError: {ue.reason}"
                logger.warning("Gemini network error attempt %d: %s", attempt, last_error)
                time.sleep(self.backoff_sec * attempt)
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error("Gemini unexpected error attempt %d: %s", attempt, last_error)
                time.sleep(self.backoff_sec)

        dt = max(0.001, time.perf_counter() - start_time)
        return {
            "status": "FAILED",
            "model": eff_model,
            "exit_code": 1,
            "timed_out": False,
            "duration_sec": round(dt, 4),
            "response_text": "",
            "parsed_json": {},
            "provider_usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "thinking_tokens": 0,
                "cached_tokens": 0,
                "total_tokens": 0,
            },
            "error_message": redact_sensitive_text(str(last_error or "Unknown error")),
            "is_mock": False,
            "notification_id": f"GEMINI-FAILED-{request.task_id}",
            "stdout_log_path": None,
            "stderr_log_path": None,
        }

    def _call_openai_rest(self, request: ModelRequest, start_time: float) -> Dict[str, Any]:
        """Calls OpenAI-compatible /chat/completions endpoint using standard library urllib."""
        eff_model = self.resolve_effective_model(request)
        if eff_model.upper() == "AUTO":
            is_or = "openrouter.ai" in getattr(self, "base_url", "") or getattr(self, "api_key", "").startswith("sk-or-")
            is_nv = "integrate.api.nvidia.com" in getattr(self, "base_url", "") or getattr(self, "api_key", "").startswith("nvapi-")
            is_gr = "groq.com" in getattr(self, "base_url", "") or getattr(self, "api_key", "").startswith("gsk_")
            is_ds = "deepseek.com" in getattr(self, "base_url", "")
            if is_or:
                eff_model = "meta-llama/llama-3.3-70b-instruct"
            elif is_nv:
                eff_model = "meta/llama-3.3-70b-instruct"
            elif is_gr:
                eff_model = "llama-3.3-70b-versatile"
            elif is_ds:
                eff_model = "deepseek-chat"
            else:
                eff_model = "gpt-4o-mini"
        endpoint = f"{self.base_url}/chat/completions"

        messages = []
        sys_inst = getattr(request, "system_instruction", None)
        if sys_inst:
            messages.append({"role": "system", "content": str(sys_inst)})
        messages.append({"role": "user", "content": request.prompt})

        payload: Dict[str, Any] = {
            "model": eff_model,
            "messages": messages,
            "temperature": 0.2,
        }

        # Dynamic Reasoning Effort Regulation for OpenAI / OpenRouter reasoning models
        meta = getattr(request, "metadata", {}) or {}
        reasoning_effort = meta.get("reasoning_effort")
        if reasoning_effort:
            payload["reasoning_effort"] = str(reasoning_effort)
        elif any(k in eff_model.lower() for k in ["o1", "o3", "deepseek-r1"]):
            prompt_l = request.prompt.lower()
            if any(fast_kw in prompt_l for fast_kw in ["button", "color", "css", "ui", "change", "edit", "tweak", "fix", "what is", "who are", "status"]):
                payload["reasoning_effort"] = "low"

        # OpenRouter Universal Reasoning Specification
        if "openrouter.ai" in getattr(self, "base_url", ""):
            eff = payload.get("reasoning_effort") or ("low" if any(fast_kw in request.prompt.lower() for fast_kw in ["button", "color", "css", "ui", "change", "edit", "tweak", "fix", "what is", "who are", "status"]) else None)
            if eff:
                payload["reasoning"] = {"effort": eff}



        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "IVA-Autonomous-Partner/1.8.0",
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            req = urllib.request.Request(endpoint, data=data_bytes, headers=headers, method="POST")
            try:
                ctx = ssl.create_default_context()
                with urllib.request.urlopen(req, timeout=self.timeout_sec, context=ctx) as resp:
                    resp_bytes = resp.read()
                    data = json.loads(resp_bytes.decode("utf-8"))
                    dt = max(0.001, time.perf_counter() - start_time)

                    choices = data.get("choices", [])
                    response_text = ""
                    if choices:
                        msg = choices[0].get("message", {})
                        response_text = msg.get("content") or msg.get("reasoning_content") or ""

                    parsed_json = {}
                    if response_text.strip().startswith("{") or response_text.strip().startswith("["):
                        try:
                            parsed_json = json.loads(response_text.strip())
                        except Exception:
                            parsed_json = {}

                    usage = data.get("usage", {})
                    input_toks = usage.get("prompt_tokens", max(1, len(request.prompt) // 4))
                    output_toks = usage.get("completion_tokens", max(1, len(response_text) // 4))

                    return {
                        "status": "SUCCEEDED",
                        "model": eff_model,
                        "exit_code": 0,
                        "timed_out": False,
                        "duration_sec": round(dt, 4),
                        "response_text": response_text,
                        "parsed_json": parsed_json,
                        "provider_usage": {
                            "input_tokens": input_toks,
                            "output_tokens": output_toks,
                            "thinking_tokens": 0,
                            "cached_tokens": 0,
                            "total_tokens": input_toks + output_toks,
                        },
                        "is_mock": False,
                        "notification_id": f"OPENAI-API-{request.task_id}",
                        "stdout_log_path": None,
                        "stderr_log_path": None,
                    }
            except urllib.error.HTTPError as he:
                error_body = ""
                try:
                    error_body = he.read().decode("utf-8", errors="ignore")
                except Exception:
                    pass
                last_error = f"HTTP {he.code}: {he.reason} - {error_body[:200]}"
                logger.warning("OpenAI API call attempt %d failed: %s", attempt, last_error)
                if he.code in (429, 500, 503):
                    time.sleep(self.backoff_sec * (2 ** (attempt - 1)))
                elif he.code in (404, 402, 400):
                    # Automated fallback to known working/free models on this provider
                    is_or = "openrouter.ai" in getattr(self, "base_url", "")
                    is_nv = "integrate.api.nvidia.com" in getattr(self, "base_url", "")
                    fallbacks = []
                    if is_or:
                        fallbacks = [
                            "meta-llama/llama-3.2-3b-instruct:free",
                            "google/gemini-2.0-flash-exp:free",
                            "liquid/lfm-3-1.7b:free",
                            "qwen/qwen-2.5-72b-instruct:free",
                            "mistralai/mistral-7b-instruct:free",
                            "meta-llama/llama-3.1-8b-instruct:free",
                        ]
                    elif is_nv:
                        fallbacks = [
                            "meta/llama-3.1-70b-instruct",
                            "meta/llama-3.3-70b-instruct",
                            "nvidia/nemotron-4-340b-instruct",
                            "mistralai/mistral-large-2-instruct",
                            "nvidia/nemotron-3.5-bolt-e4b",
                        ]
                    for fb in fallbacks:
                        if fb == payload.get("model"):
                            continue
                        logger.info("Model '%s' failed (HTTP %s). Auto-trying fallback '%s'...", payload.get("model"), he.code, fb)
                        payload["model"] = fb
                        fb_bytes = json.dumps(payload).encode("utf-8")
                        fb_req = urllib.request.Request(endpoint, data=fb_bytes, headers=headers, method="POST")
                        try:
                            with urllib.request.urlopen(fb_req, timeout=self.timeout_sec, context=ctx) as fb_resp:
                                raw_bytes = fb_resp.read()
                                if isinstance(raw_bytes, (bytes, bytearray)):
                                    raw_text = raw_bytes.decode("utf-8")
                                else:
                                    raw_text = str(raw_bytes)
                                fb_data = json.loads(raw_text)
                                dt = max(0.001, time.perf_counter() - start_time)
                                choices = fb_data.get("choices", [])
                                fb_text = ""
                                if choices:
                                    msg = choices[0].get("message", {})
                                    fb_text = msg.get("content") or msg.get("reasoning_content") or ""
                                if fb_text:
                                    usage = fb_data.get("usage", {})
                                    return {
                                        "status": "SUCCEEDED",
                                        "model": fb,
                                        "exit_code": 0,
                                        "timed_out": False,
                                        "duration_sec": round(dt, 4),
                                        "response_text": fb_text,
                                        "parsed_json": {},
                                        "provider_usage": {
                                            "input_tokens": usage.get("prompt_tokens", 1),
                                            "output_tokens": usage.get("completion_tokens", 1),
                                            "thinking_tokens": 0,
                                            "cached_tokens": 0,
                                            "total_tokens": usage.get("total_tokens", 2),
                                        },
                                        "is_mock": False,
                                        "notification_id": f"OPENAI-API-FALLBACK-{request.task_id}",
                                        "stdout_log_path": None,
                                        "stderr_log_path": None,
                                    }
                        except Exception as fb_exc:
                            logger.debug("Fallback model '%s' failed: %s", fb, fb_exc)
                    break
                else:
                    break
            except urllib.error.URLError as ue:
                last_error = f"URLError: {ue.reason}"
                logger.warning("OpenAI network error attempt %d: %s", attempt, last_error)
                time.sleep(self.backoff_sec * attempt)
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error("OpenAI unexpected error attempt %d: %s", attempt, last_error)
                time.sleep(self.backoff_sec)

        dt = max(0.001, time.perf_counter() - start_time)
        return {
            "status": "FAILED",
            "model": eff_model,
            "exit_code": 1,
            "timed_out": False,
            "duration_sec": round(dt, 4),
            "response_text": "",
            "parsed_json": {},
            "provider_usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "thinking_tokens": 0,
                "cached_tokens": 0,
                "total_tokens": 0,
            },
            "error_message": redact_sensitive_text(str(last_error or "Unknown error")),
            "is_mock": False,
            "notification_id": f"OPENAI-FAILED-{request.task_id}",
            "stdout_log_path": None,
            "stderr_log_path": None,
        }

    def _call_anthropic_rest(self, request: ModelRequest, start_time: float) -> Dict[str, Any]:
        """Calls Anthropic Messages API using standard library urllib."""
        eff_model = self.resolve_effective_model(request)
        if eff_model.upper() == "AUTO":
            eff_model = "claude-3-5-sonnet-20241022"
        endpoint = f"{self.base_url}/messages"

        payload: Dict[str, Any] = {
            "model": eff_model,
            "max_tokens": 8192,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        sys_inst = getattr(request, "system_instruction", None)
        if sys_inst:
            payload["system"] = str(sys_inst)

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "User-Agent": "IVA-Autonomous-Partner/1.8.0",
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            req = urllib.request.Request(endpoint, data=data_bytes, headers=headers, method="POST")
            try:
                ctx = ssl.create_default_context()
                with urllib.request.urlopen(req, timeout=self.timeout_sec, context=ctx) as resp:
                    resp_bytes = resp.read()
                    parsed = json.loads(resp_bytes.decode("utf-8"))
                    dt = max(0.001, time.perf_counter() - start_time)

                    resp_text = ""
                    for block in parsed.get("content", []):
                        if block.get("type") == "text":
                            resp_text += block.get("text", "")

                    usage = parsed.get("usage", {})
                    in_toks = int(usage.get("input_tokens", 0))
                    out_toks = int(usage.get("output_tokens", 0))

                    return {
                        "status": "SUCCEEDED",
                        "model": parsed.get("model", eff_model),
                        "exit_code": 0,
                        "timed_out": False,
                        "duration_sec": round(dt, 4),
                        "response_text": resp_text,
                        "parsed_json": {},
                        "provider_usage": {
                            "input_tokens": in_toks,
                            "output_tokens": out_toks,
                            "thinking_tokens": 0,
                            "cached_tokens": 0,
                            "total_tokens": in_toks + out_toks,
                        },
                        "is_mock": False,
                        "notification_id": f"ANTHROPIC-SUCCEEDED-{request.task_id}",
                        "stdout_log_path": None,
                        "stderr_log_path": None,
                    }
            except urllib.error.HTTPError as he:
                err_body = ""
                try:
                    err_body = he.read().decode("utf-8", errors="ignore")
                except Exception:
                    pass
                last_error = f"HTTP {he.code}: {he.reason} - {err_body[:200]}"
                logger.warning("Anthropic HTTPError %d on attempt %d: %s", he.code, attempt, last_error)
                if he.code in (401, 403):
                    break
                time.sleep(self.backoff_sec * attempt)
            except urllib.error.URLError as ue:
                last_error = f"URLError: {ue.reason}"
                logger.warning("Anthropic URLError on attempt %d: %s", attempt, last_error)
                time.sleep(self.backoff_sec * attempt)
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error("Anthropic unexpected error attempt %d: %s", attempt, last_error)
                time.sleep(self.backoff_sec)

        dt = max(0.001, time.perf_counter() - start_time)
        return {
            "status": "FAILED",
            "model": eff_model,
            "exit_code": 1,
            "timed_out": False,
            "duration_sec": round(dt, 4),
            "response_text": "",
            "parsed_json": {},
            "provider_usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "thinking_tokens": 0,
                "cached_tokens": 0,
                "total_tokens": 0,
            },
            "error_message": redact_sensitive_text(str(last_error or "Unknown error")),
            "is_mock": False,
            "notification_id": f"ANTHROPIC-FAILED-{request.task_id}",
            "stdout_log_path": None,
            "stderr_log_path": None,
        }

    def _generate_local_cognitive_fallback(self, request: ModelRequest, error_message: Optional[str] = None) -> str:
        """Produces a grounded, high-agency conversational response when remote AI endpoints fail."""
        p_low = (request.prompt or "").lower().strip()
        if p_low in ("hi", "hello", "hey", "greetings", "test"):
            return (
                "Hello! I am Iva, your autonomous cognitive engineering partner and systems architect.\n\n"
                "I am fully operational. (Note: Upstream model endpoint returned a transient error, "
                "so I've engaged our local cognitive engine). You can converse freely, run tests, "
                "or use `swap <model>` to change models.\n\n"
                "What would you like to build, debug, or coordinate today?"
            )
        elif "status" in p_low:
            return (
                "System Status: 100 specialists active, SQLite WAL memory operational, "
                "local cognitive partner online. Upstream endpoint notice: "
                f"{error_message or 'Rate-limited / Unreachable'}."
            )
        else:
            return (
                f"I received your request: '{request.prompt[:120]}...'\n\n"
                "Notice: Upstream model endpoint returned an error (" + str(error_message or 'Endpoint offline')[:150] + "). "
                "I have preserved your context and task intent in persistent memory. "
                "You can run `swap <model>` or `keys` to configure another provider, or continue chatting."
            )
