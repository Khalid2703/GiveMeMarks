@echo off
echo ============================================
echo Git Cleanup and Preparation
echo ============================================
echo.

cd /d "%~dp0"

echo [1/4] Updating .gitignore...
copy /Y ".gitignore_clean" ".gitignore"
del ".gitignore_clean"
echo    ✓ Updated .gitignore

echo.
echo [2/4] Removing cached files from git...
git rm -r --cached data/documents/*.pdf 2>nul
git rm -r --cached data/excel/*.xlsx 2>nul
git rm -r --cached data/logs/*.log 2>nul
git rm -r --cached sample_documents/* 2>nul
echo    ✓ Removed cached data files

echo.
echo [3/4] Current git status:
git status --short

echo.
echo [4/4] Ready to commit!
echo.
echo ============================================
echo Next Steps:
echo ============================================
echo.
echo 1. Review the changes above
echo 2. Commit the cleanup:
echo    git add .
echo    git commit -m "Clean up repository - remove docs and data"
echo    git push
echo.
echo 3. Then deploy using DEPLOY_SIMPLE.md guide
echo.
pause
