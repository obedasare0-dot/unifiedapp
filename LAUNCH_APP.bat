@echo off
REM PSA Unified Processor - Launcher
REM Launches FastAPI web app with uvicorn

echo.
echo ========================================
echo PSA Unified Processor
echo Product + Planogram + Fixture Extract
echo ========================================
echo.
echo Starting server...
echo Open your browser to: http://localhost:8000
echo Press CTRL+C to stop the server
echo.

cd /d "%~dp0"

REM Launch FastAPI app with uvicorn (without --reload to avoid watching backup folders)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

REM If it exits, keep window open
echo.
echo.
echo ========================================
echo Server has stopped!
echo ========================================
echo.
echo Press any key to close this window...
pause >nul
