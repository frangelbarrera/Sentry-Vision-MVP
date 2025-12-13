@echo off
echo ========================================
echo   Sentry Vision Dashboard
echo ========================================
echo.
echo Checking Streamlit...
streamlit --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Streamlit is not installed. Run run_sentry.bat first.
    pause
    exit /b 1
)
echo.
echo Running Dashboard...
echo Access http://localhost:8501 in your browser.
echo.
streamlit run src/dashboard.py
pause