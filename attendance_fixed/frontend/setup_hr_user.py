"""
Run ONCE to create the HR admin user:
  cd frontend && python setup_hr_user.py

Credentials are read from settings (overridable via env vars):
  HR_USERNAME  (default: hr_admin)
  HR_PASSWORD  (default: HRSecure@2024)
"""
import os, sys, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendance_frontend.settings")
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

username = settings.HR_USERNAME
password = settings.HR_PASSWORD

if User.objects.filter(username=username).exists():
    u = User.objects.get(username=username)
    u.set_password(password)
    u.is_staff = True
    u.save()
    print(f"[setup] Updated HR user: {username}")
else:
    User.objects.create_superuser(username=username, email="hr@company.com", password=password)
    print(f"[setup] Created HR user: {username}  /  password: {password}")

print("[setup] Done. Run: python manage.py runserver 0.0.0.0:8000")
