from __future__ import annotations

from ninja.errors import HttpError


class OrderNotFoundError(HttpError):
    pass
