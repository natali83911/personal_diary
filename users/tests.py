import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from users.forms import CustomUserCreationForm, UserUpdateForm

User = get_user_model()


@pytest.mark.django_db
class CustomUserManagerTests(TestCase):
    """Тесты для менеджера CustomUserManager."""

    def test_create_user_email_normalization(self):
        """Email должен нормализоваться при создании пользователя."""
        user = User.objects.create_user(email="Test@EXAMPLE.com", password="testpass")
        self.assertEqual(user.email, "Test@example.com")

    def test_create_user_without_password(self):
        """Создание пользователя без пароля должно успешно работать."""
        user = User.objects.create_user(email="nopass@example.com")
        self.assertFalse(user.has_usable_password())
        self.assertEqual(user.email, "nopass@example.com")

    def test_create_user_success(self):
        """Проверка успешного создания обычного пользователя с email и паролем."""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_no_email(self):
        """Убедиться, что создание пользователя без email вызывает ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass123")

    def test_create_superuser_success(self):
        """Проверка успешного создания суперпользователя с is_staff и is_superuser=True."""
        admin_user = User.objects.create_superuser(
            email="admin@example.com", password="adminpass"
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_create_superuser_invalid_flags(self):
        """Проверка, что создание суперпользователя с неправильными флагами вызывает ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin2@example.com", password="adminpass", is_staff=False
            )
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin3@example.com", password="adminpass", is_superuser=False
            )


@pytest.mark.django_db
class CustomUserTests(TestCase):
    """Тесты модели CustomUser."""

    def test_str_method_returns_email(self):
        """Метод __str__ должен возвращать email пользователя."""
        user = User.objects.create_user(email="user@example.com", password="pass")
        self.assertEqual(str(user), "user@example.com")


@pytest.mark.django_db
class CustomUserCreationFormTests(TestCase):
    """Тесты формы создания пользователя CustomUserCreationForm."""

    def test_form_valid_data(self):
        """Проверка валидности формы с правильными данными."""
        form_data = {
            "email": "newuser@example.com",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        """Проверка ошибки при несовпадении паролей."""
        form_data = {
            "email": "newuser@example.com",
            "password1": "password1",
            "password2": "password2",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_form_missing_email(self):
        """Проверка, что форма невалидна при отсутствии email."""
        form_data = {
            "email": "",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


@pytest.mark.django_db
class UserUpdateFormTests(TestCase):
    """Тесты формы обновления пользователя UserUpdateForm."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="pass"
        )

    def test_clean_email_unique(self):
        """Проверяет уникальность email в обновлении. Повторяющийся email должен вызвать ошибку."""
        other_user = User.objects.create_user(
            email="other@example.com", password="pass"
        )
        form_data = {
            "email": other_user.email,
            "username": "testuser",
        }
        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_clean_avatar_invalid_size_or_type(self):
        """Проверяет валидацию размера и типа файла аватара."""

        # Слишком большой файл
        big_file = SimpleUploadedFile(
            "avatar.png", b"x" * (2 * 1024 * 1024 + 1), content_type="image/png"
        )
        form = UserUpdateForm(
            data={"email": "newemail@example.com"},
            files={"avatar": big_file},
            instance=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("avatar", form.errors)

        # Неподходящий тип файла
        bad_file = SimpleUploadedFile("avatar.txt", b"test", content_type="text/plain")
        form = UserUpdateForm(
            data={"email": "newemail@example.com"},
            files={"avatar": bad_file},
            instance=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("avatar", form.errors)

    def test_clean_email_same_user(self):
        """Обновление email на тот же, что и у текущего пользователя, не вызывает ошибку."""
        form_data = {
            "email": self.user.email,
            "username": "testuser",
        }
        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_clean_avatar_blank(self):
        """Аватар необязателен, пустой файл пропускается."""
        form = UserUpdateForm(
            data={"email": "newemail@example.com"},
            files={},
            instance=self.user,
        )
        self.assertTrue(form.is_valid())
