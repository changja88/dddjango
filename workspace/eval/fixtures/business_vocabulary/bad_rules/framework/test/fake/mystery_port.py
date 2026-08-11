from __future__ import annotations

import requests


class MysteryFake:
    def call(self) -> None:
        with open("/tmp/x") as fh:
            return None
