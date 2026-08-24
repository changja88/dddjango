"""#365 부칙 경계(음성) — 동적 import(importlib)는 통신 축: 후보 강등 불가·red 유지."""
from __future__ import annotations

import importlib


class LoanhubQuoteAdapter:
    def quote(self, order_id: str) -> None:
        net = importlib.import_module("urllib.request")
        net.urlopen("https://loanhub.example/quote")
