#!/bin/sh

python manage.py migrate --no-input
python manage.py createsuperuser --no-input
python manage.py runserver 0.0.0.0:${DOCKER_APPLICATION_PORT}