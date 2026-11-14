from django.db.models import Model as M


class AliasMirror(M):
    status: str = "open"
