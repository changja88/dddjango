# S06 Baseline: 역할 간 충돌 통합 우선순위

필수 기대 기준:

- Domain Agent와 API Agent 제안의 충돌을 명시한다.
- conflict priority에 따라 도메인 불변식과 상태 전이를 API 편의보다 우선한다.
- `status` 직접 변경 대신 `Order.confirm()` 같은 명시적 도메인/application operation을 사용한다.
- API contract, transaction/idempotency, test 영향을 함께 정리한다.
- 실제 subagent를 실행하지 않았다면 실행했다고 말하지 않는다.

