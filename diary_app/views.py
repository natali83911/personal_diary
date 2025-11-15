from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import DiaryEntryForm
from .models import DiaryEntry, EventCalendar


class DiaryEntryListView(LoginRequiredMixin, ListView):
    model = DiaryEntry
    template_name = "diary/entry_list.html"
    context_object_name = "entries"
    paginate_by = 10

    def get_queryset(self):
        queryset = DiaryEntry.objects.filter(user=self.request.user)
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )
        return queryset.order_by("-created_at")


class DiaryEntryDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = DiaryEntry
    context_object_name = "entry"
    template_name = "diary/entry_detail.html"

    def test_func(self):
        entry = self.get_object()
        return entry.user == self.request.user


class DiaryEntryCreateView(LoginRequiredMixin, CreateView):
    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = "diary/entry_create.html"
    success_url = reverse_lazy("diary:entry_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class DiaryEntryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = "diary/entry_create.html"
    success_url = reverse_lazy("diary:entry_list")
    raise_exception = True
    login_url = reverse_lazy("users:login")

    def test_func(self):
        entry = self.get_object()
        return entry.user == self.request.user


class DiaryEntryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = DiaryEntry
    template_name = "diary/entry_delete.html"
    success_url = reverse_lazy("diary:entry_list")

    def test_func(self):
        entry = self.get_object()
        return entry.user == self.request.user


def calendar_view(request, year=None, month=None):
    year = int(year) if year else datetime.now().year
    month = int(month) if month else datetime.now().month

    events = DiaryEntry.objects.filter(created_at__year=year, created_at__month=month)

    cal = EventCalendar(events)
    html_cal = cal.formatmonth(year, month)

    # Рассчитать предыдущий месяц
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    # Рассчитать следующий месяц
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    context = {
        "calendar": html_cal,
        "year": year,
        "month": month,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
    }
    return render(request, "diary/calendar.html", context)
