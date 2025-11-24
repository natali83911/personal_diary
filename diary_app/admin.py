from django.contrib import admin

from .models import Affirmation, DiaryEntry, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Tag.

    Отображает название тега и позволяет осуществлять поиск по нему.
    """

    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели DiaryEntry.

    Позволяет управлять записями дневника, включая фильтрацию по дате, приватности и тегам.
    Также отображает важные поля, такие как заголовок, пользователь, даты и приватность.
    """

    list_display = ("title", "user", "created_at", "updated_at", "is_private")
    list_filter = ("is_private", "created_at", "tags")
    search_fields = ("title", "content", "user__email")
    raw_id_fields = ("user",)
    filter_horizontal = ("tags",)
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


@admin.register(Affirmation)
class AffirmationAdmin(admin.ModelAdmin):
    list_display = ("text", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("text",)
    list_editable = ("is_active",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    actions = ["activate_affirmations", "deactivate_affirmations"]

    @admin.action(description="Активировать выбранные аффирмации")
    def activate_affirmations(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Деактивировать выбранные аффирмации")
    def deactivate_affirmations(self, request, queryset):
        queryset.update(is_active=False)
