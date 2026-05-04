# real-repo-ninja-product-search

Variant: dddjango
Category: real-repo
Title: Real repo Django Ninja product search API
Fixture: evals/fixtures/django-shop
Mode: forward-diff

## Prompt

Fixture path: /Users/hyun/Desktop/dddjango/evals/fixtures/django-shop
Read the fixture files before proposing changes. Because evaluation runs in a read-only sandbox, return a unified diff or review findings instead of editing files directly.

Fixture의 `shop/orders/models.py`를 기준으로 Product 검색/목록 API를 Django Ninja로 추가하는 unified diff를 제안해줘. FilterSchema, Query, 정렬 allow-list, items/meta envelope, `request: HttpRequest`, return type, `application/problem+json` 검증을 포함해줘.
