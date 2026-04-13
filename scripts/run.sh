#!/bin/sh
set -e

/opt/venv/bin/python manage.py makemigrations --noinput
/opt/venv/bin/python manage.py migrate
/opt/venv/bin/gunicorn --bind 0.0.0.0:8000 config.wsgi:application --workers 2