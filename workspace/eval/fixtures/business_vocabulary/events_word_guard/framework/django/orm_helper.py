from __future__ import annotations

from django.db import models


def base_manager(model: models.Model) -> object:
    return model
