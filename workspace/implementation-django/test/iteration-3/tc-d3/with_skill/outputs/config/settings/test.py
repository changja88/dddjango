from .base import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "taskflow_test",
        "USER": "taskflow",
        "PASSWORD": "taskflow",
        "HOST": "localhost",
        "PORT": "5432",
    },
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
