FROM python:3.13.5-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY "pyproject.toml" "uv.lock" ".python-version" ./
RUN uv sync --locked

COPY petcache/ ./petcache/

# Create directory for database
RUN mkdir -p /app/data

# Expose port
EXPOSE 8909

ENV PETCACHE_DB_PATH=/app/data/petcache.db

CMD ["python", "-m", "petcache", "--host", "0.0.0.0", "--port", "8909", "--db-path", "/app/data/petcache.db"]