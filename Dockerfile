FROM python:3.11-slim

# Performance Optimization - Prevent Python from writing .pyc (bytecode) files
ENV PYTHONDONTWRITEBYTECODE=1
# Performance Optimization - Ensure logs are flushed immediately to speed up observability.
# Flushing forces temporarily stored log data from memory (buffer/RAM) to permanent storage (disk)
# or clearing/deleting old log data to free up database space.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/app ./app

# Expose FastAPI port
EXPOSE 8000

# Single, explicit entrypoint
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
