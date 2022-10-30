import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appbank.settings')

app = Celery('appbank')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'call_make_interest_every_1_minute': {
        'task': 'bank.tasks.call_make_interest',
        'schedule': crontab(minute='*/1')
    },
    'call_credit_payment_every_1_minute': {
        'task': 'bank.tasks.call_credit_payment',
        'schedule': crontab(minute='*/1')
    }
}