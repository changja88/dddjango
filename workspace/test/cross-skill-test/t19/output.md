# T19: implementation-django -> implementation-python

**Task:** "Django 매니저에서 async generator와 TaskGroup 비동기 배치 처리는?"

**Source Skill:** implementation-django

## [주요 내용]

implementation-django 스킬은 Django Manager/QuerySet 패턴을 다룬다:
- 커스텀 QuerySet 메서드를 통한 체이닝 가능한 필터링
- bulk_create/bulk_update를 통한 배치 작업
- (섹션 4: `references/queryset-manager.md` 참조)

그러나 async generator와 TaskGroup의 Python 비동기 패턴은
**이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "Python 전용 관용구(타입 힌트, dataclasses, async)는 implementation-python에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. Django Manager 정의와 `from_queryset()` 사용
2. Django 4.1+ 네이티브 async ORM (`Model.objects.aget()`, `afilter()`)
3. `sync_to_async`를 통한 동기 ORM 래핑

Python `asyncio.TaskGroup` (3.11+), `except*`를 통한 `ExceptionGroup` 처리,
`yield`/`async for` 제너레이터 패턴은 **implementation-python**으로 위임한다.

---
> **관련 스킬 참조:**
> - Python asyncio TaskGroup과 async generator -> **implementation-python** 스킬
> - Django Ninja async 뷰 -> **implementation-django-ninja** 스킬
