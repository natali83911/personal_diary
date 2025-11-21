from django import forms

from .models import Habit, HabitRecord


class HabitForm(forms.ModelForm):
    """
    Форма для создания и редактирования привычки.

    Использует модель Habit и поля:
    - name
    - description
    - is_active
    """

    class Meta:
        model = Habit
        fields = ["name", "description", "is_active"]


class HabitRecordForm(forms.ModelForm):
    """
    Форма для создания и редактирования отметки привычки.

    Использует модель HabitRecord и поле:
    - done (статус выполнения)
    """

    class Meta:
        model = HabitRecord
        fields = ["done"]
