# Bug Fixes & Changes Applied

## Bug Fixes (Original Issues)

### 1. Django App Not Starting — Missing Auth/Session Apps
**Problem:** `settings.py` was missing `django.contrib.auth`, `django.contrib.sessions`,
`django.contrib.messages`, `django.contrib.contenttypes`, and their middleware.
Without these, Django cannot run sessions or authentication at all.

**Fix:** Added all required apps and middleware to `settings.py`.

### 2. DATABASES Was Empty Dict
**Problem:** `DATABASES = {}` meant Django had no database, so sessions and user accounts
couldn't be persisted. This also caused `manage.py migrate` to fail silently.

**Fix:** Added SQLite database (`hr_auth.db`) for Django auth and sessions.
The attendance data still lives in the FastAPI SQLite DB (`attendance.db`), separate and untouched.

### 3. CSRF Middleware Missing
**Problem:** The login form (POST) would fail with 403 Forbidden because
`CsrfViewMiddleware` was not included in the middleware stack.

**Fix:** Added `CsrfViewMiddleware` to `MIDDLEWARE`.

### 4. `_ctx()` helper didn't accept `request`
**Problem:** `views.py` had `def _ctx(extra=None)` which couldn't pass `request`
context, meaning `{{ request.user }}` was unavailable in templates.

**Fix:** Changed signature to `def _ctx(request, extra=None)` and passed `is_hr`
flag into template context.

---

## New Feature: HR-Only Authentication for Reports

### What Was Added

**`views.py`**
- `@login_required` decorator on the `reports` view — unauthenticated users are
  redirected to `/hr-login/` automatically.
- `hr_login(request)` — handles GET (show form) and POST (authenticate + check `is_staff`).
  Regular non-staff accounts are denied even with valid credentials.
- `hr_logout(request)` — logs out and redirects to dashboard.

**`urls.py`**
- Added `hr-login/` and `hr-logout/` URL routes.

**`settings.py`**
- `LOGIN_URL = "/hr-login/"` — Django's `@login_required` redirects here.
- `HR_USERNAME` / `HR_PASSWORD` settings (overridable via environment variables).

**`templates/app/hr_login.html`** — New polished login page matching the app's dark theme.
Includes password show/hide toggle, CSRF protection, and access-denied messaging.

**`templates/app/base.html`** — Reports nav item now shows a 🔒 lock icon for
non-HR users. Sidebar footer shows "HR Login" or "HR Logout" depending on session state.

**`setup_hr_user.py`** — One-time script to create the HR Django superuser.
Run once, or the start scripts run it automatically.

### HR Credentials (Default)
| Field    | Value          |
|----------|----------------|
| Username | `hr_admin`     |
| Password | `HRSecure@2024`|

Change via environment variables before starting:
```
set HR_USERNAME=my_hr_user
set HR_PASSWORD=MyStr0ngP@ss
```

---

## How to Run

```bash
# Option A: Start everything at once
start_all.bat

# Option B: Manual (two terminals)

# Terminal 1 — Backend (FastAPI)
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 — Frontend (Django)
cd frontend
pip install -r requirements.txt
python manage.py migrate --run-syncdb
python setup_hr_user.py
python manage.py runserver 0.0.0.0:8000
```

Open: http://localhost:8000
HR Reports: http://localhost:8000/hr-login/

---

## Original Face Recognition Fixes (from previous version)
- 5-tier face detector fallback strategy (opencv → mtcnn → relaxed modes → skip)
- CLAHE image preprocessing for better webcam performance
- Cosine threshold raised 0.40 → 0.55 for real-world webcam conditions
- Camera warm-up delay before scanning starts
- Mirror transform removed from canvas capture
- Multi-sample (1–5) face registration with averaged embeddings
