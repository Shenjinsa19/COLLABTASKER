import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collabtasker.settings')

app = Celery('collabtasker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'

app.conf.broker_transport_options = {
    "visibility_timeout": 3600,
    "ssl_cert_reqs": None  # Ignore cert validation errors for Upstash
}