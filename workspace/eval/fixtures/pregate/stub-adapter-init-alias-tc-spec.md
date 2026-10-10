# 미니 설계 명세 — orders BC 시계 어댑터 패키지 · `__init__.py` 에 TYPE_CHECKING 별칭 쌍만(스텁 픽스처 P4′c — 진짜 위반)

P3 과 같고 `__init__.py` 에 `alias[TYPE_CHECKING]` · `alias[else]` 별칭 쌍 하나를 더한다(+ `from typing import TYPE_CHECKING`).

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/orders/driven_layer/adapter/clock/system_adapter/__init__.py	# 재수출 + TYPE_CHECKING 별칭 쌍
add	application/orders/driven_layer/adapter/clock/system_adapter/adapter/system_clock_adapter.py	# 구현
empty	application/orders/driven_layer/adapter/clock/system_adapter/adapter/__init__.py
empty	application/orders/driven_layer/adapter/clock/system_adapter/command/__init__.py
empty	application/orders/driven_layer/adapter/clock/system_adapter/constant/__init__.py
empty	application/orders/driven_layer/adapter/clock/system_adapter/contract/__init__.py
empty	application/orders/driven_layer/adapter/clock/system_adapter/schema/__init__.py
```

## 공개 심볼

<!-- machine: symbols -->
```symbols
application/orders/driven_layer/adapter/clock/system_adapter/adapter/system_clock_adapter.py::SystemClockAdapter(ClockPort)
application/orders/driven_layer/adapter/clock/system_adapter/__init__.py::alias[TYPE_CHECKING] DefaultClock: type[SystemClockAdapter] = SystemClockAdapter
application/orders/driven_layer/adapter/clock/system_adapter/__init__.py::alias[else] DefaultClock: type[SystemClockAdapter] = SystemClockAdapter
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
application/orders/driven_layer/adapter/clock/system_adapter/__init__.py	from typing import TYPE_CHECKING
application/orders/driven_layer/adapter/clock/system_adapter/__init__.py	from .adapter.system_clock_adapter import SystemClockAdapter as SystemClockAdapter
application/orders/driven_layer/adapter/clock/system_adapter/adapter/system_clock_adapter.py	from application.orders.application_layer.port.clock.clock_port import ClockPort
```
