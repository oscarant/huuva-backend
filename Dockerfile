# Dockerfile
FROM python:3.13-slim

# Prevent Python from writing pyc files and set unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Poetry
RUN pip install --upgrade pip poetry

WORKDIR /app

# Copy dependency files and install (without dev dependencies for production)
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application code
COPY app /app/

# Expose the FastAPI port
EXPOSE 8000

# Run the application with Uvicorn (for dev; production may use Gunicorn+Uvicorn workers)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
