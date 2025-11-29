from django.contrib import admin

from .models import Habit, HabitRecord


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """
    Админка для модели Habit (Привычка).

    Отображает поля: название, пользователь-владелец, активность и дату создания.
    Позволяет фильтровать записи по активности и дате создания.
    Включает поиск по названию привычки и email пользователя.
    Записи по умолчанию сортируются по дате создания (сначала новые).
    """

    list_display = ("name", "user", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "user__email")
    ordering = ("-created_at",)


@admin.register(HabitRecord)
class HabitRecordAdmin(admin.ModelAdmin):
    """
    Админка для модели HabitRecord (Отметка привычки).

    Отображает поля: привычка, дата, статус выполнения.
    Позволяет фильтровать отметки по статусу выполнения и дате.
    Включает поиск по названию связанной привычки.
    Записи сортируются по дате в порядке убывания.
    """

    list_display = ("habit", "date", "done")
    list_filter = ("done", "date")
    search_fields = ("habit__name",)
    ordering = ("-date",)
