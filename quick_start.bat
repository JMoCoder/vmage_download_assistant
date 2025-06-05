@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: Set window title and color
title WeChat Image Download Assistant - Quick Start
color 0A

echo.
echo     ╔══════════════════════════════════════════════════════════════╗
echo     ║                                                              ║
echo     ║           🖼️  WeChat Image Download Assistant  🖼️            ║
echo     ║                                                              ║
echo     ║                    Quick Start Script v1.0                   ║
echo     ║                                                              ║
echo     ╚══════════════════════════════════════════════════════════════╝
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not detected, please install Python 3.7+
    echo 📥 Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if dependencies are installed
echo 🔍 Checking application dependencies...
python -c "import flask, flask_cors, requests, bs4" >nul 2>&1
set DEPS_CHECK=%errorlevel%

if %DEPS_CHECK% equ 0 (
    echo ✅ Dependencies installed, quick start mode
    goto :QUICK_START
) else (
    echo ⚠️  Missing dependencies detected, running full installation
    goto :FULL_INSTALL
)

:FULL_INSTALL
echo.
echo 🔧 Running full installation process...
echo ======================================================================
if exist "one_click_deploy.py" (
    python "one_click_deploy.py"
) else (
    echo ❌ one_click_deploy.py file not found
    echo 💡 Please ensure files are complete or re-download the project
    pause
    exit /b 1
)
goto :END

:QUICK_START
echo.
echo 🚀 Quick start mode - skipping dependency check
echo ======================================================================

:: Create necessary directories
if not exist "downloads" mkdir downloads
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs

:: Check core files
if not exist "app.py" (
    echo ❌ app.py file not found
    pause
    exit /b 1
)

echo ✅ Environment check completed
echo.
echo 🌐 Starting web server...
echo ======================================================================
echo 🌐 Access URLs:
echo    Local access: http://127.0.0.1:5000
echo    LAN access: http://0.0.0.0:5000
echo.
echo 💡 Usage Instructions:
echo    1. Open the above URL in your browser
echo    2. Enter WeChat article link
echo    3. Click 'Start Analysis' button
echo    4. Select images to download
echo    5. Click 'Download Selected Images'
echo.
echo ⏹️  Stop application: Press Ctrl+C
echo ======================================================================
echo.

:: Automatically open browser
start http://127.0.0.1:5000

:: Start Flask application
python -c "from app import app; app.run(host='0.0.0.0', port=5000, debug=False)"

:END
echo.
echo 👋 Thank you for using WeChat Image Download Assistant!
pause 