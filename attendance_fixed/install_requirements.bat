@echo off
title Smart Attendance System — Install Dependencies
color 0B
echo.
echo  ============================================================
echo   AttendAI — Installing Dependencies
echo  ============================================================
echo.

echo [1/2] Installing Backend dependencies (FastAPI + DeepFace)...
echo       This may take several minutes on first install.
echo.
cd /d "%~dp0backend"
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo  ERROR: Backend installation failed. Check Python/pip setup.
    pause
    exit /b 1
)

echo.
echo [2/2] Installing Frontend dependencies (Django)...
cd /d "%~dp0frontend"
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo  ERROR: Frontend installation failed.
    pause
    exit /b 1
)

echo.
echo  ============================================================
echo   All dependencies installed successfully!
echo   
echo   NOTE: DeepFace will download the Facenet AI model on first
echo   recognition attempt (~90 MB). This is automatic.
echo  ============================================================
echo.
pause
