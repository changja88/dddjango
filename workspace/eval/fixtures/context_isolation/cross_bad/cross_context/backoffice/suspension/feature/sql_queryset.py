def rows(queryset: object) -> object:
    return queryset.raw("SELECT 1"), queryset.extra(where=["1 = 1"])
