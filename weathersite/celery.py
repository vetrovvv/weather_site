import os
from celery import Celery
from celery.schedules import crontab
import datetime


os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'weathersite.settings')

app = Celery('weathersite')
app.config_from_object('django.conf:settings', namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'every': {
        'task': 'weather.tasks.update_weather',
        "schedule": datetime.timedelta(hours=1),
    },

}
