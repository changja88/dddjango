from application.shipping.composition_root.wiring_material import default_language  # 기대: #653 R-name-import — 이름째 들이기(모듈째 import 아님)


def build_ship_order_use_case() -> str:
    return default_language()
