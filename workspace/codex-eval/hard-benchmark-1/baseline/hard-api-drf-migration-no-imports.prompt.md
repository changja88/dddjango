# hard-api-drf-migration-no-imports

Variant: baseline
Category: api-design
Title: Hard DRF migration without leftover imports
Fixture: none
Mode: implementation

## Prompt

기존 DRF ViewSet + ModelSerializer 상품 API를 Django Ninja로 옮기는 패치를 제안해줘. 답변에는 rest_framework import나 DRF 클래스 구현이 남으면 안 된다. Schema, Router, URL 연결, 검증 명령까지 포함해줘.
