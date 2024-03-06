FROM ubuntu:22.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        build-essential \
        software-properties-common \
    && DEBIAN_FRONTEND=noninteractive add-apt-repository -y ppa:deadsnakes/ppa \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        git \
        python3.11 \
        python3.11-venv \
    && rm -rf /var/lib/apt/lists/*

COPY . /opt/tinymotion_backend
COPY .git/ /opt/tinymotion_backend/.git/
COPY .gitignore /opt/tinymotion_backend/.gitignore
COPY .dockerignore /opt/tinymotion_backend/.dockerignore
COPY .flake8 /opt/tinymotion_backend/.flake8
RUN python3.11 -m venv /var/lib/tinymotion_env \
    && . /var/lib/tinymotion_env/bin/activate \
    && echo ". /var/lib/tinymotion_env/bin/activate" > /etc/profile.d/tinymotion.sh \
    && echo ". /var/lib/tinymotion_env/bin/activate" > /etc/bash.bashrc \
    && python -m pip --no-cache-dir install /opt/tinymotion_backend \
    && mkdir -p /var/lib/tinymotion_migrations \
    && mv /opt/tinymotion_backend/alembic /var/lib/tinymotion_migrations/alembic \
    && mv /opt/tinymotion_backend/alembic.ini /var/lib/tinymotion_migrations/alembic.ini \
    && cp /opt/tinymotion_backend/scripts/entrypoint.sh /entrypoint.sh \
    && chmod +x /entrypoint.sh \
    && cp /opt/tinymotion_backend/scripts/tinymotion-backend /usr/local/bin/tinymotion-backend \
    && chmod +x /usr/local/bin/tinymotion-backend \
    && rm -rf /opt/tinymotion_backend

WORKDIR /var/lib/tinymotion_backend
CMD /entrypoint.sh
