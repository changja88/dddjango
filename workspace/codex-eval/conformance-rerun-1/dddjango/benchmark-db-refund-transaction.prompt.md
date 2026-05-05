# benchmark-db-refund-transaction

Variant: dddjango
Category: db-design
Title: Refund transaction DB design conformance rerun
Fixture: none
Mode: design

## Prompt

Django에서 주문 환불 처리를 설계해줘. 부분 환불, 중복 요청, 잔액 초과 환불을 막아야 해. DB 제약, transaction.atomic/select_for_update, 조회 패턴, migration 검증을 포함해줘.
