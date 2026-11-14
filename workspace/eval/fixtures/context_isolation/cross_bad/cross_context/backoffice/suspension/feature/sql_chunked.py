from django.db import connection as conn


def open_rows() -> object:
    with conn.chunked_cursor() as cur:
        return cur.execute("SELECT 1")
