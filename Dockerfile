FROM python:3.12 AS base

RUN apt-get update && \
    apt-get install -y curl zstd && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    curl -fsSL https://ollama.com/install.sh | sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=0.0.0.0:11434

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --without dev

COPY . .

RUN chmod +x /app/entrypoint.sh
EXPOSE 11434

CMD ["/app/entrypoint.sh"]
