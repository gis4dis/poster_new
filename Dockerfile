FROM python:3.6-stretch
ENV PYTHONUNBUFFERED 1

RUN mkdir /static

RUN mkdir /code
WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/