web: pipenv run python manage.py migrate && pipenv run gunicorn poster.wsgi -k gevent --log-file - --reload
#web: "python manage.py runserver 0.0.0.0:$PORT"

celery-web: "pipenv run flower -A poster --address=0.0.0.0 --port=$PORT --basic_auth=$FLOWER_USER:$FLOWER_PASSWD"
celery: pipenv run celery -A poster worker -l info
celery_beat: pipenv run celery -A poster beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler