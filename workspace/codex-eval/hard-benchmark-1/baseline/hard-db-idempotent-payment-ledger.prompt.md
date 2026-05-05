# hard-db-idempotent-payment-ledger

Variant: baseline
Category: db-design
Title: Hard idempotent payment ledger design
Fixture: none
Mode: design

## Prompt

Django 주문 결제 원장을 설계해줘. PG 재시도 때문에 idempotency key가 있고, 같은 결제 이벤트가 두 번 들어와도 원장이 중복되면 안 된다. 조회 패턴, 인덱스, 제약조건, transaction.atomic/locking, migration 검증을 포함해줘.
