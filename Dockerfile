# pull the official base image

# for windows containers
# FROM python:3.6.3-windowsservercore-ltsc2016

# for linux containers
FROM python:3

# set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# set work directory
WORKDIR /code

# install dependencies
COPY requirements.txt /code/
RUN pip install -r requirements.txt


# copy project
COPY . /code/

RUN python eSparkTalent/manage.py makemigrations
RUN python eSparkTalent/manage.py migrate

EXPOSE 8000

CMD ["python", "eSparkTalent/manage.py", "runserver", "0.0.0.0:8000"]