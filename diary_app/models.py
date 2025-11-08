from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Тег",
        help_text="Введите название тега",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = [
            "name",
        ]


class DiaryEntry(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="entries",
        verbose_name="Пользователь",
        help_text="Владелец записи дневника",
    )

    title = models.CharField(
        max_length=255, verbose_name="Заголовок", help_text="Введите заголовок записи"
    )

    content = models.TextField(
        verbose_name="Содержание записи", help_text="Введите содержимое записи дневника"
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания записи"
    )

    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата последнего обновления"
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        verbose_name="Теги",
        help_text="Выберите или добавьте теги для записи",
    )

    mood = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Настроение",
        help_text="Опишите настроение (необязательно)",
    )

    is_private = models.BooleanField(
        default=False,
        verbose_name="Приватная запись",
        help_text="Если отмечено, запись видна только вам",
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name="Slug",
        help_text="URL-идентификатор записи, генерируется автоматически",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Запись дневника"
        verbose_name_plural = "Записи дневника"
        ordering = ["-created_at"]
