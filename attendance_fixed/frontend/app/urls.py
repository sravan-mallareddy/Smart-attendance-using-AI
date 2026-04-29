from django.urls import path
from . import views

urlpatterns = [
    path("",             views.dashboard,     name="dashboard"),
    path("attendance/",  views.attendance,    name="attendance"),
    path("register/",    views.register,      name="register"),
    path("employees/",   views.employees,     name="employees"),
    path("reports/",     views.reports,       name="reports"),
    path("device-verify/", views.device_verify, name="device_verify"),
    path("hr-login/",    views.hr_login,      name="hr_login"),
    path("hr-logout/",   views.hr_logout,     name="hr_logout"),
]
