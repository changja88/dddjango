# T33 (Test 32): TDD 중 match/case와 frozen dataclass Python 3.12+ 컨벤션

**Skill:** implementation-tdd (Writing mode)
**Cross-skill references loaded:** implementation-python (match/case, frozen dataclass, Python 3.12+)

## [주요 내용]

### TDD 사이클에서 match/case 활용 (implementation-python 위임)

Red-Green-Refactor 사이클에서 Python 3.12+ 구문을 자연스럽게 적용한다.

### Red: 실패하는 테스트

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

@dataclass(frozen=True)
class OrderCreated:
    order_id: str
    total: Money

@dataclass(frozen=True)
class OrderCancelled:
    order_id: str
    reason: str

type OrderEvent = OrderCreated | OrderCancelled

def test_handle_order_created_updates_inventory():
    event = OrderCreated(order_id="ord-1", total=Money(5000, "KRW"))
    result = handle_event(event)
    assert result == "inventory_updated"

def test_handle_order_cancelled_restores_inventory():
    event = OrderCancelled(order_id="ord-1", reason="customer_request")
    result = handle_event(event)
    assert result == "inventory_restored"

def test_handle_unknown_event_raises():
    with pytest.raises(ValueError, match="Unknown event"):
        handle_event("not_an_event")
```

### Green: match/case 구현

```python
def handle_event(event: OrderEvent) -> str:
    match event:
        case OrderCreated(order_id=oid, total=Money(amount=amt)):
            # 구조적 패턴 매칭으로 중첩 dataclass 분해
            return "inventory_updated"
        case OrderCancelled(order_id=oid, reason=reason):
            return "inventory_restored"
        case _:
            raise ValueError(f"Unknown event: {event}")
```

### Refactor: 타입 별칭과 가드 패턴

```python
# PEP 695 타입 별칭
type OrderEvent = OrderCreated | OrderCancelled

def handle_event(event: OrderEvent) -> str:
    match event:
        case OrderCreated(total=Money(amount=amt)) if amt > 100000:
            return "high_value_inventory_updated"
        case OrderCreated():
            return "inventory_updated"
        case OrderCancelled():
            return "inventory_restored"
        case _:
            raise ValueError(f"Unknown event: {event}")
```

frozen dataclass는 값 객체의 불변성을 보장하며, match/case의 구조적 패턴 매칭과 자연스럽게 결합된다.

---
> **관련 스킬 참조:**
> - [match/case, PEP 695, frozen dataclass] → **implementation-python** 스킬
> - [Value Object 패턴] → 이 스킬 `references/design-patterns-tdd.md`
> - [도메인 이벤트 설계] → **architecture-ddd** 스킬
