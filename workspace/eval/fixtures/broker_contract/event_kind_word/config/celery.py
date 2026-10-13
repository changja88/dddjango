from __future__ import annotations

from celery import Celery

app = Celery("config")
app.autodiscover_tasks(packages=app.finder, related_name=None)
