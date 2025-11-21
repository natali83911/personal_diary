from django.urls import path

from .views import (
    DiaryEntryCreateView,
    DiaryEntryDeleteView,
    DiaryEntryDetailView,
    DiaryEntryListView,
    DiaryEntryUpdateView,
    calendar_view,
)

app_name = "diary_app"

urlpatterns = [
    path("", DiaryEntryListView.as_view(), name="entry_list"),
    path("entry/<int:pk>/", DiaryEntryDetailView.as_view(), name="entry_detail"),
    path("entry/new/", DiaryEntryCreateView.as_view(), name="entry_create"),
    path("entry/<int:pk>/edit/", DiaryEntryUpdateView.as_view(), name="entry_update"),
    path("entry/<int:pk>/delete/", DiaryEntryDeleteView.as_view(), name="entry_delete"),
    path("calendar/", calendar_view, name="calendar"),
    path("calendar/<int:year>/<int:month>/", calendar_view, name="calendar_filtered"),
]
