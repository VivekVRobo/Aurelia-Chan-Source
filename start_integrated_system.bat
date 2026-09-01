@echo off
echo ============================================================
echo Aurelia Cognitive OS V3 - Integrated System Startup
echo ============================================================
echo.

echo [1/3] Installing dependencies...
pip install -r requirements.txt
echo.

echo [2/3] Starting Cognitive OS Backend...
echo Backend will run on http://localhost:5000
echo.
start "Aurelia Backend" python integrated_backend.py
echo.

echo [3/3] Waiting for backend to start...
timeout /t 3 /nobreak >nul
echo.

echo ============================================================
echo System Ready!
echo ============================================================
echo.
echo Frontend: http://localhost:5000/index.html
echo Backend API: http://localhost:5000/api
echo.
echo Press Ctrl+C in the backend window to stop the system
echo ============================================================
pause