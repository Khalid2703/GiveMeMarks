@echo off
echo ========================================
echo Restarting UOH Backend Server
echo ========================================
echo.

cd /d C:\Users\hp\UOH_Hackathon

echo Killing any existing backend processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *api.py*" 2>nul

echo.
echo Starting backend server...
echo.

start "UOH Backend" python backend/api.py

echo.
echo ========================================
echo Backend server restarted!
echo ========================================
echo.
echo Next steps:
echo 1. Wait 5 seconds for server to start
echo 2. Go to browser (http://localhost:5173)
echo 3. Press Ctrl+Shift+R to hard refresh
echo 4. CORS error should be gone!
echo.
pause
