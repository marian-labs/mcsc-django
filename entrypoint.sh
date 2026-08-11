#!/bin/sh
set -e

# Load .env file if present and PORT is not already set in the environment
if [ -f /app/.env ]; then
  # Export variables from .env if they are not already set
  set -a
  . /app/.env
  set +a
fi

# Fallback PORT, WORKERS, and THREADS if not specified in .env or environment
PORT="${PORT:-8000}"
WORKERS="${WEB_CONCURRENCY:-3}"
THREADS="${GUNICORN_THREADS:-2}"

echo "=================================================="
echo "Starting MCSC Django Application..."
echo "Configured Port: ${PORT}"
echo "Workers: ${WORKERS} | Threads per Worker: ${THREADS}"
echo "=================================================="

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --no-input

# Start Gunicorn server binding to 0.0.0.0:$PORT
echo "Launching Gunicorn server on 0.0.0.0:${PORT}..."
exec gunicorn mcsc.wsgi:application \
    --bind "0.0.0.0:${PORT}" \
    --workers "${WORKERS}" \
    --threads "${THREADS}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

