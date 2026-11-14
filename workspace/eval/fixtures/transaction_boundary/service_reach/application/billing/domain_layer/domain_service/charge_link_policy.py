from __future__ import annotations


class ChargeLinkPolicy:
    """다른 BC 의 도메인 서비스."""

    @staticmethod
    def link(order: object, lead: object) -> None:
        order.link_to(0)
