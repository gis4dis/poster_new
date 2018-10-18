#!/bin/bash

docker-compose run --rm poster-web python manage.py "$@"
