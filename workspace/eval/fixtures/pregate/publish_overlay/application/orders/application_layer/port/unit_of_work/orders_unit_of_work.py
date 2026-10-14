from abc import ABC, abstractmethod
from collections.abc import Callable
from types import TracebackType
from typing import Self


class OrdersUnitOfWork(ABC):
    @abstractmethod
    def __enter__(self) -> Self:
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None:
        raise NotImplementedError

    @abstractmethod
    def after_commit(self, callback: Callable[[], None]) -> None:
        raise NotImplementedError
