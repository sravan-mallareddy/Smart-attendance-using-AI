@echo off
title AttendAI - Backend (FastAPI) - Port 8001
color 0B
echo.
echo  ============================================================
echo   AttendAI Backend (FastAPI)
echo   Running on: http://localhost:8001
echo   API Docs:   http://localhost:8001/docs
echo  ============================================================
echo.

cd /d %~dp0backend

echo [Setup] Installing / verifying requirements...
pip install -r requirements.txt

echo.
echo  Starting backend server...
echo  API docs will open automatically once ready.
echo.

REM Start uvicorn in background, wait for it to be ready, then open browser
start /B uvicorn main:app --host 0.0.0.0 --port 8001 --reload
timeout /t 6 /nobreak >nul
start "" http://localhost:8001/docs

REM Keep window open so logs are visible
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
pause
