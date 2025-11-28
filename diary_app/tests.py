from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Attachment, DiaryEntry, EventCalendar, Tag

User = get_user_model()


class TagModelTests(TestCase):
    """Тесты модели Tag."""

    def test_create_tag_and_str(self):
        """Проверяет создание тега и корректность метода __str__."""
        tag = Tag.objects.create(name="Important")
        self.assertEqual(tag.name, "Important")
        self.assertEqual(str(tag), "Important")
        self.assertEqual(tag._meta.verbose_name, "Тег")
        self.assertEqual(tag._meta.ordering, ["name"])


class DiaryEntryModelTests(TestCase):
    """Тесты модели DiaryEntry."""

    def test_create_entry_and_slug(self):
        """Проверяет создание записи и уникальную генерацию slug."""
        user = User.objects.create_user(email="user@example.com", password="pass")
        entry = DiaryEntry.objects.create(
            user=user, title="Unique Title", content="test"
        )
        self.assertEqual(entry.title, "Unique Title")
        self.assertEqual(str(entry), "Unique Title")
        self.assertEqual(entry.slug, "unique-title")
        entry2 = DiaryEntry.objects.create(
            user=user, title="Unique Title", content="test2"
        )
        self.assertTrue(entry2.slug.startswith("unique-title-"))
        self.assertEqual(entry._meta.verbose_name, "Запись дневника")
        self.assertEqual(entry._meta.ordering, ["-created_at"])


class AttachmentModelTests(TestCase):
    """Тесты модели Attachment."""

    def test_create_attachment_and_str(self):
        """Проверяет создание вложения и корректность метода __str__."""
        user = User.objects.create_user(email="user@example.com", password="pass")
        entry = DiaryEntry.objects.create(user=user, title="Title", content="Content")
        fake_file = "path/to/file.pdf"
        attachment = Attachment.objects.create(diary_entry=entry, file=fake_file)
        self.assertEqual(attachment.diary_entry, entry)
        self.assertEqual(str(attachment), fake_file)


class EventCalendarTests(TestCase):
    """Тесты класса EventCalendar."""

    class DummyEvent:
        def __init__(self, day, title):
            self.created_at = datetime(2025, 11, day)
            self.title = title

    def test_formatday(self):
        """Проверяет форматирование HTML для дня с и без событий."""
        now = datetime.now()
        events = [self.DummyEvent(now.day, "Test Event")]
        cal = EventCalendar(now.year, now.month, events)  # все параметры сразу

        # День 0 (пустой)
        self.assertIn("noday", cal.formatday(0, 0))
        # День с событием
        html = cal.formatday(now.day, 1)
        self.assertIn("eventday", html)
        self.assertIn("Test Event", html)

    def test_group_by_day(self):
        """Проверяет правильную группировку событий по дням."""
        events = [
            self.DummyEvent(1, "Event1"),
            self.DummyEvent(1, "Event2"),
            self.DummyEvent(2, "Event3"),
        ]
        cal = EventCalendar(2025, 11, events)  # фиксированный месяц для теста
        self.assertIn(1, cal.events_by_day)  # или cal.grouped_events
        self.assertIn(2, cal.events_by_day)
        self.assertEqual(len(cal.events_by_day[1]), 2)


class DiaryEntryListViewTests(TestCase):
    """Тесты для DiaryEntryListView."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="user@example.com", password="pass")
        cls.tag = Tag.objects.create(name="tag1")
        cls.entry1 = DiaryEntry.objects.create(
            user=cls.user, title="Test One", content="Foo"
        )
        cls.entry1.tags.add(cls.tag)
        cls.entry2 = DiaryEntry.objects.create(
            user=cls.user, title="Test Two", content="Bar"
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_list_view_status_code_and_context(self):
        """Проверка, что список записей возвращается и содержит форму поиска."""
        url = reverse("diary:entry_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("search_form", response.context)
        self.assertIn(self.entry1, response.context["entries"])
        self.assertIn(self.entry2, response.context["entries"])

    def test_search_filtering_by_tag(self):
        """Проверка фильтрации по тегу."""
        url = reverse("diary:entry_list") + "?query=tag1"
        response = self.client.get(url)
        self.assertIn(self.entry1, response.context["entries"])
        self.assertNotIn(self.entry2, response.context["entries"])

    def test_search_filtering_by_title(self):
        """Проверка фильтрации по заголовку."""
        url = reverse("diary:entry_list") + "?query=Test Two"
        response = self.client.get(url)
        self.assertIn(self.entry2, response.context["entries"])
        self.assertNotIn(self.entry1, response.context["entries"])


class DiaryEntryDetailViewTests(TestCase):
    """Тесты для DiaryEntryDetailView."""

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            email="user1@example.com", password="pass1"
        )
        cls.user2 = User.objects.create_user(
            email="user2@example.com", password="pass2"
        )
        cls.entry = DiaryEntry.objects.create(
            user=cls.user1, title="Title", content="Content"
        )

    def setUp(self):
        self.client = Client()

    def test_owner_can_access(self):
        """Проверка, что владелец записи может ее видеть."""
        self.client.force_login(self.user1)
        url = reverse("diary:entry_detail", args=[self.entry.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_other_user_cannot_access(self):
        """Проверка, что другой пользователь не может просмотреть запись."""
        self.client.force_login(self.user2)
        url = reverse("diary:entry_detail", args=[self.entry.pk])
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 403])


class DiaryEntryCreateViewTests(TestCase):
    """Тесты для DiaryEntryCreateView."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="user@example.com", password="pass")

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_create_entry(self):
        """Проверка создания новой записи дневника."""
        url = reverse("diary:entry_create")
        data = {
            "title": "New Title",
            "content": "New Content",
            "tags": [],
            "mood": "радость",
            "is_private": False,
        }
        response = self.client.post(url, data)
        print(response.status_code, response.context and response.context.get("form"))

        self.assertIn(
            response.status_code, [302, 303]
        )  # Редирект после успешного создания
        self.assertTrue(
            DiaryEntry.objects.filter(user=self.user, title="New Title").exists()
        )
