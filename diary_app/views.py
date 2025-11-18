from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import AttachmentForm, DiaryEntryForm
from .models import Attachment, DiaryEntry, EventCalendar


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

    def get(self, request, *args, **kwargs):
        self.object = None
        form = self.form_class()
        files_form = AttachmentForm()
        return self.render_to_response(
            self.get_context_data(form=form, files_form=files_form)
        )

    def post(self, request, *args, **kwargs):
        print(f"FILES keys: {request.FILES.keys()}")
        print(f"FILES getlist('files'): {request.FILES.getlist('files')}")
        form = self.form_class(request.POST)
        files_form = AttachmentForm(request.POST, request.FILES)
        print(
            f"Form valid: {form.is_valid()}, files_form valid: {files_form.is_valid()}"
        )
        if form.is_valid() and files_form.is_valid():
            return self.handle_valid_forms(form, files_form)
        else:
            return self.form_invalid(form, files_form)

    def handle_valid_forms(self, form, files_form):
        form.instance.user = self.request.user
        self.object = form.save()
        files = files_form.cleaned_data.get("files", [])
        for f in files:
            Attachment.objects.create(diary_entry=self.object, file=f)
        return redirect(self.success_url)

    def form_invalid(self, form, files_form):
        self.object = None
        return self.render_to_response(
            self.get_context_data(form=form, files_form=files_form)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("files_form", AttachmentForm())
        return context


class DiaryEntryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = "diary/entry_update.html"
    success_url = reverse_lazy("diary:entry_list")
    raise_exception = True
    login_url = reverse_lazy("users:login")

    def test_func(self):
        entry = self.get_object()
        return entry.user == self.request.user

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(instance=self.object)
        files_form = AttachmentForm()
        return self.render_to_response(
            self.get_context_data(form=form, files_form=files_form)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        files_form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid() and files_form.is_valid():
            return self.handle_valid_forms(form, files_form)
        else:
            return self.form_invalid(form, files_form)

    def handle_valid_forms(self, form, files_form):
        # Удаление отмеченных вложений
        delete_ids = self.request.POST.getlist("delete_files")
        if delete_ids:
            Attachment.objects.filter(
                pk__in=delete_ids, diary_entry=self.object
            ).delete()

        self.object = form.save()

        # Добавление новых файлов
        files = files_form.cleaned_data.get("files", [])
        for f in files:
            Attachment.objects.create(diary_entry=self.object, file=f)

        return redirect(self.success_url)

    def form_invalid(self, form, files_form):
        return self.render_to_response(
            self.get_context_data(form=form, files_form=files_form)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("files_form", AttachmentForm())
        return context


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
