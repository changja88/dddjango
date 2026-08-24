from __future__ import annotations

import urllib.request


class PayhubBillableAdapter:
    def settle(self, order_id: str) -> None:
        urllib.request.urlopen("https://payhub.example/settle")
