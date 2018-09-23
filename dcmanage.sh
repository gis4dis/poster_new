#!/bin/bash

docker-compose run --rm poster-web pipenv run python manage.py "$@"
