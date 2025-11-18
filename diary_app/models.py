import calendar
from datetime import datetime

from django.db import models
from django.utils.text import slugify

from config import settings


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
        settings.AUTH_USER_MODEL,
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
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while DiaryEntry.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Запись дневника"
        verbose_name_plural = "Записи дневника"
        ordering = ["-created_at"]


class EventCalendar(calendar.HTMLCalendar):
    def __init__(self, events):
        super().__init__()
        self.events = self.group_by_day(events)

    def group_by_day(self, events):
        # Группируем события (DiaryEntry) по дню месяца
        events_per_day = {}
        for event in events:
            day = event.created_at.day  # Здесь берем созданную дату
            events_per_day.setdefault(day, []).append(event)
        return events_per_day

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # пустые дни в календаре
        cssclass = self.cssclasses[weekday]
        today = datetime.today().day

        if day == today:
            cssclass += " today"  # подсветка текущего дня

        if day in self.events:
            cssclass += " eventday"  # подсветка дней с событиями
            body = f'<span class="day">{day}</span><ul>'
            for event in self.events[day]:
                # Отображаем заголовок записи дневника (event.title)
                body += f"<li>{event.title}</li>"
            body += "</ul>"
            return f'<td class="{cssclass}">{body}</td>'
        return f'<td class="{cssclass}"><span class="day">{day}</span></td>'


class Attachment(models.Model):
    diary_entry = models.ForeignKey(
        DiaryEntry,
        related_name="attachments",
        on_delete=models.CASCADE,
        verbose_name="Запись дневника",
    )
    file = models.FileField(
        upload_to="attachments/",
        verbose_name="Файл",
        help_text="Загрузите файл (макс. 5MB, jpg/png/pdf)",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    def __str__(self):
        return self.file.name
