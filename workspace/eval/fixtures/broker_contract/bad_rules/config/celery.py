from __future__ import annotations

from application.orders.driving_layer.cron_job import nightly_settle_cron_job
from celery import Celery

app = Celery("config")
app.autodiscover_tasks(["application.orders.driving_layer.cron_job"])


def debug_task() -> None:
    return None
