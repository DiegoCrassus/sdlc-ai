FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY app ./app

RUN pip install --no-cache-dir \
    pydantic httpx "SQLAlchemy[asyncio]" aiosqlite redis beautifulsoup4 \
    fastapi uvicorn python-dotenv pytest pytest-asyncio

ENV PYTHONPATH=/app
ENV MARKET_DATA_MODE=live

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.backend.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
