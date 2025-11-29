# Diary & Habit Tracker
## 🚀 Приложение для ведения личного дневника и отслеживания привычек на Django

# О проекте
Технологии: Python 3.12, Django 5.x, API, PostgreSQL, Docker.

Готов к запуску через Docker Compose. Включает API, пользовательскую модель, загрузку файлов.

# 💡 Возможности
API для дневниковых записей и привычек: CRUD, фильтрация, вложенные запросы.

Кастомная модель пользователя (email, аватар, токен).

Аутентификация, ограничения по ролям, админка.

Быстрый старт через Docker Compose

## 🚦 Быстрый запуск через Docker Compose
1. Склонируйте репозиторий:
~~~
git clone https://github.com/natali83911/personal_diary.git
cd personal_diary
~~~

2. Скопируйте переменные окружения:
~~~
cp .env.example .env
~~~

3. Запустите все сервисы:
~~~
docker-compose up --build
~~~

4. Примените миграции:
~~~
docker-compose exec web python manage.py migrate
~~~

5. Создайте суперпользователя:
~~~
docker-compose exec web python manage.py createsuperuser
~~~

6. Откройте:

Django web: http://localhost:8000/

## 🛠 Проверка сервисов
1. Django web: страница логина/дневника должна быть доступна.

Привычки: проверьте создание привычки, статус "done" через интерфейс.

2. PostgreSQL:
~~~
docker-compose exec db psql -U postgres -d personal_diary
SELECT id, email, is_active FROM users_customuser;
~~~
3. Загрузка файлов/аватаров: добавьте файл к записи/аватару — убедитесь, что доступен в профиле.


## ⚡ Структура проекта
~~~
personal_diary/
├── config/           # Основные настройки Django
├── diary_app/        # Модели, API и логика дневника
├── habits_app/       # Модели и логика привычек
├── users/            # Пользовательская модель
├── static/           # Статичные файлы
├── media/            # Загружаемые файлы
├── templates/        # Шаблоны
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── README.md
~~~

## 🧪 Тестирование и проверка кода
Юнит-тесты:
~~~
docker-compose exec web python manage.py test
~~~

Покрытие тестами:
~~~
docker-compose exec web coverage run manage.py test
docker-compose exec web coverage report
~~~

## 📦 Зависимости
Список пакетов в requirements.txt (основные: Django, djangorestframework, postgres, pytest, coverage).

## 📧 Контакты
Вопросы, баги и предложения — в issues репозитория или на email из профиля.