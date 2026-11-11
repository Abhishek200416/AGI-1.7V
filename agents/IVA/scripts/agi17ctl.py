"""Legacy compatibility shim for IVA control CLI.

DEPRECATED: Use ivactl.py instead of agi17ctl.py.
"""

from __future__ import annotations

import sys
from agents.IVA.scripts.ivactl import main

if __name__ == "__main__":
    sys.exit(main())
