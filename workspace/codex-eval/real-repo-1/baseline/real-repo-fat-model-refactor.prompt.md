# real-repo-fat-model-refactor

Variant: baseline
Category: real-repo
Title: Real repo fat model refactor
Fixture: evals/fixtures/django-shop
Mode: forward-diff

## Prompt

Fixture path: /Users/hyun/Desktop/dddjango/evals/fixtures/django-shop
Read the fixture files before proposing changes. Because evaluation runs in a read-only sandbox, return a unified diff or review findings instead of editing files directly.

Fixture의 `shop/orders/models.py`를 읽고 `Order.cancel()`의 비즈니스 규칙을 DDD application service로 옮기는 unified diff를 제안해줘. Django 모델은 상태 저장과 불변식 최소 검증만 담당하게 하고, pytest 테스트 보강도 diff에 포함해줘.
