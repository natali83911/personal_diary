from django import forms

from .models import DiaryEntry, Tag


class DiaryEntryForm(forms.ModelForm):
    """
    Форма для создания и редактирования записи дневника.

    Поле tags реализовано с помощью нескольких чекбоксов.
    """

    MOOD_CHOICES = [
        ("радость", "Радость"),
        ("грусть", "Грусть"),
        ("спокойствие", "Спокойствие"),
        ("раздражение", "Раздражение"),
        ("энергия", "Энергия"),
        ("", "Другое/Не выбрано"),
    ]
    mood = forms.ChoiceField(
        choices=MOOD_CHOICES,
        required=False,
        label="Настроение",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Теги",
    )

    class Meta:
        model = DiaryEntry
        fields = ["title", "content", "tags", "mood", "is_private"]


class MultiFileInput(forms.FileInput):
    """Кастомный виджет для загрузки нескольких файлов одновременно."""

    allow_multiple_selected = True


class AttachmentForm(forms.Form):
    """
    Форма для загрузки одного или нескольких файлов, прикрепляемых к записи дневника.

    Валидирует размер и тип файлов.
    """

    files = forms.Field(
        widget=MultiFileInput(attrs={"multiple": True}),
        required=False,
        label="Прикрепить файлы",
        help_text="Можно выбрать несколько файлов (jpg, png, pdf)",
    )

    def clean_files(self):
        """
        Проверяет каждый файл: тип содержимого и размер (макс 15MB).
        Возвращает список файлов или вызывает ошибку валидации.
        """
        files = self.files.getlist("files") if self.files else []
        allowed_content_types = ["image/jpeg", "image/png", "application/pdf"]
        max_file_size = 15 * 1024 * 1024  # 15MB
        for f in files:
            if f.size > max_file_size:
                raise forms.ValidationError(
                    f"Файл {f.name} слишком большой (макс 15MB)."
                )
            if f.content_type not in allowed_content_types:
                raise forms.ValidationError(f"Недопустимый тип файла: {f.name}")
        return files


class EntrySearchForm(forms.Form):
    """
    Форма для поиска записей дневника по текстовому запросу.

    Поле query — необязательное текстовое поле с максимальной длиной 255 символов.
    """

    query = forms.CharField(label="Поиск", max_length=255, required=False)
