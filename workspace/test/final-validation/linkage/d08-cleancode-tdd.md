# D08: 레거시 코드 리팩터링 전 테스트 전략 (implementation-cleancode 스킬)

**Skill:** implementation-cleancode (Refactoring mode)
**Prompt:** "레거시 코드를 리팩터링하려는데, 테스트가 하나도 없어. 리팩터링 전에 테스트를 먼저 붙여야 할까?"

## [주요 내용]

반드시 테스트를 먼저 붙여야 한다. **레거시 코드란 테스트가 없는 코드다** [WELC]. 테스트 없이 리팩터링하는 것은 안전망 없이 줄타기하는 것과 같다. 리팩터링은 외부 동작을 유지하면서 내부 구조를 개선하는 작업인데, 외부 동작이 유지되는지 확인할 수단이 없으면 리팩터링이 아니라 재작성이 된다.

### 단계별 접근법

**1단계: Characterization Tests (특성화 테스트) 작성**

"올바른 동작"이 아니라 **현재 동작을 포착**하는 테스트를 작성한다. 목적은 기존 동작을 문서화하여 리팩터링 중 의도치 않은 변경을 감지하는 것이다.

```python
def test_legacy_calculate_tax():
    """현재 동작을 포착한다. '올바른' 결과가 아닌 '현재' 결과를 기대한다."""
    assert legacy_calculate_tax(1000) == 103.5
    assert legacy_calculate_tax(0) == 0
    assert legacy_calculate_tax(-500) == -51.75  # 음수 입력에 대한 현재 동작
```

**2단계: Seam을 찾아 의존성을 끊는다**

테스트를 붙이려면 먼저 코드를 테스트 가능하게 만들어야 한다. Seam은 코드를 편집하지 않고도 동작을 변경할 수 있는 지점이다. Python에서는 주로 두 가지 방식을 사용한다:

- **Object Seam**: Protocol + 의존성 주입으로 프로덕션 객체를 테스트용 가짜 객체로 교체
- **Link Seam**: 모듈 수준 함수를 monkeypatch로 교체

```python
# Before -- 테스트 불가능 (의존성이 내부에 감춰져 있다)
class OrderService:
    def place_order(self, order):
        import smtplib
        server = smtplib.SMTP("smtp.company.com")
        server.send_message(...)

# After -- Object Seam으로 테스트 가능하게 전환
class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...

class OrderService:
    def __init__(self, email_sender: EmailSender):
        self._email_sender = email_sender

    def place_order(self, order):
        self._email_sender.send(
            to=order.customer_email,
            subject="Order Confirmation",
            body=f"Order {order.id} placed.",
        )
```

**3단계: 새 기능은 Sprout Method로 추가한다**

기존 레거시 코드를 대규모로 수정하기 전에, 새 기능은 테스트 가능한 별도 메서드로 작성하여 기존 코드에서 호출한다. 이렇게 하면 새 코드는 처음부터 테스트가 있고, 기존 코드의 수정 범위는 최소화된다.

```python
# 기존 레거시 코드 (테스트 없음, 수정하기 위험)
class TransactionGate:
    def post_entries(self, entries):
        for entry in entries:
            entry.post_date = datetime.now()
            self._verify_entry(entry)
            self._persist(entry)

# Sprout: 새 기능을 별도 테스트 가능한 메서드로 작성
class TransactionGate:
    def post_entries(self, entries):
        unique_entries = self._remove_duplicates(entries)  # 발아 메서드 호출
        for entry in unique_entries:
            entry.post_date = datetime.now()
            self._verify_entry(entry)
            self._persist(entry)

    def _remove_duplicates(self, entries):
        """이 메서드는 독립적으로 테스트할 수 있다."""
        seen = set()
        unique = []
        for entry in entries:
            if entry.id not in seen:
                seen.add(entry.id)
                unique.append(entry)
        return unique
```

**4단계: 테스트가 안전망을 제공하면, 그때 리팩터링한다**

특성화 테스트가 현재 동작을 포착하고 있으므로, 이제 안전하게 내부 구조를 개선할 수 있다. 리팩터링 중 테스트가 깨지면 의도치 않은 동작 변경이 발생한 것이므로 즉시 되돌린다.

### 핵심 요약

| 순서 | 활동 | 목적 |
|------|------|------|
| 1 | Characterization Tests | 현재 동작을 안전망으로 포착 |
| 2 | Seam 식별 + 의존성 주입 | 테스트 가능한 구조로 전환 |
| 3 | Sprout/Wrap Method | 새 기능을 안전하게 추가 |
| 4 | 리팩터링 | 테스트 보호 하에 구조 개선 |

---
> **관련 스킬 참조:**
> - [특성화 테스트, Seam 패턴의 구체적 pytest 구현] → **implementation-test** 스킬
> - [테스트 우선 개발로 전환, Red-Green-Refactor 사이클] → **implementation-tdd** 스킬
> - [의존성 주입 시 Python Protocol, dataclass 활용] → **implementation-python** 스킬
