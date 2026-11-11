"""Legacy compatibility forwarder for IVAAdapter.

DEPRECATED: Import from iva_adapter instead of agi_17_adapter.
"""

from .iva_adapter import IVAAdapter, AGI17Adapter

__all__ = ["IVAAdapter", "AGI17Adapter"]
