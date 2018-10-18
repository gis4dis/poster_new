FROM python:3.6-stretch
ENV PYTHONUNBUFFERED 1
ENV PIP_SRC /opt/site-packages

RUN mkdir /code
WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgdal-dev \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip==18.0
RUN pip install pipenv
# https://github.com/pypa/pipenv/issues/2924#issuecomment-427351356
# RUN pipenv run pip install pip==18.0

ADD Pipfile /code/
ADD Pipfile.lock /code/
ADD . /code/


RUN pipenv install --system

ENV PYTHONPATH "${PYTHONPATH}:/code/src"
