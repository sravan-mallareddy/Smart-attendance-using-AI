# AttendAI — Smart Employee Attendance System

> AI-powered, face-recognition based attendance tracking. Fully local — no cloud, no subscription, no data leaves your machine.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🎯 Face Recognition | DeepFace + Facenet (128-d embeddings) |
| 🛡️ Anti-Spoofing | Blocks phone photos, printed photos, screen recordings |
| 👥 Duplicate Face Guard | Rejects the same face being registered twice under a different ID |
| 📊 Live Dashboard | Real-time attendance stats, charts, today's log |
| 📋 Reports | Filter by date/employee, sortable table, CSV export |
| 🔒 HR Portal | Protected reports section with separate HR login |
| 🖥️ 100% On-Device | SQLite database, no internet required after install |

---

## 🖼️ Screenshots

| Dashboard | Mark Attendance | Register Employee |
|---|---|---|
| Real-time stats & today's log | Live camera with scan animation | 3-step form with upload or webcam |

---

## 🗂️ Project Structure

```
attendance_fixed_final/
├── backend/                        # FastAPI backend (Python)
│   ├── main.py                     # App entry point, CORS, router registration
│   ├── models.py                   # SQLAlchemy ORM models (Employee, Attendance)
│   ├── schemas.py                  # Pydantic request/response schemas
│   ├── database.py                 # SQLite engine + session factory
│   ├── requirements.txt            # Backend Python dependencies
│   ├── face_db/                    # Face images saved here (auto-created)
│   ├── routers/
│   │   ├── students.py             # Employee CRUD + register endpoint
│   │   ├── recognition.py          # Face recognition + attendance marking
│   │   └── attendance.py           # Attendance records, stats, reports
│   └── services/
│       └── face_service.py         # DeepFace embedding, liveness, matching
│
├── frontend/                       # Django frontend (Python)
│   ├── manage.py
│   ├── setup_hr_user.py            # One-time HR user creation script
│   ├── requirements.txt            # Frontend Python dependencies
│   ├── attendance_frontend/
│   │   ├── settings.py             # Django settings (FASTAPI_BASE_URL, HR creds)
│   │   └── urls.py                 # Root URL config
│   └── app/
│       ├── views.py                # Page views (all pass API_BASE to templates)
│       ├── urls.py                 # App URL patterns
│       └── templates/app/
│           ├── base.html           # Sidebar, topbar, apiFetch(), toast system
│           ├── dashboard.html      # Stats cards + today's attendance table
│           ├── attendance.html     # Live camera + recognition result panel
│           ├── register.html       # 3-step employee registration form
│           ├── students.html       # Employee cards grid with delete
│           ├── reports.html        # Filterable attendance table + CSV export
│           └── hr_login.html       # HR-only login page
│
├── start_all.bat                   # ▶ Start both servers + open browser
├── start_backend.bat               # Start only the FastAPI backend
├── start_frontend.bat              # Start only the Django frontend
└── install_requirements.bat        # Install all dependencies (run once)
```

---

## ⚙️ Requirements

- **Python 3.9 – 3.11** (recommended: 3.10)
- **Windows** (bat scripts) — Linux/Mac: use the manual commands below
- **Webcam** connected to the machine
- ~**2 GB free disk** (DeepFace + TensorFlow model weights)
- Internet on **first run** (DeepFace downloads Facenet model ~90 MB automatically)

---

## 🚀 Quick Start (Windows)

### Step 1 — Install dependencies (once)
```
Double-click: install_requirements.bat
```
This installs all backend and frontend packages. Takes 3–10 min on first run.

### Step 2 — Start both servers
```
Double-click: start_all.bat
```
This opens two terminal windows (backend + frontend) and launches your browser.

### Step 3 — Use the system
| URL | Page |
|---|---|
| http://localhost:8000 | Dashboard |
| http://localhost:8000/register/ | Register Employee |
| http://localhost:8000/attendance/ | Mark Attendance |
| http://localhost:8000/employees/ | All Employees |
| http://localhost:8000/reports/ | Reports (HR login required) |
| http://localhost:8001/docs | FastAPI Swagger docs |

### HR Login Credentials
```
Username: hr_admin
Password: HRSecure@2024
```
> Change these in `frontend/attendance_frontend/settings.py` → `HR_USERNAME` / `HR_PASSWORD`

---

## 🖥️ Manual Start (Linux / Mac)

**Terminal 1 — Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
pip install -r requirements.txt
python manage.py migrate --run-syncdb
python setup_hr_user.py
python manage.py runserver 0.0.0.0:8000
```

---

## 🛡️ Security Features

### 1. Duplicate Face Registration Prevention
When registering a new employee, the system extracts a Facenet embedding from the uploaded photo and compares it against **every existing employee** using cosine distance. If the same face already exists (distance < 0.40), registration is rejected with a clear error message — even if a different Employee ID or name is used.

### 2. Anti-Spoofing / Liveness Detection
Attendance marking runs two spoofing checks on every captured frame:

| Check | How it works | What it blocks |
|---|---|---|
| **Texture analysis** | Laplacian variance of the frame | Phone screens (too smooth, score < 100), printed photos with moiré (score > 4500) |
| **Frame variation** | Std deviation of brightness across 3+ consecutive frames | Static phone/photo held still (variation < 0.8) |

A phone screen showing someone's photo typically scores 30–80 on texture (real faces: 150–3000) **and** shows near-zero frame variation when held still. Both checks must pass.

### 3. Confidence Threshold
Matches are only accepted if confidence ≥ **60%** (cosine distance < **0.40**). Lower confidence triggers a "scan again" prompt rather than marking attendance.

---

## 🔧 Configuration

All key settings are at the top of `backend/services/face_service.py`:

```python
COSINE_THRESHOLD         = 0.40   # Recognition strictness (lower = stricter)
MIN_CONFIDENCE_PCT       = 60.0   # Minimum % to accept a match
DUPLICATE_FACE_THRESHOLD = 0.40   # Same face = same threshold
```

The FastAPI backend URL seen by the frontend is set in `frontend/attendance_frontend/settings.py`:
```python
FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL", "http://localhost:8001")
```
Override via environment variable if deploying to a different host.

---

## 📡 API Reference

The full interactive API is at **http://localhost:8001/docs** when the backend is running.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Backend health check |
| GET | `/api/employees/` | List all employees |
| POST | `/api/employees/register` | Register new employee (multipart) |
| DELETE | `/api/employees/{id}` | Delete employee |
| POST | `/api/recognize` | Recognize face + mark attendance |
| GET | `/api/attendance/today` | Today's attendance records + stats |
| GET | `/api/attendance/stats` | Dashboard stats (present, absent, week) |
| GET | `/api/attendance/` | Filtered attendance records |
| DELETE | `/api/attendance/{id}` | Delete attendance record |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| **API Offline** (red dot in sidebar) | Make sure `start_backend.bat` is running and port 8001 is free |
| **Face not detected** | Use good lighting, face directly at camera, remove glasses |
| **Attendance not marking** | Confidence may be below 60% — ensure face is centred and unobstructed |
| **Spoofing detected** | Do not show a photo to the camera — use your actual face live |
| **Duplicate face error** | That face is already registered under another employee ID |
| **DeepFace download hang** | Allow internet access on first run — model (~90 MB) downloads once to `~/.deepface/` |
| **`No module named 'tf_keras'`** | Run `pip install tf-keras` in the backend folder |
| **Port already in use** | Change `--port 8001` / `--port 8000` in the bat files |
| **HR login not working** | Run `cd frontend && python setup_hr_user.py` to create/reset the HR user |

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI 0.110 + Uvicorn |
| Face Recognition | DeepFace 0.0.91 (Facenet model) |
| Face Detection | MTCNN + OpenCV fallback |
| Database | SQLite (via SQLAlchemy 2.0) |
| Frontend | Django 5.0 (template-rendered) |
| UI | Vanilla JS + CSS custom properties |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙏 Acknowledgements

- [DeepFace](https://github.com/serengil/deepface) by Sefik Ilkin Serengil
- [FaceNet](https://arxiv.org/abs/1503.03832) — Schroff et al., Google
- [FastAPI](https://fastapi.tiangolo.com/) — Sebastián Ramírez
