FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN uv sync

COPY . .

EXPOSE 8080

CMD ["fastapi", "run", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
