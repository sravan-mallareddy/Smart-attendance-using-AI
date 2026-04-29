@echo off
title AttendAI - Start All
color 0A
echo.
echo  ============================================================
echo   AttendAI Smart Attendance System
echo   Backend  -  http://localhost:8001
echo   Frontend -  http://localhost:8000
echo   HR Login -  http://localhost:8000/hr-login/
echo  ============================================================
echo.

REM Start backend in a separate window
start "AttendAI Backend (FastAPI)" cmd /k "cd /d %~dp0backend && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

REM Wait for backend to initialize
timeout /t 5 /nobreak >nul

REM Setup and start frontend in a separate window
start "AttendAI Frontend (Django)" cmd /k "cd /d %~dp0frontend && pip install -r requirements.txt && python manage.py migrate --run-syncdb && python setup_hr_user.py && python manage.py runserver 0.0.0.0:8000"

REM Wait for frontend to initialize
timeout /t 8 /nobreak >nul

REM Open browser
echo  Opening browser...
start "" http://localhost:8000

echo.
echo  Both servers are running!
echo  Backend  -  http://localhost:8001
echo  Frontend -  http://localhost:8000
echo  HR Login -  http://localhost:8000/hr-login/
echo.
echo  HR Credentials - Username: hr_admin  /  Password: HRSecure@2024
echo.
echo  Close the backend and frontend windows to stop the servers.
pause
