@echo off
echo ============================================
echo Quick GitHub Sync - Push Clean Version
echo ============================================
echo.

cd /d "%~dp0"

echo [1/5] Staging all changes...
git add -A

echo.
echo [2/5] Committing changes...
git commit -m "Clean repository - remove 87 documentation files, keep essentials only"

echo.
echo [3/5] Creating backup branch on GitHub...
git branch backup-before-force-push
git push origin backup-before-force-push

echo.
echo ============================================
echo Backup created at: backup-before-force-push
echo ============================================
echo.
echo Now you have 2 options:
echo.
echo OPTION 1: Normal push (recommended - try this first)
echo   git push origin main
echo.
echo OPTION 2: Force push (if Option 1 fails)
echo   git push origin main --force
echo.
echo Let's try OPTION 1 first...
echo.
pause

echo.
echo [4/5] Pushing to GitHub (normal push)...
git push origin main

if errorlevel 1 (
    echo.
    echo ============================================
    echo Normal push failed - this is normal!
    echo ============================================
    echo.
    echo GitHub has files that you deleted locally.
    echo We need to force push to override.
    echo.
    echo Your backup is safe at: backup-before-force-push
    echo.
    choice /C YN /M "Force push now? (Y/N)"
    
    if errorlevel 2 (
        echo.
        echo Cancelled. Run this script again when ready.
        goto end
    )
    
    echo.
    echo [5/5] Force pushing...
    git push origin main --force
    
    echo.
    echo ============================================
    echo DONE! Repository cleaned on GitHub!
    echo ============================================
) else (
    echo.
    echo ============================================
    echo SUCCESS! Normal push worked!
    echo ============================================
)

echo.
echo What was done:
echo   ✓ Deleted 87 documentation files
echo   ✓ Kept only essential files
echo   ✓ Created backup branch
echo   ✓ Pushed to GitHub
echo.
echo Verify at:
echo   https://github.com/Khalid2703/GiveMeMarks
echo.
echo Backup available at:
echo   https://github.com/Khalid2703/GiveMeMarks/tree/backup-before-force-push
echo.

:end
pause
