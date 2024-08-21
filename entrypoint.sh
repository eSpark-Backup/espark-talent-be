#!/bin/sh

python eSparkTalent/manage.py migrate --no-input
python eSparkTalent/manage.py createsuperuser --no-input
python eSparkTalent/manage.py runserver 0.0.0.0:${DOCKER_APPLICATION_PORT}