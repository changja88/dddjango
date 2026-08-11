class ShipOrderCommand: ...


def _guard(value: int) -> None:
    if value < 0:
        raise ValueError("음수 금지")
