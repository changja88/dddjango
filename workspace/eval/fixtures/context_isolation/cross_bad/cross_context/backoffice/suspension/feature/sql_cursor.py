from django.db import connection


def open_rows() -> object:
    with connection.cursor() as cur:
        return cur.execute("SELECT 1")
