@echo off
echo ============================================
echo GitHub Repository Cleanup Strategy
echo ============================================
echo.
echo IMPORTANT: Your GitHub has 70+ documentation files
echo Your local repository is now clean
echo.
echo OPTIONS:
echo ============================================
echo.
echo OPTION 1: FORCE PUSH (Recommended - Clean Slate)
echo   - Deletes ALL those 70+ docs from GitHub
echo   - Replaces with your clean local version
echo   - GitHub will match your local exactly
echo   - CAUTION: This overwrites GitHub history
echo.
echo OPTION 2: MANUAL DELETION
echo   - Delete files one by one on GitHub
echo   - Very time consuming (70+ files!)
echo   - Not recommended
echo.
echo OPTION 3: KEEP BOTH
echo   - Pull GitHub files first
echo   - Then delete locally
echo   - Then commit and push
echo   - Takes longer but safer
echo.
echo ============================================
echo.
echo Which option do you want?
echo.
echo Press 1 for OPTION 1 (Force push - clean slate)
echo Press 2 for OPTION 3 (Safe merge)
echo Press 3 to cancel and decide later
echo.
choice /C 123 /N /M "Enter your choice (1, 2, or 3): "

if errorlevel 3 goto cancel
if errorlevel 2 goto safe_merge
if errorlevel 1 goto force_push

:force_push
echo.
echo ============================================
echo FORCE PUSH - Clean Slate
echo ============================================
echo.
echo This will:
echo 1. Backup your current GitHub (just in case)
echo 2. Force push your clean local version
echo 3. GitHub will have ONLY essential files
echo.
echo Are you ABSOLUTELY SURE?
echo.
choice /C YN /M "Proceed with force push? (Y/N)"
if errorlevel 2 goto cancel

echo.
echo Creating backup branch on GitHub...
git push origin main:backup-before-cleanup

echo.
echo Force pushing clean version...
git push origin main --force

echo.
echo ============================================
echo DONE! Your GitHub is now clean!
echo ============================================
echo.
echo What was done:
echo - Created backup branch: backup-before-cleanup
echo - Force pushed your clean local version
echo - GitHub now matches your local (clean!)
echo.
echo You can see the backup at:
echo https://github.com/Khalid2703/GiveMeMarks/tree/backup-before-cleanup
echo.
goto end

:safe_merge
echo.
echo ============================================
echo SAFE MERGE - Pulling and Cleaning
echo ============================================
echo.
echo This will:
echo 1. Pull all GitHub files
echo 2. Delete unnecessary docs locally
echo 3. Commit the deletions
echo 4. Push back to GitHub
echo.
pause

echo.
echo [1/4] Pulling from GitHub...
git pull origin main

echo.
echo [2/4] Running cleanup script...
call clean_repository.bat

echo.
echo [3/4] Staging deletions...
git add -A

echo.
echo [4/4] Committing...
git commit -m "Clean repository - remove 70+ documentation files"

echo.
echo Ready to push. Review changes above.
echo.
choice /C YN /M "Push to GitHub now? (Y/N)"
if errorlevel 2 goto cancel

git push origin main

echo.
echo ============================================
echo DONE! Repository cleaned!
echo ============================================
goto end

:cancel
echo.
echo Operation cancelled. No changes made.
goto end

:end
echo.
pause
