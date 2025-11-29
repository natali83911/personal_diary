# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем системные зависимости, необходимые для psycopg2, pillow и др.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev libjpeg-dev zlib1g-dev libpng-dev netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Работаем внутри директории проекта
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . .

# Обеспечиваем отключение байт-кода и буферизации
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Открываем порт для Django
EXPOSE 8000

# Для разработки запускать dev-сервер
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

