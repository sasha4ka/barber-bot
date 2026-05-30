FROM ghcr.io/astral-sh/uv:latest AS uv_bin
FROM python:3.14-alpine

WORKDIR /app

COPY --from=uv_bin /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache gcc musl-dev libffi-dev

COPY libs/core_shared/ /app/libs/core_shared/

COPY pyproject.toml /app/pyproject.toml

COPY apps/api/ /app/apps/api/

RUN uv pip install --system --no-cache -e /app/libs/core_shared -e /app/apps/api

RUN apk del gcc musl-dev

EXPOSE 9000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "9000"]