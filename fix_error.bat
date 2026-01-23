@echo off
REM Quick Fix Script for Tailwind Error (Windows)

echo 🔧 Fixing Tailwind CSS Error...
echo.

echo Step 1: Installing frontend dependencies...
cd frontend
call npm install

echo.
echo Step 2: Verifying installation...
call npm list tailwindcss postcss autoprefixer

echo.
echo ✅ Dependencies installed!
echo.
echo Now you can run:
echo   npm run dev
echo.
echo The error should be fixed!
pause
