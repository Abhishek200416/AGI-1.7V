#!/usr/bin/env bash
# ==============================================================================
#   🌟 IVA — Autonomous Cognitive Partner & Engineering Runtime Installer
#   One-Click Shell Installer for Linux, macOS, Android Termux & WSL
# ==============================================================================
#   Single-Step Command:
#     curl -fsSL https://raw.githubusercontent.com/Abhishek200416/IVA/main/install.sh | bash
# ==============================================================================

set -e

echo ""
echo -e "\033[1;36m================================================================================\033[0m"
echo -e "\033[1;35m   *  IVA — AUTONOMOUS COGNITIVE PARTNER & ENGINEERING RUNTIME INSTALLER\033[0m"
echo -e "\033[1;36m================================================================================\033[0m"
echo -e "\033[0;37m   \"Cool-headed, sharp, mature, warm, ambitious, practical, and fiercely loyal.\"\033[0m"
echo -e "\033[1;36m================================================================================\033[0m"
echo ""

# 1. Check for Git
if ! command -v git &> /dev/null; then
    echo -e "\033[1;31m❌ Error: Git is not installed.\033[0m"
    echo -e "\033[1;33m   Please install Git (e.g. apt install git / pkg install git / brew install git).\033[0m"
    exit 1
fi

# 2. Resolve Python Runtime (3.10+)
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "\033[1;31m❌ Error: Python 3.10+ is not installed.\033[0m"
    echo -e "\033[1;33m   Please install python3 (e.g. apt install python3 / pkg install python / brew install python3).\033[0m"
    exit 1
fi

echo -e "\033[1;32m✅ Detected Python Runtime: $($PYTHON_CMD --version)\033[0m"

# 3. Check Workspace Directory
if [ ! -f "setup_iva.py" ] || [ ! -f "run_iva.py" ]; then
    TARGET_DIR="IVA"
    if [ ! -d "$TARGET_DIR" ]; then
        echo -e "\033[1;36m📦 Cloning IVA repository from GitHub...\033[0m"
        git clone https://github.com/Abhishek200416/IVA.git "$TARGET_DIR"
    else
        echo -e "\033[1;36m📦 Existing IVA directory found. Fetching latest updates...\033[0m"
        cd "$TARGET_DIR"
        git pull origin main || true
        cd ..
    fi
    cd "$TARGET_DIR"
fi

# 4. Launch Orchestrated Step-by-Step Interactive Setup
echo -e "\033[1;36m🚀 Launching IVA Orchestrated Setup...\033[0m"
echo ""

# Attach to /dev/tty if available so input works even when piped from curl | bash
if [ -t 0 ]; then
    $PYTHON_CMD setup_iva.py
elif [ -e /dev/tty ]; then
    $PYTHON_CMD setup_iva.py < /dev/tty
else
    $PYTHON_CMD setup_iva.py
fi
