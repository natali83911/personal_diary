from django import forms

from .models import DiaryEntry, Tag


class DiaryEntryForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Теги",
    )

    class Meta:
        model = DiaryEntry
        fields = ["title", "content", "tags", "mood", "is_private"]
        widgets = {
            "tags": forms.SelectMultiple(attrs={"class": "form-select", "size": "5"}),
        }


class MultiFileInput(forms.FileInput):
    allow_multiple_selected = True


class AttachmentForm(forms.Form):
    files = forms.Field(
        widget=MultiFileInput(attrs={"multiple": True}),
        required=False,
        label="Прикрепить файлы",
        help_text="Можно выбрать несколько файлов (jpg, png, pdf)",
    )

    def clean_files(self):
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
