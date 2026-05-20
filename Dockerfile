# ==========================================
# Этап 1: Сборщик (Builder)
# ==========================================
FROM python:3.14-slim AS builder

# Отключаем создание файлов .pyc и включаем буферизацию логов
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Добавляем Poetry в PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Устанавливаем системные зависимости, необходимые для сборки некоторых пакетов (например, psycopg2)
RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry строго определенной версии
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости. 
# Флаг --no-root указывает не устанавливать текущий проект как пакет.
# Флаг --without dev отсекает инструменты разработки (тесты, линтеры).
RUN poetry install --without dev --no-root


# ==========================================
# Этап 2: Финальный образ (Runner)
# ==========================================
FROM python:3.14-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Копируем из этапа builder созданное виртуальное окружение (.venv)
COPY --from=builder /app/.venv /app/.venv

# Активируем виртуальное окружение: добавляем его бинарники в начало PATH.
# Теперь любая команда (python, uvicorn, taskiq) будет брать пакеты из .venv
ENV PATH="/app/.venv/bin:$PATH"

# Копируем исходный код твоего приложения
COPY . .

# Открываем порт для FastAPI
EXPOSE 8000

# Команда по умолчанию (в docker-compose мы её переопределим для воркера)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]