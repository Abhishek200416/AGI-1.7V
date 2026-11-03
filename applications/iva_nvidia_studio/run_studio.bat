@echo off
title IVA Sovereign Studio (NVIDIA NIM)
cls
echo ======================================================================
echo    IVA SOVEREIGN STUDIO -- POWERED BY NVIDIA NIM
echo ======================================================================
py -3 run_studio.py
if errorlevel 1 (
    python run_studio.py
)
pause
