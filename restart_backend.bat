@echo off
echo ========================================
echo   RESTARTING UOH HACKATHON BACKEND
echo ========================================
echo.
echo Stopping any existing backend processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *uvicorn*" 2>nul

echo.
echo Starting backend server...
cd /d C:\Users\hp\UOH_Hackathon
start "UOH Backend" cmd /k "uvicorn api:app --reload --host 0.0.0.0 --port 8000"

echo.
echo ========================================
echo   Backend server started!
echo   URL: http://localhost:8000
echo ========================================
echo.
echo Press any key to test the fix...
pause >nul

echo.
echo Testing LLM parsing fix...
python test_llm_fix.py

echo.
pause
