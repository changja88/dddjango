# 미니 설계 명세 — orders BC 시계 어댑터 패키지 · `__init__.py` 에 타입 붙은 별칭만(스텁 픽스처 P4′b — 진짜 위반)

P4′ 와 같고 별칭에 타입을 붙인다(`alias DefaultClock: type[SystemClockAdapter] = SystemClockAdapter`) — #493 을 빼고 #640 만 보이게.

## 파일 계획

<!-- machine: file-plan -->
```paths
add	application/orders/driven_layer/adapter/clock/system_adapter/__init__.py	# 재수출 + 타입 붙은 별칭
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
application/orders/driven_layer/adapter/clock/system_adapter/__init__.py::alias DefaultClock: type[SystemClockAdapter] = SystemClockAdapter
```

## 경계 import

<!-- machine: boundary-imports -->
```imports
application/orders/driven_layer/adapter/clock/system_adapter/__init__.py	from .adapter.system_clock_adapter import SystemClockAdapter as SystemClockAdapter
application/orders/driven_layer/adapter/clock/system_adapter/adapter/system_clock_adapter.py	from application.orders.application_layer.port.clock.clock_port import ClockPort
```
