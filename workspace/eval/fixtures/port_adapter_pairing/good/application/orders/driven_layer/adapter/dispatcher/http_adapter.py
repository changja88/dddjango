"""#555 측정 정밀화 경계 — 포트 exception.py(파일형) 선언 오류의 관찰 후 bare 재던짐은 인정."""
from __future__ import annotations

from application.orders.application_layer.port.dispatcher.dispatcher_port import DispatcherPort
from application.orders.application_layer.port.dispatcher.exception import DispatchDeliveryError


class HttpDispatcherAdapter(DispatcherPort):
    def send_notice(self, payload: str) -> None:
        try:
            self._send(payload)
        except DispatchDeliveryError:
            self._record_failure(payload)
            raise

    def _send(self, payload: str) -> None:
        return None

    def _record_failure(self, payload: str) -> None:
        return None
