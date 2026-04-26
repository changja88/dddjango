# T16: implementation-django -> implementation-django-ninja

**Task:** "Django Ninja로 API 엔드포인트를 구현하려면 Schema와 Router는?"

**Source Skill:** implementation-django

## [주요 내용]

implementation-django 스킬은 Django 코어(모델, ORM, 설정, 서비스 레이어)를 다루며,
API 레이어에 대해 명확한 위임 규칙이 있다:

- "API 엔드포인트는 DRF가 아닌 Django Ninja로 구현한다."
- "Django Ninja 패턴(Schema, Router, 인증, 페이지네이션)은 implementation-django-ninja에 위임한다."
- 섹션 7: "모든 Django Ninja 패턴(Schema, Router, 인증, 페이지네이션, 필터링, 에러 처리)은 implementation-django-ninja 스킬을 참조한다."

이 스킬이 제공할 수 있는 부분:
1. API가 호출하는 서비스 레이어 설계 (`<entity>_<action>` 네이밍)
2. 모델 설계와 QuerySet 최적화 (select_related, prefetch_related)
3. 프로젝트 구조 (config/ + apps/ 레이아웃)

Django Ninja Schema/ModelSchema 정의, Router 데코레이터, @paginate,
FilterSchema, 인증 클래스, 에러 처리는 **implementation-django-ninja**로 위임한다.

---
> **관련 스킬 참조:**
> - Django Ninja Schema/Router/인증 -> **implementation-django-ninja** 스킬
> - REST API 설계 원칙 (URL, 상태 코드) -> **architecture-api** 스킬
