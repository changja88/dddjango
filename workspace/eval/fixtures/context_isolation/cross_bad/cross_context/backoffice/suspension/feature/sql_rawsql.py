from django.db.models.expressions import RawSQL as R


def expression() -> object:
    return R("SELECT 1", ())
