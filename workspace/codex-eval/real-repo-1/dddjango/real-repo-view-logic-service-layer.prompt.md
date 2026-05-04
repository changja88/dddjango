# real-repo-view-logic-service-layer

Variant: dddjango
Category: real-repo
Title: Real repo view logic service layer extraction
Fixture: evals/fixtures/django-shop
Mode: forward-diff

## Prompt

Fixture path: /Users/hyun/Desktop/dddjango/evals/fixtures/django-shop
Read the fixture files before proposing changes. Because evaluation runs in a read-only sandbox, return a unified diff or review findings instead of editing files directly.

Fixture의 `shop/orders/views.py`에서 `reserve_inventory`가 HTTP 파싱, transaction, 재고 차감, 응답 생성을 모두 처리하고 있어. application service를 분리하는 unified diff를 제안하고, view는 HTTP 변환만 담당하게 만들어줘.
