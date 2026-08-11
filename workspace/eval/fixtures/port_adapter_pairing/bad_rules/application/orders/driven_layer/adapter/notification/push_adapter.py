from __future__ import annotations

import requests


class PushNotificationAdapter:
    def push(self, payload: object) -> None:
        if payload.order_total > 100:
            self._bulk(payload)
        try:
            requests.post("x", json={})
        except Exception:
            raise

    def _bulk(self, payload: object) -> None:
        try:
            requests.post("y", json={})
        except Exception:
            raise RuntimeError("push failed")
