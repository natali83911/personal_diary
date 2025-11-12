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
