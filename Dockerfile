FROM python:3.10-slim

WORKDIR /app

# Install PostgreSQL client for psycopg2 and pg_isready
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Production command (matches docker-compose)
CMD ["gunicorn", "-w", "8", "-b", "0.0.0.0:5000", "app:create_app()"] 