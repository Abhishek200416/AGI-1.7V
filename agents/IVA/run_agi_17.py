"""Legacy compatibility shim for IVA runtime entrypoint.

DEPRECATED: Use run_iva.py instead of run_agi_17.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Forward directly to run_iva.py
from agents.IVA.run_iva import main

if __name__ == "__main__":
    sys.exit(main() or 0)
