@echo off
echo ========================================
echo   Sentry Vision MVP - Execution Script
echo ========================================
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed. Install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)
echo Python detected.
echo.
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: Could not upgrade pip.
    pause
    exit /b 1
)
echo.
echo Installing dependencies...
python -m pip install PyYAML opencv-python-headless ultralytics streamlit psutil onnxruntime
if errorlevel 1 (
    echo ERROR: Dependency installation failed.
    echo Check your internet connection and permissions.
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.
echo ========================================
echo   Usage Instructions:
echo ========================================
echo - The system will detect people, cell phones, and laptops.
echo - Press 'q' in the video window to exit.
echo - Check logs/sentry.log for details.
echo - For testing, point the camera at objects/people.
echo.
echo Running Sentry Vision MVP...
echo.
python src/vision_mvp.py
echo.
echo Execution finished. Check baseline_report.txt for metrics.
pause