#!/bin/sh
set -e

# Load .env file if present and PORT is not already set in the environment
if [ -f /app/.env ]; then
  # Export variables from .env if they are not already set
  set -a
  . /app/.env
  set +a
fi

# Fallback PORT if not specified in .env or environment
PORT="${PORT:-8000}"

echo "=================================================="
echo "Starting MCSC Django Application..."
echo "Configured Port: ${PORT}"
echo "=================================================="

# Wait for Database readiness
echo "Checking database connection..."
python - << 'EOF'
import sys
import time
import os
import django
from django.db import connections
from django.db.utils import OperationalError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcsc.settings')
django.setup()

max_retries = 30
for attempt in range(1, max_retries + 1):
    try:
        connection = connections['default']
        connection.cursor()
        print("✓ Database connection established successfully.")
        sys.exit(0)
    except OperationalError as err:
        print(f"Waiting for database to become available... (attempt {attempt}/{max_retries})")
        time.sleep(2)
    except Exception as err:
        print(f"Waiting for database... ({err}) (attempt {attempt}/{max_retries})")
        time.sleep(2)

print("❌ Could not connect to database after maximum retries.")
sys.exit(1)
EOF

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --no-input

# Start Gunicorn server
echo "Launching Gunicorn server on 0.0.0.0:${PORT}..."
exec gunicorn --bind 0.0.0.0:${PORT} --workers 2 --timeout 120 mcsc.wsgi:application
