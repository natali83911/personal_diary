import calendar
from datetime import date, datetime

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from config import settings
from diary_app.utils import get_mood_style


class Tag(models.Model):
    """
    Модель для тегов записей дневника.

    Поля:
    - name: уникальное название тега, используется для категоризации записей.
    """

    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Тег",
        help_text="Введите название тега",
    )

    def __str__(self):
        """Возвращает название тега для удобного отображения."""
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = [
            "name",
        ]


class DiaryEntry(models.Model):
    """
    Модель записи личного дневника.

    Поля:
    - user: владелец записи (пользователь).
    - title: заголовок записи.
    - content: текстовое содержимое записи.
    - created_at: дата и время создания.
    - updated_at: дата и время последнего обновления.
    - tags: теги, относящиеся к записи.
    - mood: настроение автора записи (опционально).
    - is_private: флаг приватности записи.
    - slug: уникальный URL-идентификатор записи.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entries",
        verbose_name="Пользователь",
        help_text="Владелец записи дневника",
    )

    title = models.CharField(
        max_length=255, verbose_name="Заголовок", help_text="Введите заголовок записи"
    )

    content = models.TextField(
        verbose_name="Содержание записи", help_text="Введите содержимое записи дневника"
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания записи"
    )

    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата последнего обновления"
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        verbose_name="Теги",
        help_text="Выберите или добавьте теги для записи",
    )

    mood = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Настроение",
        help_text="Опишите настроение (необязательно)",
    )

    is_private = models.BooleanField(
        default=False,
        verbose_name="Приватная запись",
        help_text="Если отмечено, запись видна только вам",
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name="Slug",
        help_text="URL-идентификатор записи, генерируется автоматически",
    )

    def save(self, *args, **kwargs):
        """Переопределенный метод сохранения для генерации уникального slug
        на основе заголовка записи."""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while DiaryEntry.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        """Возвращает заголовок записи для удобного отображения."""
        return self.title

    class Meta:
        verbose_name = "Запись дневника"
        verbose_name_plural = "Записи дневника"
        ordering = ["-created_at"]


class EventCalendar(calendar.HTMLCalendar):
    """
    Генерирует HTML-календарь событий с русскими днями недели и месяцем.

    Расширяет стандартный календарь Python для вывода заголовков и шапки на русском языке.
    Используется для визуализации записей дневника и других событий.

    Атрибуты:
        RU_WEEKDAYS (list[str]): Список коротких названий дней недели на русском (Пн - Вс).
        RU_MONTHS (list[str]): Список названий месяцев на русском (Январь - Декабрь, индекс 1 - январь).
    """

    RU_WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    RU_MONTHS = [
        "",
        "Январь",
        "Февраль",
        "Март",
        "Апрель",
        "Май",
        "Июнь",
        "Июль",
        "Август",
        "Сентябрь",
        "Октябрь",
        "Ноябрь",
        "Декабрь",
    ]

    def formatmonthname(self, theyear, themonth, withyear=True):
        """Выводит HTML-заголовок месяца."""
        month_name = self.RU_MONTHS[themonth]
        if withyear:
            s = f"{month_name} {theyear}"
        else:
            s = f"{month_name}"
        return f"<tr><th colspan='7' class='month'>{s}</th></tr>"

    def formatweekday(self, day):
        """Шапка для одного дня недели."""
        return f"<th class='{self.cssclasses[day]}'>{self.RU_WEEKDAYS[day]}</th>"

    def __init__(self, events, year=None, month=None):
        super().__init__()
        self.events = self.group_by_day(events)
        self.year = year
        self.month = month

    def group_by_day(self, events):
        """
        Группирует переданные события по дням месяца.

        Возвращает словарь, где ключ — день месяца, значение — список событий.
        """
        events_per_day = {}
        for event in events:
            day = event.created_at.day
            events_per_day.setdefault(day, []).append(event)
        return events_per_day

    def formatmonth(self, theyear, themonth, withyear=True):
        """Сохраняем год и месяц в объекте, чтобы использовать в formatday."""
        self.year = theyear
        self.month = themonth
        return super().formatmonth(theyear, themonth, withyear)

    def formatday(self, day, weekday):
        """
        Форматирует HTML-ячейку календаря для конкретного дня.

        - Подсвечивает текущий день.
        - Добавляет эмодзи настроения рядом с номером дня (по первому событию).
        - Дни кликабельны: переходят на список записей за этот день.
        """
        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # пустые ячейки

        cssclass = self.cssclasses[weekday]
        today = datetime.today().day

        if (
            day == today
            and self.month == datetime.today().month
            and self.year == datetime.today().year
        ):
            cssclass += " today"

        # дата этого дня
        current_date = date(self.year, self.month, day)

        # URL на список записей с фильтром по дате
        day_url = reverse("diary:entry_list") + f"?date={current_date.isoformat()}"

        # номер дня как ссылка
        day_html = f'<a href="{day_url}"><span class="day">{day}</span></a>'

        # если есть события — ставим emoji по настроению первого события
        if day in self.events and self.events[day]:
            first_event = self.events[day][0]
            mood_style = get_mood_style(getattr(first_event, "mood", None))
            if mood_style.get("emoji"):
                day_html += f" <span>{mood_style['emoji']}</span>"

        body = day_html

        if day in self.events:
            cssclass += " eventday"
            body += "<ul style='list-style:none;padding-left:0;'>"
            for event in self.events[day]:
                mood_style = get_mood_style(event.mood)
                tags = ", ".join(t.name for t in event.tags.all())
                body += (
                    f"<li>"
                    f"<span style='font-size:1.2em;'>{mood_style['emoji']}</span> "
                    f"{event.title} "
                    f"<span style='color: {mood_style['color']};'>({event.mood})</span>"
                    f"{' — <small>' + tags + '</small>' if tags else ''}"
                    f"</li>"
                )
            body += "</ul>"
            return f'<td class="{cssclass}">{body}</td>'

        return f'<td class="{cssclass}">{body}</td>'


class Attachment(models.Model):
    """
    Модель для хранения прикрепленных файлов к записям дневника.

    Поля:
    - diary_entry: связь с записью дневника.
    - file: загруженный файл.
    - uploaded_at: дата загрузки файла.
    """

    diary_entry = models.ForeignKey(
        DiaryEntry,
        related_name="attachments",
        on_delete=models.CASCADE,
        verbose_name="Запись дневника",
    )
    file = models.FileField(
        upload_to="attachments/",
        verbose_name="Файл",
        help_text="Загрузите файл (макс. 5MB, jpg/png/pdf)",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    def __str__(self):
        """Возвращает имя файла для удобного отображения."""
        return self.file.name


class Affirmation(models.Model):
    text = models.CharField(max_length=255, verbose_name="Текст аффирмации")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Показывать в ротации")

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Аффирмация"
        verbose_name_plural = "Аффирмации"
