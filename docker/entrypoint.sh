#!/bin/bash -e

# initialise the virtual environment
. /var/lib/tinymotion_env/bin/activate

# run the database migrations
echo "Running database migrations..."
cd /var/lib/tinymotion_migrations
alembic upgrade head

# start gunicorn web server
echo "Launching gunicorn..."
cd /var/lib/tinymotion_backend
gunicorn \
    --timeout 240 \
    --workers 4 \
    --worker-class tinymotion_backend.custom_uvicorn_worker.CustomUvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile="-" \
    tinymotion_backend.main:app
