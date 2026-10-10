from importlib import import_module

material = import_module(
    b"application.orders.composition_root.wiring_material".decode()  # 기대: #653 R-bytes-path — import_module(b"…".decode())
)
value = material.default_language()
