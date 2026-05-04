# 레거시 코드 다루기 레퍼런스

16장(레거시 코드 다루기)에 대한 상세 규칙과 예시.
레거시 코드에 테스트를 추가하거나 리팩토링할 때 참조한다.

---

## 1. 레거시 코드의 정의 [WELC]

**레거시 코드란 테스트가 없는 코드다.** 아무리 잘 작성되었든, 아무리 예쁘고
객체지향적이고 잘 캡슐화되었든, 테스트가 없으면 레거시 코드다.

## 2. Seam 개념 [WELC]

**Seam**은 코드를 편집하지 않고도 동작을 변경할 수 있는 지점이다.
테스트를 삽입하기 위한 틈새를 찾는 핵심 개념이다.

| Seam 유형      | 설명                                  | Python 적용                          |
|----------------|---------------------------------------|--------------------------------------|
| Object Seam    | 프로덕션 객체를 테스트용 가짜 객체로 교체 | Protocol + 의존성 주입                |
| Link Seam      | 구현 함수를 교체                       | 모듈 수준 함수 교체 (monkeypatch)      |

```python
# Before — 테스트 불가능
class OrderService:
    def place_order(self, order):
        import smtplib
        server = smtplib.SMTP("smtp.company.com")
        server.send_message(...)

# After — Object Seam (의존성 주입으로 테스트 가능)
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

# 테스트에서 가짜 객체 사용
class FakeEmailSender:
    def __init__(self):
        self.sent_emails = []
    def send(self, to, subject, body):
        self.sent_emails.append((to, subject, body))

def test_place_order():
    sender = FakeEmailSender()
    service = OrderService(email_sender=sender)
    service.place_order(sample_order)
    assert len(sender.sent_emails) == 1
```

## 3. Sprout Method (발아 메서드) [WELC]

새 기능을 추가할 때, 기존 코드를 수정하지 않고 새 메서드로 작성한 후
기존 코드에서 호출한다.

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
        seen = set()
        unique = []
        for entry in entries:
            if entry.id not in seen:
                seen.add(entry.id)
                unique.append(entry)
        return unique
```

## 4. Wrap Method (감싸기 메서드) [WELC]

기존 메서드의 이름을 변경하고, 원래 이름의 래퍼를 만들어 전후에 새 동작을 추가한다.

```python
class Employee:
    def pay(self):
        self._log_payment()       # 새 동작 (전)
        self._dispatch_pay()      # 기존 로직 (이름 변경)
        self._update_records()    # 새 동작 (후)
```

## 5. 특성화 테스트 (Characterization Tests) [WELC]

"올바른 동작"을 검증하는 것이 아니라, **현재 동작을 포착**하는 테스트.
리팩토링 전에 안전망으로 작성한다.

```python
def test_legacy_calculate_tax():
    """현재 동작을 포착한다. '올바른' 결과가 아닌 '현재' 결과를 기대한다."""
    assert legacy_calculate_tax(1000) == 103.5
    assert legacy_calculate_tax(0) == 0
    assert legacy_calculate_tax(-500) == -51.75  # 음수 입력에 대한 현재 동작
```

## 6. Sensing과 Separation [WELC]

- **Sensing (감지)** -- 코드가 계산하는 값에 접근하여 시스템의 다른 부분에 미치는 영향을 파악
- **Separation (분리)** -- 테스트를 위해 코드를 의존성에서 분리

레거시 코드에서 테스트가 어려운 주요 원인은 얽힌 의존성 때문이다.
Seam을 찾아 의존성을 끊고, 감지와 분리를 통해 테스트 가능한 코드로 전환한다.
