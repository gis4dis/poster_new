#!/bin/bash

echo "Sleeping for 30s to allow Postgres to start"
sleep 30
while :
do
    echo "COLLECTING STATIC FILES"
    python3 manage.py collectstatic --no-input
    echo "RUNNING DJANGO DEVEL SERVER IN LOOP"
    python3 manage.py runserver 0.0.0.0:8000
    echo "Sleeping for 5s before restart"
    sleep 5
done