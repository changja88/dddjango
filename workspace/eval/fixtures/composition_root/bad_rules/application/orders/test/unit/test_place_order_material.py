from unittest import mock


def test_place_order_uses_default_language() -> None:
    with mock.patch("application.orders.composition_root.wiring_material.default_language"):  # 기대: #653 R-test-patch — 시험 파일의 mock.patch 문자열
        pass
