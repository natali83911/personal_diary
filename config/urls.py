from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("diary_app.urls", namespace="diary_app")),
    path("users/", include("users.urls", namespace="users")),
]
