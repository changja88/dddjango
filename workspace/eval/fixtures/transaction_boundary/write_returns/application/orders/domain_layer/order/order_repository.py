"""F4-49 — 쓰기 메서드(save · remove)의 반환도 조회와 같은 허용 목록(#355)을 진다.

조회 줄(find_raw #355 · exists_open 후보)은 그대로다. 쓰기의 bool · int(CAS 성공 · 지운 개수)는 후보 물음도 내지 않는다.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from application.orders.domain_layer.order.order import Order
from application.orders.domain_layer.order.value_object.order_code import OrderCode


class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: str) -> Order: ...

    @abstractmethod
    def find_raw(self, order_id: str) -> dict: ...

    @abstractmethod
    def exists_open(self) -> bool: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...

    @abstractmethod
    def save_returning(self, order: Order) -> Order: ...

    @abstractmethod
    def save_all(self, orders: list[Order]) -> list[Order]: ...

    @abstractmethod
    def save_code(self, order: Order) -> OrderCode: ...

    @abstractmethod
    def save_with_version_guard(self, order: Order) -> bool: ...

    @abstractmethod
    def remove_many(self, orders: tuple[Order, ...]) -> int: ...

    @abstractmethod
    def save_raw(self, order: Order) -> dict: ...

    @abstractmethod
    def save_key(self, order: Order) -> str: ...

    @abstractmethod
    def remove_matching(self, orders: list[Order]) -> QuerySet: ...  # noqa: F821

    @abstractmethod
    def save_receipt(self, order: Order) -> SaveReceipt: ...  # noqa: F821

    @abstractmethod
    def save_rows(self, orders: list[Order]) -> "list[OrderModel]": ...  # noqa: F821
