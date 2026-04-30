# Setup Guide — AttendAI Smart Attendance System

## Project Overview

AttendAI is an AI-powered face recognition attendance system built using:

- Frontend: Django 5
- Backend: FastAPI
- Database: SQLite
- Face Recognition: DeepFace + FaceNet
- Face Detection: MTCNN

This guide explains how to install, configure, and run the project.

---

## Folder Structure

```text
attendance_fixed/
├── backend/
├── frontend/
├── start_all.bat
├── start_backend.bat
├── start_frontend.bat
├── install_requirements.bat
├── README.md
└── FIXES.md
```

---

## System Requirements

### Required Software

- Python 3.10 or Python 3.11 (Recommended)
- pip (Python package manager)
- Windows OS
- Webcam (for attendance capture)
- Internet connection (first run downloads AI model)

### Recommended Hardware

- Minimum 8 GB RAM
- Minimum 2 GB free disk space

---

## Installation Steps

## Step 1: Extract the Project

Extract the ZIP file to any folder such as:

```text
D:\Projects\attendance_fixed
```

---

## Step 2: Open in VS Code

Open the extracted folder in Visual Studio Code.

---

## Step 3: Install Dependencies

Run:

```bat
install_requirements.bat
```

This installs both frontend and backend packages.

### Manual Alternative

### Backend

```bash
cd backend
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
pip install -r requirements.txt
```

---

## Step 4: Run Database Migration

Open terminal inside frontend folder:

```bash
cd frontend
python manage.py migrate --run-syncdb
```

This creates Django authentication database.

---

## Step 5: Create HR Admin User

Run:

```bash
python setup_hr_user.py
```

Default HR login:

- Username: hr_admin
- Password: HRSecure@2024

---

## Step 6: Start Backend Server

Run:

```bat
start_backend.bat
```

OR manually:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

Backend URL:

```text
http://localhost:8001
```

API Docs:

```text
http://localhost:8001/docs
```

---

## Step 7: Start Frontend Server

Run:

```bat
start_frontend.bat
```

OR manually:

```bash
cd frontend
python manage.py runserver 0.0.0.0:8000
```

Frontend URL:

```text
http://localhost:8000
```

---

## Step 8: Start Everything Together

Instead of separate terminals:

```bat
start_all.bat
```

This launches both frontend and backend automatically.

---

## Troubleshooting

## Issue: start.bat closes immediately

### Solution

Run manually using terminal to see actual error:

```bash
python manage.py runserver
```

---

## Issue: No face detected

### Solution

- Use proper lighting
- Face should be front-facing
- Remove mask/sunglasses
- Keep webcam stable

---

## Issue: Login page not opening

### Solution

Run:

```bash
python manage.py migrate
python setup_hr_user.py
```

---

## Issue: Reports page asks for login

### Solution

This is expected.

Only HR users can access reports.

Use:

- Username: hr_admin
- Password: HRSecure@2024

---

## Important Notes

- Reports page is protected using Django authentication
- Attendance records are stored in backend SQLite database
- HR login data is stored separately in frontend SQLite database

---

## Completion

After successful setup, open:

```text
http://localhost:8000
```

and begin using the system.
