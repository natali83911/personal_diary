from django.urls import path

from users.views import (
    DashboardView,
    RegisterView,
    UserDeleteView,
    UserDetailView,
    UserListView,
    UserUpdateView,
    email_verification,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("email-confirm/<uidb64>/<token>/", email_verification, name="email_confirm"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    # Пользователи - доступно только суперпользователю
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("users/<int:pk>/edit/", UserUpdateView.as_view(), name="user_update"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user_delete"),
]
