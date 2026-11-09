from application.orders.driving_layer.cron_job.settle_cron_job import settle_cron_job


def test_settle_cron_job() -> None:
    settle_cron_job()
