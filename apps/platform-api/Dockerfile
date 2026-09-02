FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml .
COPY apps/platform-api/app ./app
RUN pip install --no-cache-dir fastapi pydantic-settings PyJWT[crypto] httpx prometheus-client sqlalchemy asyncpg alembic uvicorn
USER 10001
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
