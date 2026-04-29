AttendAI
AI-powered face recognition attendance system. Fully local — no cloud, no subscription, no data leaves your machine.

Tech Stack
LayerTechnologyBackend APIFastAPI + UvicornFace RecognitionDeepFace (Facenet model)Face DetectionMTCNN + OpenCVDatabaseSQLite via SQLAlchemyFrontendDjango (server-rendered templates)UIVanilla JS + CSS

Requirements

Python 3.9, 3.10, or 3.11
Webcam (for attendance marking)
~2 GB free disk space (TensorFlow + DeepFace model weights)
Internet on first run only (DeepFace downloads the Facenet model ~90 MB automatically)


Getting Started
Windows
cmd# 1. Clone the repo
git clone https://github.com/your-username/attendai.git
cd attendai

# 2. Install dependencies (run once)
install_requirements.bat

# 3. Start both servers
start_all.bat
The app opens automatically at http://localhost:8000.

Linux / macOS
bash# 1. Clone the repo
git clone https://github.com/your-username/attendai.git
cd attendai

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# 4. Install frontend dependencies
cd frontend
pip install -r requirements.txt

# 5. Set up the database and HR user
python manage.py migrate --run-syncdb
python setup_hr_user.py
cd ..
Then start each server in a separate terminal:
bash# Terminal 1 - Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend
cd frontend
python manage.py runserver 0.0.0.0:8000
Open http://localhost:8000 in your browser.

Default Credentials
The Reports section requires HR login:
Username: hr_admin
Password: HRSecure@2024

Pages
URLPagehttp://localhost:8000/Dashboardhttp://localhost:8000/register/Register Employeehttp://localhost:8000/attendance/Mark Attendancehttp://localhost:8000/employees/All Employeeshttp://localhost:8000/reports/Reports (HR login required)http://localhost:8001/docsAPI Docs (Swagger)
