# T03: architecture-ddd -> architecture-api

**Task:** "주문 Bounded Context에서 REST API URL 구조와 상태 코드 설계를 하고 싶습니다"

**Source Skill:** architecture-ddd

## [주요 내용]

architecture-ddd 스킬은 주문 Bounded Context의 경계와 도메인 모델을 다루지만,
REST API URL 구조, HTTP 상태 코드 설계는 **이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "REST API 설계 원칙(엔드포인트, 상태 코드, 버저닝)에 대해서는 architecture-api에 위임한다."

DDD 스킬이 제공할 수 있는 부분:
1. 주문 Bounded Context 경계 식별 (주문, 주문 항목, 배송 주소)
2. 유비쿼터스 언어 기반 리소스 네이밍 도출 (orders, order-items)
3. 도메인 이벤트 기반 상태 전이 식별 (OrderPlaced, OrderConfirmed, OrderShipped)

URL 구조(`/v1/orders`, `/v1/orders/{id}/items`), 상태 코드(201, 404, 409),
RFC 9457 에러 형식은 **architecture-api**로 위임한다.

---
> **관련 스킬 참조:**
> - REST API URL 설계와 상태 코드 -> **architecture-api** 스킬
> - Django Ninja로 API 엔드포인트 구현 -> **implementation-django-ninja** 스킬
