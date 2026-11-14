LOCAL_APPS: list[str] = ["cross_context.backoffice.apps.BackofficeConfig"]
INSTALLED_APPS: list[str] = ["django.contrib.admin", "application.orders.driven_layer.django_orders"] + LOCAL_APPS
LOGGING: dict[str, object] = {"version": 1, "loggers": {"cross_context.backoffice": {"level": "INFO"}}}
