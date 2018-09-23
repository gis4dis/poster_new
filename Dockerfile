FROM python:3.6-stretch
ENV PYTHONUNBUFFERED 1

RUN mkdir /static

RUN mkdir /code
WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgdal-dev \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install pipenv

ADD Pipfile /code/
ADD Pipfile.lock /code/

RUN pipenv install --deploy

ENV PYTHONPATH "${PYTHONPATH}:/code/src"

ADD . /code/