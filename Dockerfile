# Use official Python 3.11 slim image
FROM python:3.11-slim

# Environment variables with default PORT (overridden at runtime by .env)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set working directory
WORKDIR /app

# Install system dependencies needed for compiling python packages (e.g., psycopg2, Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and copy requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app/

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Expose port dynamically read from ENV PORT
EXPOSE ${PORT}

# Entrypoint script starts migrations, static collection, and Gunicorn on PORT from .env
ENTRYPOINT ["/app/entrypoint.sh"]

