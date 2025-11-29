from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Менеджер для кастомной модели пользователя CustomUser.
    Обеспечивает создание обычных пользователей и суперпользователей с использованием email как идентификатора.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет пользователя с указанным email и паролем.
        Если email не указан, выбрасывает исключение.
        """
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        extra_fields.setdefault("username", email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Создает и сохраняет суперпользователя с административными правами.
        Устанавливает флаги is_staff и is_superuser в True, иначе возвращает ошибку.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser должен иметь is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя с использованием email в качестве уникального идентификатора вместо username.

    Поля:
    - username: необязательное, может быть пустым.
    - email: обязательный, уникальный email.
    - avatar: изображение профиля пользователя (опционально).
    - token: произвольный токен для различных нужд (опционально).
    """

    username = models.CharField(max_length=150, unique=True, blank=True, null=True)

    email = models.EmailField(_("email адрес"), unique=True)

    avatar = models.ImageField(
        upload_to="users/avatars/", verbose_name="Аватар", blank=True, null=True
    )

    token = models.CharField(
        max_length=100, verbose_name="Токен", blank=True, null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        """Возвращает email пользователя для удобства отображения."""
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("view_user", "Can view user"),
        ]
