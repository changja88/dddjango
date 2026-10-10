"""application.orders.composition_root.wiring_material"""  # 기대: #653 R-docstring-path — import_module(__doc__) 의 경로 docstring
from importlib import import_module

material = import_module(__doc__)
value = material.default_language()
