from django.contrib.auth import get_user_model


def staff_model() -> object:
    return get_user_model()
