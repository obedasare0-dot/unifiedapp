@echo off
REM PSA Unified Processor - Launcher WITH Auto-Reload
REM Use this if you're actively developing and want auto-reload on code changes
REM This excludes backup folders from being watched

echo.
echo ========================================
echo PSA Unified Processor (DEV MODE)
echo Auto-reload enabled
echo ========================================
echo.
echo Starting server...
echo Open your browser to: http://localhost:8000
echo Press CTRL+C to stop the server
echo.

cd /d "%~dp0"

REM Launch FastAPI app with uvicorn with reload, excluding backup folders
python -m uvicorn app.main:app --reload --reload-exclude "PRODUCT_BACKUP/**" --reload-exclude "PLANOGRAM_BACKUP/**" --host 0.0.0.0 --port 8000

REM If it exits, keep window open
echo.
echo Server has stopped.
echo Window will close in 5 seconds...
timeout /t 5 /nobreak
