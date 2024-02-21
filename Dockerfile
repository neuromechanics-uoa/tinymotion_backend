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
    && rm -rf /var/lib/apt/lists/* \
    && python3.11 -m ensurepip

COPY . /opt/tinymotion_backend
COPY .git/ /opt/tinymotion_backend/.git/
COPY .gitignore /opt/tinymotion_backend/.gitignore
COPY .dockerignore /opt/tinymotion_backend/.dockerignore
COPY .flake8 /opt/tinymotion_backend/.flake8
RUN python3.11 -m pip --no-cache-dir install /opt/tinymotion_backend \
        && rm -rf /opt/tinymotion_backend

WORKDIR /var/lib/tinymotion_backend
CMD gunicorn \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --access-logfile="-" \
        tinymotion_backend.main:app
