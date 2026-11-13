SECRET_KEY = "toy"
DEBUG = False
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = "toyproj.urls"
INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth", "django.contrib.sessions", "ninja_extra"]
MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "framework.django.maintenance_mode_middleware.MaintenanceModeMiddleware",
    "framework.django.cross_site_request_middleware.CrossSiteRequestMiddleware",
    "framework.django.not_acceptable_middleware.NotAcceptableMiddleware",
]
DATABASES = {}
USE_TZ = True
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
NINJA_EXTRA = {"THROTTLE_RATES": {"user": None, "anon": None}}
MAINTENANCE_MODE = False
MAINTENANCE_MODE_EXEMPT_PATHS = ["/api/health"]
CROSS_SITE_REQUEST_EXEMPT_PATHS = ["/api/webhook"]
