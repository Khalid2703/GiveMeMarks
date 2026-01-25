@echo off
echo ============================================
echo REPOSITORY CLEANUP - Remove Unwanted Data
echo ============================================
echo.

cd /d "%~dp0"

echo [1/5] Cleaning up documentation mess...
del /Q "AI_QUERY_QUICK_GUIDE.txt" 2>nul
del /Q "AI_QUERY_VISUAL_DIAGRAM.txt" 2>nul
del /Q "ARCHITECTURE_DIAGRAM.txt" 2>nul
del /Q "BUILD_MANIFEST.md" 2>nul
del /Q "BUILD_STATUS.py" 2>nul
del /Q "COMMANDS_REFERENCE.txt" 2>nul
del /Q "COMPLETE_DOCUMENTATION_INDEX.md" 2>nul
del /Q "convert_samples_guide.py" 2>nul
del /Q "DEMO_PRESENTATION_SCRIPT.txt" 2>nul
del /Q "DEPLOYMENT_ARCHITECTURE.md" 2>nul
del /Q "DEPLOYMENT_GUIDE.md" 2>nul
del /Q "DEPLOY.md" 2>nul
del /Q "DOCUMENTATION_INDEX.md" 2>nul
del /Q "ENHANCED_IMPLEMENTATION_GUIDE.md" 2>nul
del /Q "FINAL_MASTER_SUMMARY.txt" 2>nul
del /Q "FIX_DEPLOYMENT_ERRORS.md" 2>nul
del /Q "LOCALHOST_CONFIGURATION.md" 2>nul
del /Q "LOCALHOST_QUICK_REFERENCE.txt" 2>nul
del /Q "LOCALHOST_UPDATE_SUMMARY.txt" 2>nul
del /Q "PROJECT_INDEX.md" 2>nul
del /Q "PROJECT_SUMMARY.md" 2>nul
del /Q "QUICK_REFERENCE.md" 2>nul
del /Q "QUICK_REFERENCE_CARD.md" 2>nul
del /Q "QUICK_START.md" 2>nul
del /Q "RESULTS_TAB_FIX.md" 2>nul
del /Q "RESULTS_TAB_QUICK_FIX.md" 2>nul
del /Q "RESULTS_TAB_VISUAL_SUMMARY.txt" 2>nul
del /Q "START_HERE.txt" 2>nul
del /Q "START_HERE_RESULTS_FIX.txt" 2>nul
del /Q "SUMMARY.md" 2>nul
del /Q "SYSTEM_DIAGRAMS.txt" 2>nul
del /Q "TOMORROW_PRESENTATION_GUIDE.md" 2>nul
del /Q "VECTOR_DB_INTEGRATION_GUIDE.md" 2>nul
del /Q "verify_localhost.py" 2>nul
del /Q "verify_results_tab.py" 2>nul
del /Q "cleanup_docs.bat" 2>nul
del /Q "files_to_delete.txt" 2>nul
del /Q "show_remaining_files.bat" 2>nul

echo [2/5] Cleaning up old batch scripts...
del /Q "fix_error.bat" 2>nul
del /Q "fix_error.sh" 2>nul
del /Q "restart_backend.bat" 2>nul
del /Q "restart_backend_fix_cors.bat" 2>nul
del /Q "start_backend_with_ai.bat" 2>nul
del /Q "sync_with_github.bat" 2>nul
del /Q "PUSH_FRONTEND_TO_GIT.bat" 2>nul
del /Q "cleanup_vercel_config.bat" 2>nul

echo [3/5] Cleaning up sample documents (keeping directory)...
if exist "sample_documents" (
    del /Q "sample_documents\*.*" 2>nul
    echo    Cleared sample_documents folder
)

echo [4/5] Cleaning up temporary data files...
if exist "data\documents" (
    del /Q "data\documents\*.pdf" 2>nul
    echo    Cleared uploaded PDFs
)

echo [5/5] Cleaning up old Excel batches (keeping structure)...
if exist "data\excel" (
    del /Q "data\excel\*.xlsx" 2>nul
    del /Q "data\excel\batch_metadata.json" 2>nul
    echo    Cleared Excel batches
)

echo.
echo ============================================
echo Cleanup Complete!
echo ============================================
echo.
echo Removed:
echo   ✓ 35+ documentation files
echo   ✓ 8 old batch scripts
echo   ✓ Sample documents
echo   ✓ Uploaded PDFs
echo   ✓ Old Excel batches
echo.
echo Kept:
echo   ✓ Source code (backend, frontend, src)
echo   ✓ Configuration files
echo   ✓ README_CLEAN.md
echo   ✓ DEPLOY_SIMPLE.md
echo   ✓ requirements.txt
echo   ✓ .env (your API keys)
echo   ✓ Directory structure
echo.
echo Next: Run 'git_cleanup.bat' to update .gitignore
echo.
pause
