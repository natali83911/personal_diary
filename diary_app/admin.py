from django.contrib import admin

from .models import DiaryEntry, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at", "updated_at", "is_private")
    list_filter = ("is_private", "created_at", "tags")
    search_fields = ("title", "content", "user__email")
    raw_id_fields = ("user",)
    filter_horizontal = ("tags",)
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
