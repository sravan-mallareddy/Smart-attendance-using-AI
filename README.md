# AttendAI — Smart Employee Attendance System

> AI-powered, face-recognition-based attendance tracking. Fully local — no cloud, no subscription, no biometric data ever leaves your machine.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Quick Start — Windows](#quick-start--windows)
- [Quick Start — Linux / macOS](#quick-start--linux--macos)
- [Running on a Network / Mobile Devices](#running-on-a-network--mobile-devices)
- [First-Time Setup Details](#first-time-setup-details)
- [Pages & URLs](#pages--urls)
- [HR Login](#hr-login)
- [How to Register an Employee](#how-to-register-an-employee)
- [How Attendance Marking Works](#how-attendance-marking-works)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Security & Anti-Spoofing](#security--anti-spoofing)
- [Git Setup](#git-setup)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## Features
| Feature | Details |
|---|---|
| Face Recognition | DeepFace + Facenet (128-d embeddings), MTCNN + OpenCV detection |
| Anti-Spoofing | Blocks phone-screen photos, printed photos, screen recordings |
| Duplicate Guard | Rejects same face registered under a different Employee ID |
| Multi-Sample Enrolment | Capture up to 5 webcam angles for better accuracy |
| Live Dashboard | Real-time stats, today's log, weekly summary |
| Reports | Filter by date/employee, sortable table, CSV export |
| HR Portal | Protected reports section with separate HR login |
| Mobile Friendly | Works with mobile browsers as the camera source |
| 100% On-Device | SQLite database, no internet required after install |

---

## Tech Stack
| Layer | Technology | Version |
|---|---|---|
| Backend API | FastAPI + Uvicorn | 0.110 / 0.29 |
| Face Recognition | DeepFace (Facenet model) | 0.0.91 |
| Face Detection | MTCNN + OpenCV cascade | 0.1.1 / 4.9 |
| Database | SQLite via SQLAlchemy | 2.0 |
| Frontend | Django (template-rendered) | 5.0 |
| UI | Vanilla JS + CSS custom properties | — |

---

## Project Structure

```
attendance_fixed/
│
├── backend/                          # FastAPI backend (Python)
│   ├── main.py                       # App entry, CORS, router registration, static files
│   ├── models.py                     # SQLAlchemy ORM: Employee, Attendance
│   ├── schemas.py                    # Pydantic request/response schemas
│   ├── database.py                   # SQLite engine + session factory
│   ├── requirements.txt              # Backend Python dependencies
│   ├── attendance.db                 # SQLite DB (auto-created on first run, git-ignored)
│   ├── face_db/                      # Saved face images (auto-created, git-ignored)
│   │   └── .gitkeep                  # Keeps folder in git while ignoring image contents
│   ├── routers/
│   │   ├── students.py               # Employee CRUD + /register endpoint
│   │   ├── recognition.py            # Face recognition + attendance marking
│   │   └── attendance.py             # Attendance records, today stats, reports data
│   └── services/
│       └── face_service.py           # DeepFace embedding, liveness check, matching logic
│
├── frontend/                         # Django frontend (Python)
│   ├── manage.py                     # Django management utility
│   ├── setup_hr_user.py              # One-time: creates the HR admin user in Django auth DB
│   ├── requirements.txt              # Frontend Python dependencies
│   ├── hr_auth.db                    # Django auth SQLite DB (auto-created, git-ignored)
│   ├── attendance_frontend/
│   │   ├── settings.py               # Django settings (FASTAPI_BASE_URL, HR credentials)
│   │   ├── urls.py                   # Root URL config (includes app.urls)
│   │   └── wsgi.py                   # WSGI entry point
│   └── app/
│       ├── views.py                  # Page view functions (pass API_BASE to templates)
│       ├── urls.py                   # URL patterns for all pages
│       └── templates/app/
│           ├── base.html             # Sidebar, topbar, apiFetch(), showToast(), clock
│           ├── dashboard.html        # Stat cards + today's attendance table
│           ├── attendance.html       # Live camera + recognition result panel
│           ├── register.html         # 3-step employee registration (upload or webcam)
│           ├── students.html         # Employee card grid + delete
│           ├── reports.html          # Filterable attendance log + CSV export
│           └── hr_login.html         # HR-only login form
│
├── .gitignore                        # Excludes DB files, face images, venvs, model weights
├── start_all.bat                     # Windows: start both servers + open browser
├── start_backend.bat                 # Windows: start only the FastAPI backend
├── start_frontend.bat                # Windows: start only the Django frontend
├── install_requirements.bat          # Windows: install all pip dependencies (run once)
└── README.md                         # This file
```

---

## Requirements

### System Requirements
| Requirement | Details |
|---|---|
| **Python** | 3.9, 3.10, or 3.11 (3.10 recommended) |
| **pip** | Latest — run `pip install --upgrade pip` if unsure |
| **RAM** | 4 GB minimum, 8 GB recommended (TensorFlow/DeepFace is memory-heavy) |
| **Disk** | ~2 GB free (DeepFace + TensorFlow model weights) |
| **Webcam** | Required for attendance marking; optional for registration (upload works too) |
| **Internet** | Only on first run — DeepFace downloads the Facenet model (~90 MB) automatically |
| **OS** | Windows 10/11 (bat scripts provided), Linux, macOS |

### Python Package Summary

**Backend (`backend/requirements.txt`)**
```
fastapi==0.110.0          # REST API framework
uvicorn[standard]==0.29.0 # ASGI server
python-multipart==0.0.9   # File upload support
sqlalchemy==2.0.29        # ORM / DB layer
pydantic==2.6.4           # Data validation
deepface==0.0.91          # Face recognition (wraps TensorFlow + Facenet)
opencv-python==4.9.0.80   # Image processing
numpy==1.26.4             # Numerical arrays
pillow==10.3.0            # Image I/O
scipy==1.13.0             # Cosine distance for embedding comparison
mtcnn==0.1.1              # Multi-task CNN face detector
tf-keras>=2.16.0          # Keras 2 shim required by DeepFace on TF 2.16+
aiofiles==23.2.1          # Async file handling
requests==2.31.0          # HTTP client utilities
```

**Frontend (`frontend/requirements.txt`)**
```
django==5.0.4             # Web framework (template rendering only)
```

---

## Quick Start — Windows

### Step 1 — Clone the repository

```cmd
git clone https://github.com/your-username/attendai.git
cd attendai
```

### Step 2 — Install all dependencies (run once)

Double-click **`install_requirements.bat`** or run in a terminal:

```cmd
install_requirements.bat
```

>  This takes 3–10 minutes the first time. It installs FastAPI, DeepFace, TensorFlow, Django, and all supporting packages.

### Step 3 — Start both servers

Double-click **`start_all.bat`** or run:

```cmd
start_all.bat
```

This opens two terminal windows (backend + frontend) and automatically opens your browser to `http://localhost:8000`.

### Step 4 — Register an employee, then mark attendance

See [How to Register an Employee](#how-to-register-an-employee) and [How Attendance Marking Works](#how-attendance-marking-works) below.

---

## Quick Start — Linux / macOS

### Step 1 — Clone the repository

```bash
git clone https://github.com/your-username/attendai.git
cd attendai
```

### Step 2 — Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# On Windows:  venv\Scripts\activate
```

### Step 3 — Install backend dependencies

```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..
```

> **Note:** If you get a TensorFlow error on Apple Silicon (M1/M2/M3), install the Metal version instead:
> ```bash
> pip install tensorflow-macos tensorflow-metal
> ```

### Step 4 — Install frontend dependencies

```bash
cd frontend
pip install -r requirements.txt
cd ..
```

### Step 5 — Initialise the Django database and HR user

```bash
cd frontend
python manage.py migrate --run-syncdb
python setup_hr_user.py
cd ..
```

Expected output from `setup_hr_user.py`:
```
HR user 'hr_admin' created successfully.
Username: hr_admin
Password: HRSecure@2024
```

### Step 6 — Start the backend (Terminal 1)

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### Step 7 — Start the frontend (Terminal 2)

Open a new terminal (keep the backend running):

```bash
cd frontend
python manage.py runserver 0.0.0.0:8000
```

You should see:
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

### Step 8 — Open the app

Navigate to **http://localhost:8000** in your browser.

---

## Running on a Network / Mobile Devices

To use the system from **other devices on your local network** (e.g., employees scanning their face from a mobile phone):

### Step 1 — Find your machine's local IP address

```bash
# Linux/macOS
ip addr show | grep "inet " | grep -v 127.0.0.1
# or
hostname -I

# Windows
ipconfig
# Look for IPv4 Address under your Wi-Fi or Ethernet adapter
```

Example: your IP is `192.168.1.105`

### Step 2 — Update the frontend settings

Edit `frontend/attendance_frontend/settings.py`:

```python
# Change this line:
FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL", "http://localhost:8001")

# To your machine's local IP:
FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL", "http://192.168.1.105:8001")
```

Or set it as an environment variable without editing the file:

```bash
# Linux/macOS
export FASTAPI_BASE_URL=http://192.168.1.105:8001

# Windows CMD
set FASTAPI_BASE_URL=http://192.168.1.105:8001

# Windows PowerShell
$env:FASTAPI_BASE_URL="http://192.168.1.105:8001"
```

### Step 3 — Start servers bound to all interfaces

```bash
# Backend (Terminal 1)
cd backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Frontend (Terminal 2)
cd frontend
python manage.py runserver 0.0.0.0:8000
```

### Step 4 — Access from other devices
| Device | URL |
|---|---|
| Same machine | http://localhost:8000 |
| Other PC on same network | http://192.168.1.105:8000 |
| Mobile phone (same Wi-Fi) | http://192.168.1.105:8000 |

>  **Camera on mobile browsers:** Most mobile browsers require **HTTPS** to access the camera. For local network testing, Chrome on Android is an exception — it allows camera access on `http://192.168.x.x` addresses. For full HTTPS support, consider using [ngrok](https://ngrok.com/) or a self-signed cert.

---

## First-Time Setup Details

### What happens on first run

1. **Backend starts** → SQLAlchemy creates `backend/attendance.db` and all tables automatically
2. **Frontend starts** → Django creates `frontend/hr_auth.db` for session/auth storage
3. **`setup_hr_user.py` runs** → creates the `hr_admin` user in Django's auth system
4. **First face recognition** → DeepFace downloads the Facenet model (~90 MB) to `~/.deepface/weights/`. This only happens once.

### Verifying everything works

1. Open http://localhost:8000 — you should see the Dashboard with 0 employees
2. Check the **green dot** in the bottom-left sidebar — it should say **"API Online"**
3. Open http://localhost:8001/docs — FastAPI Swagger UI should load
4. Register a test employee at http://localhost:8000/register/

---

## Pages & URLs
| URL | Page | Notes |
|---|---|---|
| `http://localhost:8000/` | Dashboard | Stats, today's log |
| `http://localhost:8000/register/` | Register Employee | Upload photo or use webcam |
| `http://localhost:8000/attendance/` | Mark Attendance | Live camera recognition |
| `http://localhost:8000/employees/` | All Employees | View and delete employees |
| `http://localhost:8000/reports/` | Reports | HR login required |
| `http://localhost:8000/hr-login/` | HR Login | For reports access |
| `http://localhost:8001/docs` | API Docs (Swagger) | FastAPI interactive docs |
| `http://localhost:8001/redoc` | API Docs (ReDoc) | Alternative API reference |
| `http://localhost:8001/health` | Health Check | Returns `{"status": "ok"}` |

---

## HR Login

The Reports page is restricted to HR personnel. Default credentials:

```
Username: hr_admin
Password: HRSecure@2024
```

### Changing HR credentials

**Option A — Edit settings.py:**
```python
# frontend/attendance_frontend/settings.py
HR_USERNAME = "your_username"
HR_PASSWORD = "YourSecurePassword"
```
Then re-run `python setup_hr_user.py` to update the Django auth user.

**Option B — Environment variables (recommended for production):**
```bash
export HR_USERNAME=your_username
export HR_PASSWORD=YourSecurePassword
```

---

## How to Register an Employee

1. Go to **http://localhost:8000/register/**
2. **Step 1 — Employee Info:** Enter Name and Employee ID (required), plus optional Email, Department, Designation
3. **Step 2 — Face Photo:** Choose one method:
- **Upload Photo:** Click the drop zone or drag-and-drop a JPG/PNG/WEBP file. A preview appears — use the red  button to remove and re-upload if needed.
- **Use Webcam:** Click "Start Camera", then "Capture Sample" 1–5 times from slightly different angles for best accuracy.
4. **Step 3 — Confirm:** Review details and click **Register Employee**
5. A **success popup** appears with the employee's full details confirming enrolment

### Photo guidelines for best recognition accuracy

- Clear, front-facing photo — face must be visible and centred
- Good, even lighting — no harsh shadows, no backlighting
- No sunglasses, masks, or face coverings
- Neutral expression, eyes open
- No group photos or profile/side-angle shots
- For webcam: capture 3–5 samples from slightly different angles (slight left, right, straight)

---

## How Attendance Marking Works

1. Go to **http://localhost:8000/attendance/**
2. Click **Start Camera** — the webcam feed starts with an animated scanner overlay
3. The system **auto-scans every 4–5 seconds** — no manual action needed
4. When a registered employee's face is detected:
-  **Match found:** Attendance is marked, a green success card appears, the employee is added to Today's Log
-  **Already marked:** The employee was already marked present today — no duplicate record is created
-  **Low confidence:** Face detected but confidence is below threshold — reposition and try again
-  **Not recognized:** Face not in system — direct link to Register page provided
5. Click **Scan Now** to trigger an immediate scan instead of waiting for auto-scan
6. Click the **↻ Flip** button to switch between front/back camera on mobile

### Tips for reliable recognition

- Ensure good, even lighting on your face
- Look directly at the camera, not at an angle
- Stay still for 2–3 seconds while scanning
- Remove glasses if recognition fails consistently
- Stand ~40–80 cm from the camera (not too close, not too far)

---

## API Reference

Full interactive documentation at **http://localhost:8001/docs**

### Employee Endpoints
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/employees/` | List all employees (name, ID, dept) | None |
| `GET` | `/api/employees/stats` | Total employee count | None |
| `GET` | `/api/employees/{id}` | Get single employee by DB ID | None |
| `POST` | `/api/employees/register` | Register new employee with face photo | None |
| `DELETE` | `/api/employees/{id}` | Delete employee and their face image | None |

**Register employee — multipart form fields:**
```
name          string   required   Full name
employee_id   string   required   Unique employee ID (e.g. EMP001)
email         string   optional   Email address
department    string   optional   Department name
designation   string   optional   Job title
image         file     required   Face photo (JPG/PNG/WEBP)
extra_images  string   optional   JSON array of base64 webcam samples
```

### Recognition Endpoint
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/recognize` | Recognize face in base64 image + mark attendance |

**Request body (JSON):**
```json
{
"image": "data:image/jpeg;base64,/9j/4AAQ...",
"session_key": "sess_abc123"
}
```

**Response:**
```json
{
"recognized": true,
"employee_name": "Rajesh Kumar",
"employee_id": "EMP001",
"employee_db_id": 3,
"confidence": 82.4,
"attendance_marked": true,
"already_marked": false,
"message": " Attendance marked for Rajesh Kumar at 09:14:32"
}
```

### Attendance Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/attendance/today` | Today's records + present/absent counts |
| `GET` | `/api/attendance/stats` | Dashboard stats (week total, today counts) |
| `GET` | `/api/attendance/?date=YYYY-MM-DD&employee_id=EMP001` | Filtered records (max 500) |
| `DELETE` | `/api/attendance/{id}` | Delete a single attendance record |

### Health
| Method | Endpoint | Response |
|---|---|---|
| `GET` | `/health` | `{"status": "ok"}` |

---

## Configuration

### Backend — `backend/services/face_service.py`

```python
# Recognition thresholds
COSINE_THRESHOLD         = 0.45   # Max cosine distance to accept a match
# Lower = stricter. Range: 0.0 (exact) to 1.0 (anything)
MIN_CONFIDENCE_PCT       = 55.0   # Min confidence % to mark attendance (below = scan again)
DUPLICATE_FACE_THRESHOLD = 0.40   # Cosine threshold for duplicate-face check at registration

# Liveness / anti-spoofing
TEXTURE_MIN = 30.0    # Laplacian variance below this = reject (too smooth = screen/photo)
TEXTURE_MAX = 6000.0  # Laplacian variance above this = reject (printed photo moiré)
# Frame variation std below 0.3 after 3+ frames = reject (static image held to camera)
```

### Frontend — `frontend/attendance_frontend/settings.py`

```python
# URL the browser uses to call the FastAPI backend
FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL", "http://localhost:8001")

# HR portal credentials
HR_USERNAME = os.environ.get("HR_USERNAME", "hr_admin")
HR_PASSWORD = os.environ.get("HR_PASSWORD", "HRSecure@2024")

# Timezone (used for Django session/auth timestamps)
TIME_ZONE = "Asia/Kolkata"   # Change to your timezone, e.g. "UTC", "America/New_York"
```

---

## Security & Anti-Spoofing

### 1. Liveness Detection

Every camera frame sent for attendance goes through two checks before face matching:

**Texture check (Laplacian variance):**
- A phone screen showing a face photo is coated in flat glass with an LCD pixel grid → very smooth → low Laplacian score (< 30)
- A real live face has organic skin texture, pores, hair → score 100–4000+
- Printed photos with moiré pattern can score very high → also rejected (> 6000)

**Frame variation check:**
- A static photo held to the camera produces near-zero brightness variation across consecutive frames (std < 0.3)
- A live person breathing, blinking, and micro-moving produces measurable variation (std > 0.3)
- Check only activates after 3+ frames are accumulated to avoid false positives on the first scan

### 2. Duplicate Face Guard

During registration, the new face embedding is compared against every existing employee. If cosine distance < 0.40 (the same person), registration is rejected with a clear message identifying the existing employee. This prevents one person from registering multiple times under different IDs.

### 3. Confidence Threshold

Recognition only marks attendance if:
- Cosine distance < 0.45 (reasonably similar face)
- Computed confidence ≥ 55% (1 − distance, expressed as %)

Anything below threshold returns a "scan again" prompt rather than a wrong match or silence.

### 4. One-Attendance-Per-Day

The database has a unique constraint on `(employee_db_id, date)`. Even if the same face is scanned multiple times, attendance is only recorded once per employee per calendar day.

---

## Git Setup

### Initial push to GitHub

```bash
# 1. Initialize git in the project root
cd attendance_fixed
git init

# 2. Add all files (the .gitignore already excludes DB files, face images, venvs)
git add .

# 3. Verify what will be committed (should NOT include *.db, face_db/*.jpg, venv/)
git status

# 4. First commit
git commit -m "feat: initial commit — AttendAI face recognition attendance system"

# 5. Create a repo on GitHub (via web UI or GitHub CLI)
gh repo create attendai --public --source=. --remote=origin
# OR if you already created the repo on GitHub:
git remote add origin https://github.com/your-username/attendai.git

# 6. Push
git branch -M main
git push -u origin main
```

### What the `.gitignore` excludes

```
*.db / *.sqlite3          # Runtime databases (auto-created on first run)
backend/face_db/*.jpg     # Biometric face images — never commit these
backend/face_db/*.png
venv/ / .venv/ / env/     # Virtual environments
.deepface/                # Downloaded model weights (hundreds of MB)
*.log                     # Log files
.env / .env.local         # Secret environment files
.DS_Store / Thumbs.db     # OS junk files
```

### Recommended branch strategy

```bash
main          # stable, production-ready
dev           # active development
feature/xyz   # individual features

# Workflow
git checkout -b feature/add-csv-export
# ... make changes ...
git commit -m "feat: add CSV export to reports page"
git push origin feature/add-csv-export
# Open pull request → merge into dev → merge dev into main for releases
```

### Commit message conventions

```
feat:     new feature (register employee, export CSV)
fix:      bug fix (image preview, liveness threshold)
refactor: code restructure without behavior change
docs:     README or comment updates
chore:    dependency updates, config changes
```

---

## Troubleshooting
| Problem | Likely Cause | Solution |
|---|---|---|
| **Red dot — "API Offline"** in sidebar | Backend not running or wrong port | Run `start_backend.bat` or `uvicorn main:app --port 8001 --reload` in `backend/` |
| **Image preview doesn't show** after upload | Browser cache issue | Hard refresh: `Ctrl + Shift + R` (Windows) / `Cmd + Shift + R` (Mac) |
| **"No face detected"** during registration | Poor lighting, angle, or glasses | Use good frontal lighting, remove glasses, look directly at camera |
| **"Confidence too low — scan again"** | Face partially obscured or poor lighting | Centre face in viewfinder, improve lighting |
| **Attendance not marking — always "Not Recognized"** | Embedding mismatch (registration photo vs live scan) | Re-register with webcam multi-sample (3–5 captures) instead of a single uploaded photo |
| **"Liveness check failed: too smooth"** | Anti-spoofing triggering on compressed mobile frame | Ensure you're using a live camera, not holding a photo. If using a real camera, clean the lens |
| **DeepFace hangs on first recognition** | Downloading Facenet model (~90 MB) | Wait — this is a one-time download. Check internet connection if it takes > 5 min |
| **`No module named 'tf_keras'`** | TensorFlow 2.16+ compatibility issue | Run: `pip install tf-keras` inside the backend folder / venv |
| **`ModuleNotFoundError: deepface`** | Backend venv not activated or install failed | Activate venv and re-run `pip install -r requirements.txt` |
| **Port 8001 already in use** | Another process using the port | Kill it: `lsof -ti:8001 | xargs kill` (Linux/Mac) or check Task Manager (Windows) |
| **Port 8000 already in use** | Django already running or another service | Change port: `python manage.py runserver 8080` (update `start_frontend.bat` too) |
| **HR login not working** | HR user not created in Django auth DB | Run: `cd frontend && python setup_hr_user.py` |
| **Camera not starting on mobile** | HTTPS required for camera API | Use Chrome on Android (allows camera on local IPs), or set up ngrok for HTTPS |
| **Face recognized but attendance not marked** | Already marked today | This is correct behavior — one record per employee per day |
| **`UNIQUE constraint failed: attendance`** | Race condition on double-scan | Safe to ignore — the unique constraint prevents duplicate records correctly |
| **Slow recognition (5–15 seconds)** | TensorFlow loading on slow CPU | Normal on first few scans; subsequent scans are faster once TF is warm |

---

## FAQ

**Q: Does this work without an internet connection?**
Yes — after the first run (which downloads the ~90 MB Facenet model), the system is fully offline. All data stays on your machine.

**Q: Where is the face data stored?**
Face embeddings (mathematical vectors, not photos) are stored in `backend/attendance.db`. Face reference photos are saved in `backend/face_db/`. Both are excluded from git.

**Q: Can multiple employees be scanned at the same time?**
No — the system processes one face at a time per camera frame. In practice, only one person should stand in front of the camera during each scan.

**Q: How accurate is the recognition?**
In good lighting with a clear frontal face: 90–98% accuracy. Accuracy drops with poor lighting, partial occlusion, or a very different appearance from the registration photo. Using multi-sample webcam registration (3–5 captures) significantly improves accuracy vs. a single uploaded photo.

**Q: Can I use a phone as the camera for attendance?**
Yes — open the attendance page on a mobile browser. The phone's front or back camera will be used. Make sure the backend URL is set to your machine's local IP (see [Running on a Network](#running-on-a-network--mobile-devices)).

**Q: How do I back up the data?**
Copy `backend/attendance.db` (all attendance records + employee embeddings) and `backend/face_db/` (face reference photos). That's the entire data set.

**Q: Can I reset all data and start fresh?**
Delete `backend/attendance.db` and all files in `backend/face_db/`. The database will be recreated automatically on next backend start.

**Q: How do I add more departments to the register form?**
Edit the `<select id="department">` options in `frontend/app/templates/app/register.html`.

---

## Acknowledgements

- [DeepFace](https://github.com/serengil/deepface) by Sefik Ilkin Serengil — the face recognition backbone
- [FaceNet](https://arxiv.org/abs/1503.03832) — Schroff et al., Google — the embedding model
- [FastAPI](https://fastapi.tiangolo.com/) — Sebastián Ramírez — the backend framework
- [MTCNN](https://github.com/ipazc/mtcnn) — face detection

---

## License

MIT License — free to use, modify, and distribute for personal and commercial projects.
