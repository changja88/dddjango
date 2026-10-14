# 미니 설계 — 사실 발행 길 예보(F4-93 · #541 선언 확정 red)

브로커 포트를 받는 유스케이스 넷 가운데 생성자를 선언하고 저장 경계가 없는 둘이 선언 확정이다: `place_order`(add · effects
`uow=none`) · `close_order`(update · symbols `__init__` · external 브로커). `notify_order`(add · 생성자 서명 없음)와
`archive_order`(update · 클래스 행만 — 산문이 저장 경계를 더한다고 적은 꼴 · 기준선 생성자뿐)는 선언 후보이고,
`rename_order`(update · 기준선 생성자에 저장 경계)는 대상이 아니다.

<!-- machine: file-plan -->
```paths
add	application/orders/application_layer/order/place_order/place_order_use_case.py
add	application/orders/application_layer/order/place_order/place_order_command.py
add	application/orders/application_layer/order/place_order/place_order_query.py
add	application/orders/application_layer/order/place_order/place_order_result.py
add	application/orders/application_layer/order/notify_order/notify_order_use_case.py
add	application/orders/application_layer/order/notify_order/notify_order_command.py
add	application/orders/application_layer/order/notify_order/notify_order_query.py
add	application/orders/application_layer/order/notify_order/notify_order_result.py
update	application/orders/application_layer/order/close_order/close_order_use_case.py
update	application/orders/application_layer/order/archive_order/archive_order_use_case.py
update	application/orders/application_layer/order/rename_order/rename_order_use_case.py
```

<!-- machine: symbols -->
```symbols
application/orders/application_layer/order/place_order/place_order_use_case.py::PlaceOrderUseCase
application/orders/application_layer/order/place_order/place_order_use_case.py::PlaceOrderUseCase.__init__(self, *, order_repository: OrderRepository, broker: InternalBrokerPort) -> None
application/orders/application_layer/order/place_order/place_order_use_case.py::PlaceOrderUseCase.execute(self, command: PlaceOrderCommand) -> PlaceOrderResult
application/orders/application_layer/order/place_order/place_order_command.py::PlaceOrderCommand {order_id: int, note: str}
application/orders/application_layer/order/place_order/place_order_command.py::PlaceOrderCommand @dataclass(frozen=True)
application/orders/application_layer/order/place_order/place_order_result.py::PlaceOrderResult {order_id: int}
application/orders/application_layer/order/place_order/place_order_result.py::PlaceOrderResult @dataclass(frozen=True)
application/orders/application_layer/order/notify_order/notify_order_use_case.py::NotifyOrderUseCase
application/orders/application_layer/order/notify_order/notify_order_use_case.py::NotifyOrderUseCase.execute(self, command: NotifyOrderCommand) -> NotifyOrderResult
application/orders/application_layer/order/notify_order/notify_order_command.py::NotifyOrderCommand {order_id: int}
application/orders/application_layer/order/notify_order/notify_order_command.py::NotifyOrderCommand @dataclass(frozen=True)
application/orders/application_layer/order/notify_order/notify_order_result.py::NotifyOrderResult {order_id: int}
application/orders/application_layer/order/notify_order/notify_order_result.py::NotifyOrderResult @dataclass(frozen=True)
application/orders/application_layer/order/close_order/close_order_use_case.py::CloseOrderUseCase
application/orders/application_layer/order/close_order/close_order_use_case.py::CloseOrderUseCase.__init__(self, *, order_repository: OrderRepository, broker: ExternalBrokerPort) -> None
application/orders/application_layer/order/archive_order/archive_order_use_case.py::ArchiveOrderUseCase
```

<!-- machine: boundary-imports -->
```imports
application/orders/application_layer/order/place_order/place_order_use_case.py	from framework.broker.internal.internal_broker_port import InternalBrokerPort
application/orders/application_layer/order/place_order/place_order_use_case.py	from application.orders.domain_layer.order.order_repository import OrderRepository
application/orders/application_layer/order/place_order/place_order_use_case.py	from application.orders.application_layer.order.place_order.place_order_command import PlaceOrderCommand
application/orders/application_layer/order/place_order/place_order_use_case.py	from application.orders.application_layer.order.place_order.place_order_result import PlaceOrderResult
application/orders/application_layer/order/place_order/place_order_command.py	from dataclasses import dataclass
application/orders/application_layer/order/place_order/place_order_result.py	from dataclasses import dataclass
application/orders/application_layer/order/notify_order/notify_order_use_case.py	from framework.broker.internal.internal_broker_port import InternalBrokerPort
application/orders/application_layer/order/notify_order/notify_order_use_case.py	from application.orders.application_layer.order.notify_order.notify_order_command import NotifyOrderCommand
application/orders/application_layer/order/notify_order/notify_order_use_case.py	from application.orders.application_layer.order.notify_order.notify_order_result import NotifyOrderResult
application/orders/application_layer/order/notify_order/notify_order_command.py	from dataclasses import dataclass
application/orders/application_layer/order/notify_order/notify_order_result.py	from dataclasses import dataclass
application/orders/application_layer/order/close_order/close_order_use_case.py	from framework.broker.external.external_broker_port import ExternalBrokerPort
application/orders/application_layer/order/close_order/close_order_use_case.py	from application.orders.domain_layer.order.order_repository import OrderRepository
application/orders/application_layer/order/archive_order/archive_order_use_case.py	from framework.broker.internal.internal_broker_port import InternalBrokerPort
application/orders/application_layer/order/rename_order/rename_order_use_case.py	from framework.broker.internal.internal_broker_port import InternalBrokerPort
```

<!-- machine: exception-map -->
```exceptions
```

<!-- machine: use-case-effects -->
```effects
application/orders/application_layer/order/place_order/place_order_use_case.py::PlaceOrderUseCase write uow=none
```
