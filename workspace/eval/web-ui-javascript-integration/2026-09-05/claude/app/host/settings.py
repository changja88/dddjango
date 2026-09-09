from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "isolated-evaluation-only"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]
INSTALLED_APPS = ["django.contrib.staticfiles", "web.apps.WebConfig"]
ROOT_URLCONF = "host.urls"
MIDDLEWARE = []
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "web"], "APP_DIRS": True, "OPTIONS": {"context_processors": []}}]
STATIC_URL = "/static/"
STATICFILES_DIRS = [("web", BASE_DIR / "web/static"), ("design_system", BASE_DIR / "web/design_system")]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
