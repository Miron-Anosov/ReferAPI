FROM python:3.12.4-slim-bullseye AS builder
LABEL authors="mairon26rus@gmail.com"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential libpq-dev curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME=/opt/poetry

ENV PATH="$POETRY_HOME/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 - --version 1.8.3

RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-dev


COPY ./src /app/src
COPY gunicorn_conf.py /app/gunicorn_conf.py
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic
COPY start.sh /app/start.sh
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

FROM python:3.12-slim-bullseye
WORKDIR /app/
COPY --from=builder /app /app
COPY --from=builder /usr/local/ /usr/local/
