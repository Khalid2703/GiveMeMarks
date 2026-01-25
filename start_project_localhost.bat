@echo off
echo ============================================
echo Starting UOH Hackathon Project (Localhost)
echo ============================================
echo.

echo [1/2] Starting Backend Server...
echo.
cd /d "%~dp0backend"
start "Backend Server" cmd /k "python api.py"
timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend Server...
echo.
cd /d "%~dp0frontend"
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ============================================
echo Both servers are starting!
echo ============================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Check the opened terminal windows for status
echo.
echo Press any key to open browser...
pause >nul

start http://localhost:5173

echo.
echo ============================================
echo Project is running!
echo ============================================
echo.
echo To stop servers: Close the terminal windows
echo.
pause
