현재 `/private/tmp/dddjango-codex-eval`에는 코드가 없어 프로젝트 고유 도메인은 확인할 수 없었습니다. 그래서 일반적인 DDD/Django 기준으로 답하면, **테이블 기준이 아니라 비즈니스 언어와 일관성 경계 기준**으로 나누는 게 좋습니다.

**추천 순서**

1. **바운디드 컨텍스트부터 나누기**
   같은 단어가 다른 의미로 쓰이면 분리 후보입니다.

   예:
   - `회원` in 인증: 로그인 주체
   - `회원` in 주문: 구매자
   - `회원` in 정산: 지급 대상자

   이런 경우 하나의 `Member` 모델로 합치기보다 `identity`, `ordering`, `settlement`처럼 컨텍스트를 나누는 편이 낫습니다.

2. **컨텍스트 안에서 애그리거트 나누기**
   애그리거트는 “항상 한 트랜잭션에서 같이 지켜야 하는 규칙”의 단위입니다.

   좋은 기준:
   - 같이 생성/수정/삭제되어야 하는가?
   - 하나의 비즈니스 명령으로 상태가 바뀌는가?
   - 불변식을 지키려면 같은 락/트랜잭션 안에 있어야 하는가?

   아니면 ID로만 연결하고 별도 애그리거트로 둡니다.

3. **값 객체 먼저 찾기**
   고유 ID보다 값 자체가 중요한 것은 값 객체로 둡니다.

   예:
   - `Money`
   - `Address`
   - `DateRange`
   - `Email`
   - `PhoneNumber`
   - `Quantity`

4. **도메인 서비스는 마지막에**
   로직이 특정 애그리거트에 자연스럽게 들어가면 애그리거트 메서드로 둡니다.

   예:
   - `order.cancel()` 좋음
   - `OrderService.cancel(order)` 남용 주의

   여러 애그리거트의 정보가 필요하지만 상태를 갖지 않는 계산/판단만 도메인 서비스로 뺍니다.

**Django 구조 예시**

```text
applications/
  ordering/
    domain_layer/
      order/
        order.py              # Order aggregate root
        order_line.py
        shipping_info.py
      value_object/
        money.py
        address.py
      repository/
        order_repository.py
      event/
        order_events.py
    application_layer/
      order_service.py
    infra_layer/
      django_ordering/
        models/
          order_model.py
      repository/
        django_order_repository.py
    presentation_layer/
      api/
      schema/
```

**애그리거트 예시**

```python
@dataclass
class Order:
    """Order aggregate root.

    불변식:
    - 주문은 최소 1개 이상의 주문 라인을 가진다.
    - 결제 완료 이후에는 주문 라인을 변경할 수 없다.
    - 배송 시작 이후에는 배송지를 변경할 수 없다.
    """

    id: OrderId
    orderer_id: MemberId
    lines: list[OrderLine]
    shipping_info: ShippingInfo
    status: OrderStatus

    def confirm(self) -> None:
        if not self.lines:
            raise EmptyOrderError()
        if self.status != OrderStatus.DRAFT:
            raise OrderCannotBeConfirmedError()
        self.status = OrderStatus.CONFIRMED
```

**분리 기준 요약**

| 기준 | 같이 둔다 | 나눈다 |
|---|---|---|
| 트랜잭션 | 항상 같이 변경됨 | 따로 변경 가능 |
| 언어 | 같은 의미의 용어 | 같은 단어가 다른 의미 |
| 규칙 | 같은 불변식으로 묶임 | 이벤트로 이어져도 됨 |
| 참조 | 내부 구성요소 | ID 참조 |
| 로직 | 애그리거트가 직접 판단 가능 | 여러 애그리거트 판단 필요 |

제일 현실적인 출발점은 **컨텍스트 2~4개 정도로 크게 나누고, 각 컨텍스트 안의 애그리거트는 작게 유지**하는 것입니다. 처음부터 모든 테이블을 도메인 객체로 만들기보다, 핵심 유스케이스에서 상태가 바뀌는 객체부터 모델링하는 게 좋습니다.

---
> **관련 스킬 참조:**
> - Django 폴더 구조/ORM 매핑 → **implementation-django** 스킬
> - DB 테이블/인덱스 설계 → **architecture-db** 스킬
> - API 경계와 요청/응답 설계 → **architecture-api** 스킬