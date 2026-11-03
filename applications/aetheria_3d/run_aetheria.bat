@echo off
title AETHERIA 3D • Living Neural Cosmos
echo ======================================================================
echo    Starting AETHERIA 3D (Living Neural Cosmos)
echo    Powered by NVIDIA Nemotron & Python Standard Library
echo ======================================================================
cd /d "%~dp0"
py -3 run_aetheria.py %*
if %ERRORLEVEL% NEQ 0 (
    python run_aetheria.py %*
)
pause
