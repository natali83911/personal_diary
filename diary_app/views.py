from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import DiaryEntryForm
from .models import DiaryEntry


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
    template_name = "diary/entry_detail.html"

    def test_func(self):
        entry = self.get_object()
        return entry.user == self.request.user


class DiaryEntryCreateView(LoginRequiredMixin, CreateView):
    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = "diary/entry_form.html"
    success_url = reverse_lazy("diary:entry_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class DiaryEntryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = "diary/entry_form.html"
    success_url = reverse_lazy("diary:entry_list")

    def test_func(self):
        entry = self.get_object()
        return entry.user == self.request.user


class DiaryEntryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = DiaryEntry
    template_name = "diary/entry_confirm_delete.html"
    success_url = reverse_lazy("diary:entry_list")

    def test_func(self):
        entry = self.get_object()
        return entry.user == self.request.user
