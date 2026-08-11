from django.db import OperationalError


class DjangoOrderRepository:
    def save(self, order) -> None:
        attempts: int = 3
        for _ in range(attempts):
            if self._try_persist(order):
                return
        raise OperationalError(f"재고 차감 CAS 경합이 {attempts}회 소진")

    def _try_persist(self, order) -> bool:
        return False
