from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE','mindplex.settings')
BASE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
app = Celery('mindplex')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'add-every-20-seconds': {
        'task': 'articleRecommender.tasks.relearnerTask',
        'schedule': 5,
    }
}
app.autodiscover_tasks()
app.conf.broker_url = BASE_REDIS_URL
app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'