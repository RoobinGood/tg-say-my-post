FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev

COPY src/ ./src/
RUN mkdir -p prompts config

ENV PYTHONPATH=/app
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "src.cli.run_bot"]
