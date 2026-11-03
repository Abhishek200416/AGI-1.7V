@echo off
setlocal
where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    py -3 "%~dp0setup_iva.py" %*
    exit /b %ERRORLEVEL%
)
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python "%~dp0setup_iva.py" %*
    exit /b %ERRORLEVEL%
)
where python3 >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python3 "%~dp0setup_iva.py" %*
    exit /b %ERRORLEVEL%
)
echo [ERROR] Python 3.10+ was not found on your system.
echo Please install official Python from https://www.python.org/downloads/
pause
exit /b 1
