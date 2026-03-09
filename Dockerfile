FROM python:3.12-slim

WORKDIR /app

# System deps for Pillow and FFmpeg (needed later for video)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .

# Media storage directory
RUN mkdir -p /app/media

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
