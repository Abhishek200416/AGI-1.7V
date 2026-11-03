"""AGI 1.7 Adapters Package."""

from .model_adapter import DirectiveZeroViolationError, ModelAdapter

def __getattr__(name: str):
    if name == "AGI17Adapter":
        from .agi_17_adapter import AGI17Adapter
        return AGI17Adapter
    elif name in (
        "OmniRouteAdapter",
        "OmniRouteConfig",
        "OmniRouteResponse",
        "OmniRouteTelemetry",
        "TaskType",
        "CircuitState",
    ):
        from . import omniroute_adapter
        return getattr(omniroute_adapter, name)
    elif name == "UniversalAPIProvider":
        from .universal_api_provider import UniversalAPIProvider
        return UniversalAPIProvider
    elif name == "ModelMetadataCatalog":
        from .model_catalog import ModelMetadataCatalog
        return ModelMetadataCatalog
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "DirectiveZeroViolationError",
    "ModelAdapter",
    "AGI17Adapter",
    "OmniRouteAdapter",
    "TaskType",
    "CircuitState",
    "OmniRouteConfig",
    "OmniRouteResponse",
    "OmniRouteTelemetry",
    "UniversalAPIProvider",
    "ModelMetadataCatalog",
]

