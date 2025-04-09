FROM python:3.8.11-alpine3.13
MAINTAINER Anderson Contreira <anderson.contreira@madeiramadeira.com.br>

ARG FLASK_PORT=5000
ARG ENVIRONMENT_NAME=development
ENV FLASK_ENV=$ENVIRONMENT_NAME \
    FLASK_APP=app.py \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# SQLite support
RUN apk update && apk add --no-cache \
    sqlite \
    socat \
    build-base \
    python3-dev \
    libffi-dev \
    musl-dev \
    openldap \
    libcurl \
    gpgme-dev \
    libc-dev \
    bash \
    curl \
    zip \
    freetype-dev \
    libpng-dev \
    openblas-dev \
    && rm -rf /var/cache/apk/*

# Upgrade pip e instala awscli
RUN pip install --upgrade pip \
    && pip install --no-cache-dir awscli

COPY requirements.txt requirements-vendor.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-vendor.txt

# Flask compatibility with Python 3.8
RUN pip uninstall -y dataclasses || true
RUN rm -Rf ./vendor/dataclasses-0.8.dist-info/ ./vendor/dataclasses.py

COPY . .

RUN chmod +x ./docker/python/entrypoint.sh

EXPOSE ${FLASK_PORT}

ENTRYPOINT ["sh", "./docker/python/entrypoint.sh"]
