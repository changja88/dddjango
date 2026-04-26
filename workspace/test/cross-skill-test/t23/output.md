# T23: implementation-django-ninja -> implementation-django

**Task:** "Django Ninja API에서 QuerySet 최적화와 custom Manager 패턴은?"

**Source Skill:** implementation-django-ninja

## [주요 내용]

implementation-django-ninja 스킬은 Django Ninja API 구현 패턴을 다룬다:
- Schema/ModelSchema를 통한 요청/응답 검증
- Router 데코레이터 패턴 (@router.get, @router.post)
- @paginate, FilterSchema, 인증 클래스
- async 뷰와 에러 처리

그러나 QuerySet 최적화와 custom Manager 패턴은 **이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "Django 코어(모델, QuerySet, 마이그레이션, 설정)는 implementation-django에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. API 엔드포인트에서 QuerySet을 반환하는 패턴
2. @paginate 데코레이터를 통한 페이지네이션
3. FilterSchema를 통한 필터링 조건 적용

커스텀 QuerySet 메서드 정의, select_related()/prefetch_related() 패턴,
Prefetch() 객체, bulk_create/bulk_update, annotate()/alias(),
커스텀 Manager(from_queryset())는 **implementation-django**로 위임한다.

---
> **관련 스킬 참조:**
> - QuerySet 최적화와 Manager 패턴 -> **implementation-django** 스킬
> - 인덱스 설계와 쿼리 성능 -> **architecture-db** 스킬
