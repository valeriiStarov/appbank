FROM python:3

WORKDIR /appbank

ENV PYTHONUNBUFFERED 1

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY ./appbank /appbank