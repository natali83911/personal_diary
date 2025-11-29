from django.conf import settings
from django.db import models
from django.utils import timezone


class Habit(models.Model):
    """
    Модель Привычки.

    Поля:
    user (ForeignKey): Пользователь, которому принадлежит привычка.
    name (CharField): Название привычки.
    description (TextField): Описание привычки.
    is_active (BooleanField): Флаг активности привычки (активна/неактивна).
    created_at (DateTimeField): Дата и время создания привычки.

    Метаданные:
    verbose_name - название модели в единственном числе.
    verbose_name_plural - название модели во множественном числе.
    get_latest_by - поле для сортировки по дате создания.
    ordering - порядок сортировки по умолчанию (сначала новые).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="habits"
    )
    name = models.CharField(max_length=255, verbose_name="Название привычки")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        get_latest_by = "created_at"
        ordering = ["-created_at"]


class HabitRecord(models.Model):
    """
    Модель Отметки Привычки (фиксирует дату и состояние выполнения привычки).

    Поля:
    habit (ForeignKey): Ссылка на привычку.
    date (DateField): Дата отметки выполнения.
    done (BooleanField): Выполнена ли привычка в эту дату.

    Метаданные:
    verbose_name - название модели в единственном числе.
    verbose_name_plural - название модели во множественном числе.
    get_latest_by - поле для сортировки по дате отметки.
    unique_together - уникальность сочетания привычки и даты.
    """

    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="records")
    date = models.DateField(default=timezone.now, verbose_name="Дата")
    done = models.BooleanField(default=False, verbose_name="Выполнено")

    class Meta:
        verbose_name = "Отметка привычки"
        verbose_name_plural = "Отметки привычек"
        get_latest_by = "date"
        unique_together = ("habit", "date")

    def __str__(self):
        status = "✓" if self.done else "✗"
        return f"{self.habit.name} - {self.date}: {status}"
