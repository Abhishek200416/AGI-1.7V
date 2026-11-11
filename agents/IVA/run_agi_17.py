"""Legacy compatibility shim for IVA runtime entrypoint.

DEPRECATED: Use run_iva.py instead of run_agi_17.py.
"""

from __future__ import annotations

import sys
from agents.IVA.run_iva import (
    TERMINAL_OUTCOME_EXIT_CODES,
    compute_cli_exit_code,
    main,
    _resolve_storage_root,
    _spawn_detached,
    _update_detached_pid_file,
)

__all__ = [
    "TERMINAL_OUTCOME_EXIT_CODES",
    "compute_cli_exit_code",
    "main",
    "_resolve_storage_root",
    "_spawn_detached",
    "_update_detached_pid_file",
]

if __name__ == "__main__":
    sys.exit(main() or 0)
