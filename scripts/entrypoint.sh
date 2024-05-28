#!/bin/bash -e

# activate virtual env
. /var/lib/tinymotion_env/bin/activate

# test that token is set
if [ ! -z "${INFISICAL_TOKEN}" ]; then
    echo "Error: must set INFISICAL_TOKEN"
    exit 1
fi

# infisical command
PRECMD="infisical run --projectID ${INFISICAL_PROJECT_ID} --env ${INFISICAL_ENV} -- "

# run the database migrations
echo "Running database migrations..."
cd /var/lib/tinymotion_migrations
${PRECMD}alembic upgrade head

# start gunicorn web server
echo "Launching gunicorn..."
cd /var/lib/tinymotion_backend
${PRECMD}gunicorn \
    --timeout 240 \
    --workers 4 \
    --worker-class tinymotion_backend.custom_uvicorn_worker.CustomUvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile="-" \
    tinymotion_backend.main:app
