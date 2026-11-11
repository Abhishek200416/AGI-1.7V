#!/usr/bin/env bash
# ==============================================================================
#   🌟 IVA — Autonomous Cognitive Engineering Partner & Developer Runtime
#   Native Cross-Platform Launcher for macOS (MacBook Air/Pro), Linux & BSD
# ==============================================================================
# Usage:
#   ./run_iva.sh                 # Interactive Terminal CLI
#   ./run_iva.sh "Your prompt"   # Single-shot prompt
#   ./run_iva.sh --profile-only  # Capability profiler & self-diagnostic
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Enforce UTF-8 Locale for clean emoji & terminal typography
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
export LANG="${LANG:-en_US.UTF-8}"

# 2. Detect Operating System & CPU Architecture
OS_NAME="$(uname -s)"
ARCH_NAME="$(uname -m)"

# 3. Locate Python 3.10+ Runtime
PYTHON_BIN=""

# Check local virtual environment first (.venv or venv)
if [ -x "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
elif [ -x "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON_BIN="$SCRIPT_DIR/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
fi

if [ -z "$PYTHON_BIN" ]; then
    echo -e "\033[1;31m❌ Error: Python 3.10+ was not found on your system.\033[0m"
    if [ "$OS_NAME" = "Darwin" ]; then
        echo -e "\033[1;33m   MacBook Setup: Install Python via Homebrew:\033[0m"
        echo -e "     brew install python@3.12"
        echo -e "   Or use Astral uv:"
        echo -e "     curl -LsSf https://astral.sh/uv/install.sh | sh"
    else
        echo -e "\033[1;33m   Please install Python 3.10+ using your package manager (apt/dnf/pacman/apk).\033[0m"
    fi
    exit 1
fi

# 4. Verify Python Version >= 3.10
PY_VER="$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "0.0")"
PY_MAJOR="$(echo "$PY_VER" | cut -d. -f1)"
PY_MINOR="$(echo "$PY_VER" | cut -d. -f2)"

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo -e "\033[1;31m❌ Error: Python 3.10 or higher is required (found Python $PY_VER).\033[0m"
    if [ "$OS_NAME" = "Darwin" ]; then
        echo -e "\033[1;33m   On MacBook: brew install python@3.12\033[0m"
    fi
    exit 1
fi

# 5. Launch IVA Runtime Entrypoint
exec "$PYTHON_BIN" "$SCRIPT_DIR/run_iva.py" "$@"
