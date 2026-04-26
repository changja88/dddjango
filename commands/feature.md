---
description: Full feature development (domain design → architecture → DB → API → implementation)
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion
---

# 신규 기능 개발

사용자의 요청에 따라 신규 기능을 설계부터 구현까지 전체 과정을 진행한다.

## 1단계: 기본 스킬 로드

다음 스킬 파일을 순서대로 읽는다:

**기본 스킬 (항상 적용):**
1. `skills/implementation-cleancode/SKILL.md` 읽기
2. `skills/implementation-python/SKILL.md` 읽기
3. `skills/implementation-django/SKILL.md` 읽기

## 2단계: TDD 여부 질문

사용자에게 질문한다: "TDD로 진행할까요?"

- **Yes** → 추가로 `skills/implementation-tdd/SKILL.md`를 읽는다.
- **No** → TDD 스킬 없이 진행한다.

## 3단계: 전체 스킬 로드

**설계 스킬:**
4. `skills/architecture-ddd/SKILL.md` 읽기
5. `skills/architecture-implementation-patterns/SKILL.md` 읽기
6. `skills/architecture-db/SKILL.md` 읽기
7. `skills/architecture-api/SKILL.md` 읽기

**구현 스킬:**
8. `skills/implementation-django-ninja/SKILL.md` 읽기

## 4단계: 단계별 실행

다음 순서로 진행한다. 각 단계에서 해당 스킬의 reference를 먼저 로드한 후 작업한다.

### Phase 1: 도메인 설계
`architecture-ddd` 스킬의 **Design** 모드를 따른다.
- 바운디드 컨텍스트 식별
- 유비쿼터스 언어 정의
- Aggregate, Entity, Value Object 설계
- 도메인 이벤트 정의

### Phase 2: 아키텍처 선택
`architecture-implementation-patterns` 스킬의 **Design** 모드를 따른다.
- 아키텍처 패턴 선택 (계층/헥사고날)
- 레이어 분리 및 의존성 방향 결정
- 프로젝트 폴더 구조 설계

### Phase 3: DB 스키마 설계
`architecture-db` 스킬의 **Design** 모드를 따른다.
- 정규화 수준 결정
- 인덱스 전략 수립
- Django ORM 모델 설계

### Phase 4: REST API 설계
`architecture-api` 스킬의 **Design** 모드를 따른다.
- URL 구조 및 리소스 설계
- HTTP 메서드/상태코드 매핑
- 에러 포맷 (RFC 9457)
- 페이지네이션/버저닝 전략

### Phase 5: Django Ninja 구현
`implementation-django-ninja` 스킬의 **Writing** 모드를 따른다.
- Schema/ModelSchema 정의
- Router 및 엔드포인트 구현
- 인증/페이지네이션/필터링
- 에러 핸들러

### Phase 6: 테스트 (TDD 선택 시)
`implementation-tdd` 스킬의 **Writing** 모드를 따른다.
- 각 Phase에서 Red-Green-Refactor 사이클 적용
- 테스트 먼저, 구현 나중

## 참고

- 각 Phase는 사용자 확인 없이 연속으로 진행한다
- Phase 간 전환 시 이전 Phase의 결과를 다음 Phase의 입력으로 사용한다
- 사용자가 특정 Phase를 건너뛰길 원하면 그 Phase를 생략한다
