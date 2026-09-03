from application.orders.domain_layer.shared_value_object.plain_base import PlainBase as StrEnum


class Shadow(StrEnum):
    """비선언 클래스를 선언적 이름으로 별칭 — 면제 대상이 아니다(첫 대입 타입 #493)."""

    FIRST = "first"
