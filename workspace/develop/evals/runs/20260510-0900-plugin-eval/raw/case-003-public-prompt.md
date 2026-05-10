# Case 003

각 요청을 독립적인 사용자 요청으로 보고, 서로 섞지 말고 순서대로 답해줘.

## Requests

```text
주문 상태 컬럼을 추가하고 기존 데이터를 backfill한 뒤 NOT NULL과 index를 적용하는 Django migration 계획을 세워줘.
```

```text
Django Ninja로 주문 목록 API를 만들고 auth, pagination, filtering, response schema 기준을 정리해줘.
```

```text
Django TemplateView 기반 주문 상세 페이지를 추가하고 template/static/HTMX/CSRF 구조를 정리해줘.
```

```text
주문 상태 전이 코드를 Python 타입 힌트, dataclass, StrEnum으로 더 명시적으로 리팩터링해줘.
```

```text
Order 모델이 너무 커졌는지 리뷰하고 어떤 로직을 model method에 남길지, service/usecase로 뺄지 판단해줘.
```

```text
쿠폰 할인 정책을 TDD로 구현하고 최소 주문 금액, 중복 사용 금지, 만료일 boundary case를 포함해줘.
```

```text
Django Ninja API contract test를 pytest fixture, factory, test double 기준으로 작성해줘.
```

```text
주문 도메인의 bounded context, aggregate, invariant, domain event를 DDD 기준으로 설계해줘.
```

```text
결제 승인 유스케이스에 hexagonal architecture, repository, UoW, outbox, ACL을 적용해야 하는지 판단해줘.
```

```text
재고 차감과 예약 확정이 동시에 들어오는 상황에서 DB constraint, transaction, locking, idempotency 저장 방식을 설계해줘.
```

```text
주문 생성 REST API의 endpoint, status code, Problem Details 오류, Idempotency-Key, OpenAPI 기준을 설계해줘.
```

```text
주문 생성 기능을 DDD 설계부터 DB/API/Django 구현과 테스트까지 역할별로 나눠 진행 계획을 세워줘.
```
