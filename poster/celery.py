from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poster.settings')

app = Celery('processing')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@app.task(bind=True)
def debug_logging(self):
    import sys
    import logging
    # Get an instance of a logger
    logger = logging.getLogger(__name__)
    print('Celery debug_task testing message STDOUT', file=sys.stdout)
    print('Celery debug_task testing message STDERR', file=sys.stderr)
    logger.debug('Celery debug_task testing message logger DEBUG')
    logger.info('Celery debug_task testing message logger INFO')
    logger.warning('Celery debug_task testing message logger WARNING')
    logger.error('Celery debug_task testing message logger ERROR')
    logger.fatal('Celery debug_task testing message logger FATAL')
