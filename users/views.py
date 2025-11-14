from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView, View)

from config.settings import EMAIL_HOST_USER
from users.forms import CustomUserCreationForm, UserUpdateForm

User = get_user_model()


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        self.object = user
        # Генерация email с подтверждением
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        host = self.request.get_host()
        url = f"http://{host}{reverse_lazy('users:email_confirm', kwargs={'uidb64': uid, 'token': token})}"
        send_mail(
            subject="Подтверждение почты",
            message=f"Здравствуйте, перейдите по ссылке для подтверждения почты {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        messages.success(self.request, "Проверьте почту для подтверждения регистрации.")
        return HttpResponseRedirect(self.get_success_url())


def email_verification(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        messages.success(request, "Почта подтверждена. Вы можете войти в систему.")
        return redirect("users:login")
    else:
        messages.error(request, "Ссылка недействительна или просрочена.")
        return redirect("users:register")


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "users/dashboard.html")


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    raise_exception = True
    login_url = reverse_lazy("users:login")

    def test_func(self):
        return (
            self.request.user.is_superuser
            or self.request.user.groups.filter(name="moderators").exists()
        )


class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = "users/user_detail.html"
    raise_exception = True
    login_url = reverse_lazy("users:login")

    def test_func(self):
        obj = self.get_object()
        # Суперпользователь всегда имеет доступ
        if self.request.user.is_superuser:
            return True
        # Пользователь может видеть/редактировать/удалять только себя
        return obj == self.request.user


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/user_form.html"
    raise_exception = True
    login_url = reverse_lazy("users:login")

    def test_func(self):
        obj = self.get_object()
        # Суперпользователь всегда имеет доступ
        if self.request.user.is_superuser:
            return True
        # Пользователь может видеть/редактировать/удалять только себя
        return obj == self.request.user

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy("users:user_list.html")
        return reverse_lazy("users:dashboard")


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = "users/user_delete.html"
    raise_exception = True
    login_url = reverse_lazy("users:login")

    def test_func(self):
        obj = self.get_object()
        # Суперпользователь всегда имеет доступ
        if self.request.user.is_superuser:
            return True
        # Пользователь может видеть/редактировать/удалять только себя
        return obj == self.request.user

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy("users:user_list.html")
        return reverse_lazy("users:dashboard")
