@echo off
chcp 65001 >nul
title WeChat Image Download Assistant - One Click Deploy

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║           🖼️  WeChat Image Download Assistant  🖼️            ║
echo ║                                                              ║
echo ║              WeChat Image Download Assistant                 ║
echo ║                                                              ║
echo ║                     One Click Deploy v2.0                   ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo ⏳ Starting application, please wait...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not detected
    echo.
    echo Please install Python 3.8 or higher:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check project files
if not exist "app.py" (
    echo ❌ Error: app.py file not found
    echo Please make sure to run this script in the project root directory
    echo.
    pause
    exit /b 1
)

REM Run Python startup script
echo 🚀 Starting Python application...
python "one_click_deploy.py"

REM If Python script exits, pause to view error information
if errorlevel 1 (
    echo.
    echo ❌ Application startup failed
    echo.
    pause
)

echo.
echo 👋 Application has exited, thank you for using!
pause 