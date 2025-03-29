import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "e_commerce_api.settings")

app = Celery("e_commerce_api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()  # Finds tasks inside `tasks.py`
