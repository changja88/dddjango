import psycopg2


def open_rows() -> object:
    return psycopg2.connect("")
