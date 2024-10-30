"""Конфигурация Gunicorn."""

from src.core.settings.env import settings

workers = settings.gunicorn.WORKERS  # noqa

bind = settings.gunicorn.BUILD

loglevel = settings.gunicorn.LOG_LEVEL

wsgi_app = settings.gunicorn.WSGI_APP

worker_class = settings.gunicorn.WORKER_CLASS

timeout = settings.gunicorn.TIMEOUT
accesslog = settings.gunicorn.ACCESSLOG
errorlog = settings.gunicorn.ERRORLOG
