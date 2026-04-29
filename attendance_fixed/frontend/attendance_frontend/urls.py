from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),   # Django admin (required by INSTALLED_APPS)
    path("", include("app.urls")),
]
