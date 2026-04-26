# B03: Aggregate+Repository 설계 리뷰, UoW와 Data Mapper 평가

**Skill:** architecture-ddd (리뷰 mode)
**Design under review:**
Order(Aggregate Root), OrderLine(Entity), Money(VO), OrderRepository Interface

## [주요 내용]

### 리뷰: 잘된 부분

- **Order를 애그리거트 루트로 설정**: 모든 상태 변경이 Order를 통해서만 수행되는 올바른 설계
- **OrderLine을 내부 엔티티로 포함**: 애그리거트 경계 내에서 일관성을 보호
- **Money를 값 객체로 분리**: 불변성과 동등성 보장
- **OrderRepository 인터페이스 정의**: DIP 적용으로 도메인이 인프라에 의존하지 않음

### 리뷰: 개선 사항

[Vernon 규칙 2: 작은 애그리거트] -- OrderLine이 Entity인지 확인 필요. OrderLine에 독자적 생명주기가 없다면 값 객체(frozen dataclass)가 더 적합하다. 값 객체는 불변성으로 부수효과를 제거한다.

[Vernon 규칙 3: ID 참조] -- Order가 다른 애그리거트(Customer, Product)를 직접 객체 참조하는지 확인 필요. ID로만 참조해야 결합도가 낮아진다.

[Vernon 규칙 4: 결과적 일관성] -- 주문 생성 후 재고 차감, 포인트 적립 등은 도메인 이벤트를 통한 결과적 일관성으로 처리해야 한다.

### UoW (Unit of Work) 평가

```python
class UnitOfWork(Protocol):
    orders: OrderRepository

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, *args) -> None: ...
    def commit(self) -> None: ...
```

Django에서는 `transaction.atomic()`이 UoW 역할을 한다. 별도 UoW 클래스는 Django의 Active Record 패턴에서는 과도한 추상화일 수 있다. 서비스 함수에서 `@transaction.atomic` 데코레이터로 충분하다.

### Data Mapper 평가

```python
class DjangoOrderRepository(OrderRepository):
    def _to_domain(self, orm_obj: OrderModel) -> Order:
        """ORM -> Domain 변환 (Data Mapper)"""
        return Order(
            id=str(orm_obj.id),
            orderer_id=str(orm_obj.orderer_id),
            order_lines=[...],
        )

    def _to_orm(self, domain_obj: Order) -> OrderModel:
        """Domain -> ORM 변환"""
        ...
```

Data Mapper는 도메인 모델을 ORM에서 완전히 분리한다. 핵심 도메인에서는 가치가 있지만, 지원/범용 서브도메인에서는 Django ORM을 직접 사용하는 것이 실용적이다.

---
> **관련 스킬 참조:**
> - [헥사고날, Repository + UoW 구현] → **architecture-implementation-patterns** 스킬
> - [Django ORM, 서비스 레이어] → **implementation-django** 스킬
> - [Python Protocol, frozen dataclass] → **implementation-python** 스킬
