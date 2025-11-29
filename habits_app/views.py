from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import HabitForm
from .models import Habit, HabitRecord


class HabitListView(LoginRequiredMixin, ListView):
    """
    Представление списка активных привычек пользователя.

    Отображает все привычки, принадлежащие текущему пользователю и имеющие флаг is_active=True.
    Результаты сортируются по дате создания в порядке убывания.
    """

    model = Habit
    template_name = "habits/habit_list.html"
    context_object_name = "habits"

    def get_queryset(self):
        """Возвращает QuerySet привычек пользователя для отображения."""
        return Habit.objects.filter(user=self.request.user, is_active=True).order_by(
            "-created_at"
        )


class HabitCreateView(LoginRequiredMixin, CreateView):
    """
    Представление создания новой привычки.

    Отображает форму для создания привычки и сохраняет её, связывая с текущим пользователем.
    При успешном сохранении перенаправляет на список привычек.
    """

    model = Habit
    form_class = HabitForm
    template_name = "habits/habit_form.html"
    success_url = reverse_lazy("habits:habit_list")

    def form_valid(self, form):
        """Автоматически устанавливает текущего пользователя как владельца привычки."""
        form.instance.user = self.request.user
        return super().form_valid(form)


class HabitUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Представление редактирования существующей привычки.

    Доступно только владельцу привычки.
    """

    model = Habit
    form_class = HabitForm
    template_name = "habits/habit_form.html"
    success_url = reverse_lazy("habits:habit_list")

    def test_func(self):
        """Проверяет, является ли текущий пользователь владельцем привычки."""
        habit = self.get_object()
        return habit.user == self.request.user


class HabitDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Представление удаления привычки.

    Доступно только владельцу привычки.
    После удаления перенаправляет на список привычек.
    """

    model = Habit
    template_name = "habits/habit_confirm_delete.html"
    success_url = reverse_lazy("habits:habit_list")

    def test_func(self):
        """Проверяет, является ли текущий пользователь владельцем привычки."""
        habit = self.get_object()
        return habit.user == self.request.user


class HabitRecordToggleView(LoginRequiredMixin, View):
    """
    Представление для переключения отметки выполнения привычки на текущую дату.

    Если отметка отсутствует, создаёт новую с флагом done=True.
    Если уже существует, переключает состояние done на обратное.
    После обновления перенаправляет на список привычек.
    """

    def post(self, request, habit_id):
        habit = get_object_or_404(Habit, pk=habit_id, user=request.user)
        today = timezone.now().date()

        record, created = HabitRecord.objects.get_or_create(habit=habit, date=today)
        record.done = not record.done
        record.save()

        return redirect("habits:habit_list")
