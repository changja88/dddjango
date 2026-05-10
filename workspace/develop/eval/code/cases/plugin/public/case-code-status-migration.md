Fixture repo에서 주문 상태 rollout을 위한 migration 초안을 작성해줘.

요구사항:
- 기존 주문에 `status`가 없던 배포를 가정하고 expand/backfill/contract 단계를 코드나 migration 주석으로 표현해.
- hot table에서 바로 NOT NULL과 index를 거는 위험을 피하는 방향이어야 해.
- Django migration 책임과 DB rollout 위험을 구분해서 남겨줘.
- 검증 가능한 테스트 또는 최소한 compile 검증을 실행해줘.
