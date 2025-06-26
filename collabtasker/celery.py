import os
from celery import Celery
import ssl
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collabtasker.settings')
CELERY_BROKER_URL = os.getenv('REDIS_URL')
app = Celery('collabtasker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'

app.conf.broker_transport_options = {
    "visibility_timeout": 3600,
    "ssl_cert_reqs": ssl.CERT_NONE, # Ignore cert validation errors for Upstash
}