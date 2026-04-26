# T13: architecture-api -> architecture-db

**Task:** "API 페이지네이션 지원 DB 인덱스 전략은?"

**Source Skill:** architecture-api

## [주요 내용]

architecture-api 스킬은 페이지네이션의 API 설계 측면을 다룬다:
- Offset (단순, 성능 저하), Cursor (일관성, 빠름), Keyset (인덱스 기반)
- Cursor는 1M+ 레코드에서 Offset보다 17배 빠르다
- 불투명 base64 인코딩 커서, has_more 응답 필드
- (섹션 7: `references/pagination.md` 참조)

그러나 DB 인덱스 전략(B+Tree, 복합 인덱스 컬럼 순서)은
**이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "데이터베이스 스키마 설계(정규화, 인덱스)에 대해서는 architecture-db에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. Cursor vs Offset 페이지네이션의 API 레벨 트레이드오프
2. 커서 응답 형식 설계 (next_cursor, has_more)
3. 페이지네이션 파라미터 설계 (limit, cursor)

커서 컬럼의 복합 인덱스 설계, Keyset WHERE 절 최적화,
B+Tree 리프 노드 활용은 **architecture-db**로 위임한다.

---
> **관련 스킬 참조:**
> - 페이지네이션 지원 인덱스 설계 -> **architecture-db** 스킬
> - Django Ninja @paginate 구현 -> **implementation-django-ninja** 스킬
