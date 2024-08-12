# pull the official base image

# for windows containers
# FROM python:3.6.3-windowsservercore-ltsc2016

# for linux containers
FROM python:3

# set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# set work directory
WORKDIR /usr/src/app

# install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt


# copy project
COPY . .

RUN python eSparkTalent/manage.py makemigrations
RUN python eSparkTalent/manage.py migrate
RUN python eSparkTalent/manage.py collectstatic
RUN python eSparkTalent/manage.py create_super_user

EXPOSE 8000

CMD ["python", "eSparkTalent/manage.py", "runserver", "0.0.0.0:8000"]