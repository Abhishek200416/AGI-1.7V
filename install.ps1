<#
================================================================================
  🌟 IVA — Autonomous Cognitive Partner & Engineering Runtime Installer
  One-Click PowerShell Installer for Windows
================================================================================
  Single-Step Command:
    irm https://raw.githubusercontent.com/Abhishek200416/IVA/main/install.ps1 | iex
================================================================================
#>

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "   *  IVA — AUTONOMOUS COGNITIVE PARTNER & ENGINEERING RUNTIME INSTALLER" -ForegroundColor Magenta
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "   `"Cool-headed, sharp, mature, warm, ambitious, practical, and fiercely loyal.`"" -ForegroundColor DarkGray
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check for Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Git is not detected in your PATH." -ForegroundColor Red
    Write-Host "   Please install Git for Windows: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# 2. Resolve Python Runtime (3.10+)
$pyExe = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pyExe = "py -3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pyExe = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pyExe = "python3"
} else {
    Write-Host "❌ Error: Python is not detected in your PATH." -ForegroundColor Red
    Write-Host "   Please install Python 3.10+: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Detected Python Runtime ($pyExe)" -ForegroundColor Green

# 3. Check Workspace Directory
$inRepo = $false
if ((Test-Path "setup_iva.py") -and (Test-Path "run_iva.py")) {
    $inRepo = $true
}

if ($inRepo) {
    Write-Host "📦 Inside existing IVA repository. Pulling latest updates from GitHub..." -ForegroundColor Cyan
    try { git pull origin main } catch { Write-Host "⚠️ Notice: git pull completed with warnings." -ForegroundColor Yellow }
} else {
    $targetDir = "IVA"
    if (-not (Test-Path $targetDir)) {
        Write-Host "📦 Cloning IVA repository from GitHub..." -ForegroundColor Cyan
        git clone https://github.com/Abhishek200416/IVA.git $targetDir
    } else {
        Write-Host "📦 Existing IVA directory found. Fetching latest updates from GitHub..." -ForegroundColor Cyan
        Push-Location $targetDir
        try { git pull origin main } catch { Write-Host "⚠️ Notice: git pull completed with warnings." -ForegroundColor Yellow }
        Pop-Location
    }
    Set-Location $targetDir
}

# 4. Launch Orchestrated Step-by-Step Interactive Setup
Write-Host "🚀 Launching IVA Orchestrated Setup..." -ForegroundColor Cyan
Write-Host ""

if ($pyExe -eq "py -3") {
    & py -3 setup_iva.py
} else {
    & $pyExe setup_iva.py
}
