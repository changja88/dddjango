# real-repo-drf-to-ninja-migration

Variant: dddjango
Category: real-repo
Title: Real repo DRF to Django Ninja migration
Fixture: evals/fixtures/django-shop
Mode: forward-diff

## Prompt

Fixture path: /Users/hyun/Desktop/dddjango/evals/fixtures/django-shop
Read the fixture files before proposing changes. Because evaluation runs in a read-only sandbox, return a unified diff or review findings instead of editing files directly.

Fixture의 `shop/orders/api_drf.py`는 DRF `ModelSerializer`와 `APIView`를 사용한다. DRF 코드를 생성하지 말고 Django Ninja Schema/Router로 전환하는 unified diff를 제안해줘. `fields='__all__'` 민감 필드 노출 위험도 같이 고쳐줘.
