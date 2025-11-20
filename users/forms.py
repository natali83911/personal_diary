from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Форма создания пользователя с обязательным полем email."""

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    email = forms.EmailField(label="Email", required=True)


class UserUpdateForm(forms.ModelForm):
    """
    Форма обновления данных пользователя: username, email, avatar.

    Валидация:
    - Проверка уникальности email.
    - Проверка типа и размера загружаемого аватара (макс 2 Мб, только изображения).
    """

    username = forms.CharField(
        max_length=150,
        required=False,
        label="Имя пользователя",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        required=True,
        label="Email адрес",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    avatar = forms.ImageField(
        required=False,
        label="Аватар",
        widget=forms.ClearableFileInput(attrs={"class": "form-control-file"}),
    )

    class Meta:
        model = User
        fields = ["username", "email", "avatar"]

    def clean_email(self):
        """Проверяет, что email уникален среди всех пользователей, кроме текущего."""
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean_avatar(self):
        """Проверяет размер и тип загружаемого файла аватара."""
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Максимальный размер аватара 2 Мб")
            if not avatar.content_type.startswith("image/"):
                raise forms.ValidationError("Загрузите изображение")
        return avatar
