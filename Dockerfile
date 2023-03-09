FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y gcc && \
    apt-get install -y libpq-dev

RUN pip install --upgrade pip
RUN pip install virtualenv

RUN mkdir /venv
ENV VIRTUAL_ENV=/venv
RUN virtualenv /venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY ./ /app
WORKDIR /app

ENV PYTHONPATH /app/src:/app/tests

RUN pip install poetry==1.1.15
RUN poetry install
