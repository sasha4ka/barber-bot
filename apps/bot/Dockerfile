FROM ghcr.io/astral-sh/uv:latest AS uv_bin
FROM python:3.14-alpine

WORKDIR /app

COPY --from=uv_bin /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache gcc musl-dev libffi-dev

COPY libs/core_shared/ /app/libs/core_shared/

COPY pyproject.toml /app/pyproject.toml

COPY apps/bot/ /app/apps/bot/

RUN uv pip install --system --no-cache -e /app/libs/core_shared -e /app/apps/bot

RUN apk del gcc musl-dev

EXPOSE 8000

CMD ["python", "-m", "bot.main", "run-bot"]