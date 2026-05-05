# benchmark-db-payment-ledger

Variant: dddjango
Category: db-design
Title: Payment ledger DB design conformance rerun
Fixture: none
Mode: design

## Prompt

Django 결제 원장 테이블을 설계해줘. PG 재시도와 중복 webhook 때문에 idempotency key가 있고, 결제/환불 이력은 불변이어야 해. 조회 패턴, 인덱스, 제약조건, transaction, migration 검증을 포함해줘.
