"""순수 도메인 모델 — ORM·프레임워크 무관(표준 §0 #6: 도메인 엔티티 ≠ ORM).

비즈니스 규칙("재고가 충분할 때만 차감")의 단일 소유처는 여기 `Product.deduct()`다.
세 변형 모두 이 동일한 도메인을 import 한다 — 차이는 *누가 이 규칙을 실제로 호출하느냐*뿐이다.
"""
from dataclasses import dataclass


class InsufficientStock(Exception):
    """재고 부족 — 도메인 규칙 위반."""


class ConcurrencyConflict(Exception):
    """낙관적 동시성 충돌이 재시도 상한을 초과."""


@dataclass
class Product:
    id: int
    stock: int
    version: int = 0  # 낙관적 변형만 의미를 가짐; 나머지는 무시한다.

    def deduct(self, quantity: int) -> None:
        """비즈니스 규칙의 권위(authority): 재고가 충분할 때만 차감한다.

        이 메서드가 프로덕션 경로에서 실제로 호출되면 B1(빈혈/죽은 도메인)이 아니다.
        """
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.stock < quantity:
            raise InsufficientStock(f"stock={self.stock} < quantity={quantity}")
        self.stock -= quantity
