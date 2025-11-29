from django.urls import path

from .views import (HabitCreateView, HabitDeleteView, HabitListView,
                    HabitRecordToggleView, HabitUpdateView)

app_name = "habits_app"

urlpatterns = [
    path("", HabitListView.as_view(), name="habit_list"),
    path("new/", HabitCreateView.as_view(), name="habit_create"),
    path("<int:pk>/edit/", HabitUpdateView.as_view(), name="habit_update"),
    path("<int:pk>/delete/", HabitDeleteView.as_view(), name="habit_delete"),
    path(
        "<int:habit_id>/toggle/", HabitRecordToggleView.as_view(), name="habit_toggle"
    ),
]
