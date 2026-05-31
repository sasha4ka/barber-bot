FROM ghcr.io/astral-sh/uv:latest AS uv_bin
FROM python:3.14-alpine

WORKDIR /app

COPY --from=uv_bin /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache gcc musl-dev libffi-dev

COPY pyproject.toml /app/pyproject.toml

COPY libs/core_shared/ /app/libs/core_shared/

RUN uv pip install --system --no-cache -e /app/libs/core_shared

RUN apk del gcc musl-dev

WORKDIR /app/libs/core_shared

CMD ["alembic", "upgrade", "head"]