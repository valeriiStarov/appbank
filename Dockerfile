FROM python:3.10.8-alpine

WORKDIR /appbank

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apk update \
    && apk add postgresql-dev zlib-dev jpeg-dev gcc python3-dev musl-dev
RUN apk add libc-dev libffi-dev

RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./appbank /appbank

ENTRYPOINT ["/appbank/entrypoint.sh"]