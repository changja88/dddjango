# hard-tdd-inventory-idempotency

Variant: dddjango
Category: tdd
Title: Hard inventory reservation TDD
Fixture: none
Mode: implementation

## Prompt

재고 예약 기능을 TDD로 설계해줘. 같은 request_id 재시도는 같은 결과를 돌려야 하고, 재고 부족이면 예약이 생성되면 안 된다. Django DB 저장은 나중에 붙일 예정이라 도메인 정책과 repository port 중심으로 테스트부터 보여줘.
