#!/bin/sh

Create migration
alembic upgrade head

# run API server
gunicorn --config /app/gunicorn_conf.py