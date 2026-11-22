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
MAINTENANCE_MODE_EXEMPT_PATHS = ["/api/health", "/api/gate/list.csv"]
MAINTENANCE_MODE_EXEMPT_PATTERNS = [
    r"/api/gate/open/.+/status",
    r"/api/gate/p[io]ng",
    r"/api/gate/slot/[^/]+",
    r"/api/gate/number/\d+",   # 템플릿 글 `{number}` 에는 맞지 않는다 — 문서에는 남는다
    r"/api/gate/head",          # 경로의 앞머리만 — 맞지 않는다
    r"/gate/head/tail",         # mount 앞머리가 없다 — 맞지 않는다
]
CROSS_SITE_REQUEST_EXEMPT_PATHS = ["/api/webhook"]
CROSS_SITE_REQUEST_EXEMPT_PATTERNS = [r"/api/gate/hook/.+"]
BROKEN_EXEMPT_PATTERNS = ["/api/gate/(unclosed"]   # 깨진 정규식(표 bad_exempt_pattern)
