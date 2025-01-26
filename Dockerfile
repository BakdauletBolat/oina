# -----------------------
# Шаг 1: Сборка (builder)
# -----------------------
FROM python:3.11-slim-bullseye AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .


RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


COPY . /app

# -----------------------
# Шаг 2: Финальный образ
# -----------------------
FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Создадим нового пользователя (не root) для лучшей безопасности
RUN addgroup --system django && adduser --system --ingroup django django

WORKDIR /app

# Скопируем из builder только установленные зависимости
COPY --from=builder /install /usr/local

# Скопируем сам код приложения
COPY . /app

# Переключаемся на пользователя django
USER django

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "oina.wsgi:application"]
