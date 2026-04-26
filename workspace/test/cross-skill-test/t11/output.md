# T11: architecture-db -> architecture-api

**Task:** "Cursor 인덱스를 REST API 페이지네이션으로 노출하는 방법은?"

**Source Skill:** architecture-db

## [주요 내용]

architecture-db 스킬은 Cursor 기반 페이지네이션을 지원하는 인덱스 설계를 다룬다:
- B+Tree 리프 노드의 형제 포인터를 활용한 범위 쿼리
- 커서 컬럼에 대한 인덱스 설계 (정렬 키 + 유니크 보장)
- 최좌선 접두사 규칙을 따르는 복합 인덱스
- (섹션 3: `references/index-and-performance.md` 참조)

그러나 REST API 레벨의 페이지네이션 설계(커서 인코딩, 응답 형식, has_more 필드)는
**이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "REST API 설계 원칙(엔드포인트, 페이지네이션, 상태 코드)에 대해서는 architecture-api에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. 커서 컬럼(created_at + id)에 대한 복합 인덱스 설계
2. Keyset 페이지네이션의 WHERE 조건 최적화
3. Offset vs Cursor의 성능 비교 (DB 레벨)

API 레벨 커서 포맷(불투명 base64), 응답 스키마, 버저닝은
**architecture-api**로 위임한다.

---
> **관련 스킬 참조:**
> - REST API 페이지네이션 설계 (Cursor/Offset/Keyset) -> **architecture-api** 스킬
> - Django Ninja @paginate 구현 -> **implementation-django-ninja** 스킬
