#!/bin/sh

python eSparkTalent/manage.py makemigrations --no-input
python eSparkTalent/manage.py migrate --no-input
python eSparkTalent/manage.py create_super_user
python eSparkTalent/manage.py runserver 0.0.0.0:8000
