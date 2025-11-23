from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .forms import HabitForm, HabitRecordForm
from .models import Habit, HabitRecord

User = get_user_model()


class HabitModelTests(TestCase):
    """Тесты модели Habit."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@example.com", password="password"
        )

    def test_create_habit(self):
        """Проверяет создание объекта Habit с основными полями."""
        habit = Habit.objects.create(
            user=self.user,
            name="Test habit",
            description="Test description",
            is_active=True,
        )
        self.assertEqual(habit.name, "Test habit")
        self.assertEqual(habit.description, "Test description")
        self.assertTrue(habit.is_active)
        self.assertEqual(habit.user, self.user)
        self.assertEqual(str(habit), habit.name)

    def test_ordering_by_created_at(self):
        """Проверяет, что объекты Habit сортируются по created_at по убыванию."""
        Habit.objects.create(
            user=self.user, name="Old habit", created_at=timezone.now()
        )
        Habit.objects.create(
            user=self.user, name="New habit", created_at=timezone.now()
        )
        habits = Habit.objects.all().order_by("-created_at")
        self.assertEqual(list(habits), list(Habit.objects.all()))


class HabitRecordModelTests(TestCase):
    """Тесты модели HabitRecord."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user3@example.com", password="password"
        )
        cls.habit = Habit.objects.create(user=cls.user, name="Habit 1")

    def test_create_habit_record(self):
        """Проверяет создание отметки привычки с флагом done."""
        record = HabitRecord.objects.create(
            habit=self.habit, date=timezone.now().date(), done=True
        )
        self.assertEqual(record.habit, self.habit)
        self.assertTrue(record.done)
        self.assertEqual(str(record), f"{self.habit.name} - {record.date}: ✓")

    def test_unique_together_constraint(self):
        """Проверяет уникальность сочетания habit и date."""
        date = timezone.now().date()
        HabitRecord.objects.create(habit=self.habit, date=date, done=True)
        with self.assertRaises(Exception):
            HabitRecord.objects.create(habit=self.habit, date=date, done=False)


class HabitFormTests(TestCase):
    """Тесты формы HabitForm."""

    def test_valid_data(self):
        """Проверяет валидность формы при корректных данных."""
        data = {
            "name": "New Habit",
            "description": "Description here",
            "is_active": True,
        }
        form = HabitForm(data=data)
        self.assertTrue(form.is_valid())

    def test_missing_name(self):
        """Проверяет, что форма невалидна, если отсутствует обязательное поле name."""
        data = {
            "name": "",
            "description": "Description here",
            "is_active": True,
        }
        form = HabitForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class HabitRecordFormTests(TestCase):
    """Тесты формы HabitRecordForm."""

    def test_valid_data(self):
        """Проверяет валидность формы при корректных данных."""
        data = {"done": True}
        form = HabitRecordForm(data=data)
        self.assertTrue(form.is_valid())

    def test_done_field_behavior(self):
        """
        Проверяет логику валидации поля done в HabitRecordForm.

        Поле done необязательное, поэтому форма валидна и без него.
        """
        data_empty = {}
        form_empty = HabitRecordForm(data=data_empty)
        self.assertTrue(form_empty.is_valid())

        data_true = {"done": True}
        form_true = HabitRecordForm(data=data_true)
        self.assertTrue(form_true.is_valid())

        data_false = {"done": False}
        form_false = HabitRecordForm(data=data_false)
        self.assertTrue(form_false.is_valid())
