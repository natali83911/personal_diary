import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import AttachmentForm, DiaryEntryForm, EntrySearchForm
from .models import Attachment, DiaryEntry, EventCalendar
from .utils import TAG_COLORS, get_daily_affirmation, get_tag_color


class DiaryEntryListView(LoginRequiredMixin, ListView):
    """
     Представление списка записей дневника текущего пользователя.

    Отображает записи с возможностью поиска по заголовку, содержимому, тегам и дате.
    Реализует постраничную навигацию.
    """

    model = DiaryEntry
    template_name = "diary/entry_list.html"
    context_object_name = "entries"
    paginate_by = 5

    def get_queryset(self):
        """
        Возвращает отсортированную по дате создания (по убыванию) уникальную выборку записей
        текущего пользователя с фильтрацией по поисковому запросу и дате.
        """
        queryset = DiaryEntry.objects.filter(user=self.request.user)

        # текстовый поиск
        query = self.request.GET.get("query", "").strip()
        filtered_queryset = queryset

        if query:
            filtered_queryset = filtered_queryset.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(tags__name__icontains=query)
            )

            # попытка интерпретировать query как дату YYYY-MM-DD
            try:
                date_query = datetime.datetime.strptime(query, "%Y-%m-%d").date()
                filtered_queryset = filtered_queryset | queryset.filter(
                    created_at__date=date_query
                )
            except ValueError:
                # query не дата — просто игнорируем этот путь
                pass

        # фильтр, приходящий из календаря ?date=YYYY-MM-DD
        date_str = self.request.GET.get("date")
        if date_str:
            try:
                date_query = datetime.datetime.fromisoformat(date_str).date()
                filtered_queryset = filtered_queryset.filter(
                    created_at__year=date_query.year,
                    created_at__month=date_query.month,
                    created_at__day=date_query.day,
                )
            except ValueError:
                pass

        return filtered_queryset.distinct().order_by("-created_at")

    def get_context_data(self, **kwargs):
        """Добавляет в контекст форму поиска и аффирмацию дня."""
        context = super().get_context_data(**kwargs)
        context["search_form"] = EntrySearchForm(self.request.GET)
        context["affirmation"] = get_daily_affirmation()
        return context


class DiaryEntryDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Представление детальной информации о записи дневника.

    Ограничивает доступ только владельцу записи.
    """

    model = DiaryEntry
    context_object_name = "entry"
    template_name = "diary/entry_detail.html"

    def test_func(self):
        """Проверяет, что текущий пользователь является владельцем записи."""
        entry = self.get_object()
        return entry.user == self.request.user


class DiaryEntryCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания новой записи дневника."""

    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = "diary/entry_create.html"
    success_url = reverse_lazy("diary:entry_list")

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос, возвращая пустую форму для создания записи
        вместе с формой прикрепленных файлов.
        """
        self.object = None
        form = self.form_class()
        files_form = AttachmentForm()
        return self.render_to_response(
            self.get_context_data(form=form, files_form=files_form)
        )

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос, валидирует формы, сохраняет запись и прикрепленные файлы,
        либо возвращает ошибки.
        """
        form = self.form_class(request.POST)
        files_form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid() and files_form.is_valid():
            return self.handle_valid_forms(form, files_form)
        else:
            return self.form_invalid(form, files_form)

    def handle_valid_forms(self, form, files_form):
        """Обрабатывает валидные формы, сохраняет запись и прикрепляет файлы."""
        form.instance.user = self.request.user
        self.object = form.save()
        files = files_form.cleaned_data.get("files", [])
        for f in files:
            Attachment.objects.create(diary_entry=self.object, file=f)
        return redirect(self.success_url)

    def form_invalid(self, form, files_form):
        """Возвращает страницу с формой и ошибками."""
        self.object = None
        return self.render_to_response(
            self.get_context_data(form=form, files_form=files_form)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["TAG_COLORS"] = TAG_COLORS
        context["get_tag_color"] = get_tag_color
        if "files_form" not in context:
            context["files_form"] = AttachmentForm()
        return context


class DiaryEntryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Представление для редактирования существующей записи дневника.
    Ограничивает доступ только владельцу.
    """

    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = "diary/entry_update.html"
    success_url = reverse_lazy("diary:entry_list")
    raise_exception = True
    login_url = reverse_lazy("users:login")

    def test_func(self):
        """Проверяет, что текущий пользователь — владелец записи."""
        entry = self.get_object()
        return entry.user == self.request.user

    def get(self, request, *args, **kwargs):
        """Возвращает форму для редактирования записи и формы прикрепления файлов."""
        self.object = self.get_object()
        form = self.form_class(instance=self.object)
        files_form = AttachmentForm()
        return self.render_to_response(
            self.get_context_data(form=form, files_form=files_form)
        )

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос, валидирует формы, обновляет запись и добавляет новые файлы."""
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        files_form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid() and files_form.is_valid():
            return self.handle_valid_forms(form, files_form)
        else:
            return self.form_invalid(form, files_form)

    def handle_valid_forms(self, form, files_form):
        """Обновляет запись и удаляет выбранные вложения."""
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
        """Возвращает страницу с формой и ошибками."""
        return self.render_to_response(
            self.get_context_data(form=form, files_form=files_form)
        )

    def get_context_data(self, **kwargs):
        """Вставляет формы в контекст."""
        context = super().get_context_data(**kwargs)
        context.setdefault("files_form", AttachmentForm())
        return context


class DiaryEntryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Представление для удаления записи дневника."""

    model = DiaryEntry
    template_name = "diary/entry_delete.html"
    success_url = reverse_lazy("diary:entry_list")

    def test_func(self):
        """Проверяет, что текущий пользователь — владелец записи."""
        entry = self.get_object()
        return entry.user == self.request.user


def calendar_view(request, year=None, month=None):
    """
    Функция для отображения календаря с записями в выбранном месяце.

    Параметры:
    - year: год месяца, по умолчанию текущий.
    - month: номер месяца, по умолчанию текущий.
    """
    year = int(year) if year else datetime.datetime.now().year
    month = int(month) if month else datetime.datetime.now().month

    events = DiaryEntry.objects.filter(
        created_at__year=year,
        created_at__month=month,
        user=request.user,
    )

    cal = EventCalendar(events, year=year, month=month)
    html_cal = cal.formatmonth(year, month)
    month_name = EventCalendar.RU_MONTHS[month]

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
        "ru_month": month_name,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
    }
    return render(request, "diary/calendar.html", context)
