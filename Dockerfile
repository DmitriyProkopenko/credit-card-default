# Базовый образ Python
FROM python:3.12-slim

# Рабочая директория
WORKDIR /app

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Копирование зависимостей и установка
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода и моделей
COPY app/ ./app/
COPY models/ ./models/

# Копируем также файл __init__.py (на случай, если он не попал в COPY app/)
# и документацию для удобства
COPY README.md ./
COPY ARCHITECTURE.md ./
COPY AB_TEST_PLAN.md ./

# Порт, который слушает приложение
EXPOSE 5000

# Запуск через gunicorn (production WSGI сервер)
# app.api:app означает: папка app -> файл api.py -> переменная app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app.api:app"]