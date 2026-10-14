# 미니 설계 — 사실 발행 길 예보(F4-93 · #541 green)

브로커를 import 하는 유스케이스는 모두 저장 경계를 받는다: `place_order`(add · symbols `__init__` 의 `OrdersUnitOfWork` ·
effects `uow=OrdersUnitOfWork`) · `rename_order`(update · 기준선 실물 `__init__` 의 저장 경계). 저장 경계가 없는
`count_orders`(add · effects `uow=none`)는 브로커를 import 하지 않으므로 대상이 아니다.

<!-- machine: file-plan -->
```paths
add	application/orders/application_layer/order/place_order/place_order_use_case.py
add	application/orders/application_layer/order/place_order/place_order_command.py
add	application/orders/application_layer/order/place_order/place_order_query.py
add	application/orders/application_layer/order/place_order/place_order_result.py
add	application/orders/application_layer/order/count_orders/count_orders_use_case.py
add	application/orders/application_layer/order/count_orders/count_orders_command.py
add	application/orders/application_layer/order/count_orders/count_orders_query.py
add	application/orders/application_layer/order/count_orders/count_orders_result.py
update	application/orders/application_layer/order/rename_order/rename_order_use_case.py
```

<!-- machine: symbols -->
```symbols
application/orders/application_layer/order/place_order/place_order_use_case.py::PlaceOrderUseCase
application/orders/application_layer/order/place_order/place_order_use_case.py::PlaceOrderUseCase.__init__(self, *, unit_of_work: OrdersUnitOfWork, order_repository: OrderRepository, broker: InternalBrokerPort) -> None
application/orders/application_layer/order/place_order/place_order_use_case.py::PlaceOrderUseCase.execute(self, command: PlaceOrderCommand) -> PlaceOrderResult
application/orders/application_layer/order/place_order/place_order_command.py::PlaceOrderCommand {order_id: int, note: str}
application/orders/application_layer/order/place_order/place_order_command.py::PlaceOrderCommand @dataclass(frozen=True)
application/orders/application_layer/order/place_order/place_order_result.py::PlaceOrderResult {order_id: int}
application/orders/application_layer/order/place_order/place_order_result.py::PlaceOrderResult @dataclass(frozen=True)
application/orders/application_layer/order/count_orders/count_orders_use_case.py::CountOrdersUseCase
application/orders/application_layer/order/count_orders/count_orders_use_case.py::CountOrdersUseCase.__init__(self, *, order_repository: OrderRepository) -> None
application/orders/application_layer/order/count_orders/count_orders_use_case.py::CountOrdersUseCase.execute(self, query: CountOrdersQuery) -> CountOrdersResult
application/orders/application_layer/order/count_orders/count_orders_query.py::CountOrdersQuery {order_id: int}
application/orders/application_layer/order/count_orders/count_orders_query.py::CountOrdersQuery @dataclass(frozen=True)
application/orders/application_layer/order/count_orders/count_orders_result.py::CountOrdersResult {count: int}
application/orders/application_layer/order/count_orders/count_orders_result.py::CountOrdersResult @dataclass(frozen=True)
```

<!-- machine: boundary-imports -->
```imports
application/orders/application_layer/order/place_order/place_order_use_case.py	from framework.broker.internal.internal_broker_port import InternalBrokerPort
application/orders/application_layer/order/place_order/place_order_use_case.py	from application.orders.application_layer.port.unit_of_work.orders_unit_of_work import OrdersUnitOfWork
application/orders/application_layer/order/place_order/place_order_use_case.py	from application.orders.domain_layer.order.order_repository import OrderRepository
application/orders/application_layer/order/place_order/place_order_use_case.py	from application.orders.application_layer.order.place_order.place_order_command import PlaceOrderCommand
application/orders/application_layer/order/place_order/place_order_use_case.py	from application.orders.application_layer.order.place_order.place_order_result import PlaceOrderResult
application/orders/application_layer/order/place_order/place_order_command.py	from dataclasses import dataclass
application/orders/application_layer/order/place_order/place_order_result.py	from dataclasses import dataclass
application/orders/application_layer/order/count_orders/count_orders_use_case.py	from application.orders.domain_layer.order.order_repository import OrderRepository
application/orders/application_layer/order/count_orders/count_orders_use_case.py	from application.orders.application_layer.order.count_orders.count_orders_query import CountOrdersQuery
application/orders/application_layer/order/count_orders/count_orders_use_case.py	from application.orders.application_layer.order.count_orders.count_orders_result import CountOrdersResult
application/orders/application_layer/order/count_orders/count_orders_query.py	from dataclasses import dataclass
application/orders/application_layer/order/count_orders/count_orders_result.py	from dataclasses import dataclass
application/orders/application_layer/order/rename_order/rename_order_use_case.py	from framework.broker.external.external_broker_port import ExternalBrokerPort
```

<!-- machine: exception-map -->
```exceptions
```

<!-- machine: use-case-effects -->
```effects
application/orders/application_layer/order/place_order/place_order_use_case.py::PlaceOrderUseCase write uow=OrdersUnitOfWork
application/orders/application_layer/order/count_orders/count_orders_use_case.py::CountOrdersUseCase read-only uow=none
```
