@echo off
title AttendAI - Frontend (Django) - Port 8000
color 0E
echo.
echo  ============================================================
echo   AttendAI Frontend (Django)
echo   Running on: http://localhost:8000
echo  ============================================================
echo.

cd /d %~dp0frontend

echo [Setup] Installing requirements...
pip install -r requirements.txt

echo [Setup] Running Django migrations...
python manage.py migrate --run-syncdb

echo [Setup] Setting up HR user...
python setup_hr_user.py

echo.
echo  Starting server...
echo  HR Login: http://localhost:8000/hr-login/
echo  Username: hr_admin   Password: HRSecure@2024
echo.

REM Wait a moment then open browser
timeout /t 4 /nobreak >nul
start "" http://localhost:8000

python manage.py runserver 0.0.0.0:8000
pause
