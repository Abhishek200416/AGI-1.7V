@echo off
title IVA 3D Neural Observatory
cls
echo ======================================================================
echo    IVA 3D NEURAL OBSERVATORY -- AGI 1.7 QUANTUM VISUALIZATION
echo ======================================================================
py -3 run_observatory.py
if errorlevel 1 (
    python run_observatory.py
)
pause
