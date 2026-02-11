@echo off
echo ============================================================
echo       AI4SIDS Climate Resilience System
echo       Starting Local Development Server
echo ============================================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call ..\ai4sids_env\Scripts\activate.bat

echo.
echo Starting API Server...
echo Server will be available at: http://localhost:8000
echo.
echo Press CTRL+C to stop the server
echo.

python api_server.py

pause
