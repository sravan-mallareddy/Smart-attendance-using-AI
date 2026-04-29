from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def _ctx(request, extra=None):
    ctx = {
        "API_BASE": settings.FASTAPI_BASE_URL,
        "is_hr": request.user.is_authenticated,
    }
    if extra:
        ctx.update(extra)
    return ctx


def dashboard(request):
    return render(request, "app/dashboard.html", _ctx(request))


def attendance(request):
    return render(request, "app/attendance.html", _ctx(request))


@login_required
def register(request):
    """Employee registration — HR only."""
    # Extra safety: only allow staff/superuser accounts (HR)
    if not (request.user.is_staff or request.user.is_superuser):
        logout(request)
        return redirect(f"/hr-login/?next=/register/")
    return render(request, "app/register.html", _ctx(request))


def employees(request):
    return render(request, "app/students.html", _ctx(request))


@login_required
def reports(request):
    return render(request, "app/reports.html", _ctx(request))


def hr_login(request):
    """HR-only login page for the Reports section."""
    if request.user.is_authenticated:
        return redirect("reports")

    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Only allow staff/superusers (HR accounts)
            if user.is_staff or user.is_superuser:
                login(request, user)
                next_url = request.GET.get("next", "/reports/")
                return redirect(next_url)
            else:
                error = "Access denied. Only HR personnel can access Reports."
        else:
            error = "Invalid username or password."

    return render(request, "app/hr_login.html", {"error": error})


def device_verify(request):
    return render(request, "app/device_verify.html", _ctx(request))



def hr_logout(request):
    logout(request)
    return redirect("dashboard")
