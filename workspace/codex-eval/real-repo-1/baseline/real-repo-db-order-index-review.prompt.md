# real-repo-db-order-index-review

Variant: baseline
Category: real-repo
Title: Real repo order query index review
Fixture: evals/fixtures/django-shop
Mode: forward-diff

## Prompt

Fixture path: /Users/hyun/Desktop/dddjango/evals/fixtures/django-shop
Read the fixture files before proposing changes. Because evaluation runs in a read-only sandbox, return a unified diff or review findings instead of editing files directly.

Fixture의 주문/예약 조회 패턴을 보고 DB index와 constraint 개선 unified diff를 제안해줘. migration 파일 예시, idempotency_key unique 제약, 자주 쓰는 status/created_at 조회 인덱스를 포함해줘.
