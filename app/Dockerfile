FROM python:3.9.5-slim-buster

WORKDIR /usr/src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2 \
    && pip install -U jinja2 \

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r app/requirements.txt

COPY . /usr/src/app/