MIDDLEWARE: list = [
    "django.middleware.security.SecurityMiddleware",
    "application.orders.driving_layer.middleware.OrderContentNegotiationMiddleware",
]

MIDDLEWARE += [
    "application.billing.driving_layer.middleware.BillingJsonMiddleware",
]
