web: gunicorn poster.wsgi -k gevent --timeout 120 --log-file - --reload
#web: "python manage.py runserver 0.0.0.0:$PORT"

celery-web: "flower -A poster --address=0.0.0.0 --port=$PORT --basic_auth=$FLOWER_USER:$FLOWER_PASSWD"
celery: celery -A poster worker -l info
celery_beat: celery -A poster beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

jupyter-web: "jupyter nbextension enable --py widgetsnbextension; python manage.py shell_plus --notebook"

release: python manage.py migrate