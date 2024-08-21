#!/bin/sh

python eSparkTalent/manage.py migrate --no-input
python eSparkTalent/manage.py createsuperuser
python eSparkTalent/manage.py runserver 0.0.0.0:8000