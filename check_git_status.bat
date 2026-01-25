@echo off
echo ============================================
echo Checking Git Status
echo ============================================
echo.

cd /d "%~dp0"

echo Your current git status:
echo.
git status

echo.
echo ============================================
echo Remote repository info:
echo ============================================
echo.
git remote -v

echo.
echo ============================================
echo Latest commits:
echo ============================================
echo.
git log --oneline -5

echo.
pause
