@echo off
echo ============================================
echo UOH Academic System - AI Query Test
echo ============================================
echo.

echo [1/3] Checking Python dependencies...
python -c "import cohere; import pandas; import fastapi" 2>nul
if errorlevel 1 (
    echo ERROR: Missing dependencies. Installing...
    pip install -r requirements.txt
) else (
    echo OK: All dependencies installed
)

echo.
echo [2/3] Testing Cohere Connection...
python -c "from src.core.cohere_ai_agent import CohereAIAgent; agent = CohereAIAgent(); print('OK: Cohere connected')" 2>nul
if errorlevel 1 (
    echo ERROR: Cohere connection failed. Check your COHERE_API_KEY in .env
    pause
    exit /b 1
)

echo.
echo [3/3] Starting Backend Server...
echo.
echo Backend will start on http://localhost:8000
echo Press Ctrl+C to stop
echo.

python main.py
