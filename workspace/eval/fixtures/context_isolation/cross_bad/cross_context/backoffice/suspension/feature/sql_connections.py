from django.db import connections


def open_rows() -> object:
    return connections["default"].cursor()
