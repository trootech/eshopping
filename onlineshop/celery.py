import os
from celery import Celery

# set the default django settings to celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineshop.settings')
app = Celery('onlineshop')
app.config_from_object('django.conf:settings', namespace='CELERY')
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
# message broker configurations
BASE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
app.conf.broker_url = BASE_REDIS_URL
