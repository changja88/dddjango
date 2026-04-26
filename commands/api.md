---
description: Design and implement Django Ninja API endpoints (Schema, Router, auth, pagination)
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion
---

# API 개발

사용자의 요청에 따라 REST API를 설계하고 Django Ninja로 구현한다.

## 1단계: 기본 스킬 로드

다음 스킬 파일을 순서대로 읽고 지시사항을 따른다.
각 스킬의 Reference loading rules에 따라, 코드 생성 전 관련 reference를 로드한다.

**기본 스킬 (항상 적용):**
1. `skills/implementation-cleancode/SKILL.md` 읽기
2. `skills/implementation-python/SKILL.md` 읽기
3. `skills/implementation-django/SKILL.md` 읽기

**커맨드 전용 스킬:**
4. `skills/architecture-api/SKILL.md` 읽기
5. `skills/implementation-django-ninja/SKILL.md` 읽기

## 2단계: TDD 여부 질문

사용자에게 질문한다: "TDD로 진행할까요?"

- **Yes** → 추가로 `skills/implementation-tdd/SKILL.md`를 읽는다.
  Red-Green-Refactor 사이클로 개발을 진행한다.
- **No** → TDD 스킬 없이 진행한다.

## 3단계: 모드 판단

사용자 요청에서 모드를 판단한다:
- "만들어줘", "구현해줘" → **Design** (api) + **Writing** (ninja)
- "리뷰해줘" → **Review** 모드
- "리팩토링해줘" → **Refactoring** 모드

모호하면 Design + Writing 모드를 기본으로 한다.

## 4단계: 실행

**Design + Writing 모드 (기본):**
1. `architecture-api` 스킬의 Design 모드로 REST API를 설계한다
   - URL 구조, HTTP 메서드, 상태 코드, 에러 포맷
2. `implementation-django-ninja` 스킬의 Writing 모드로 구현한다
   - Schema, Router, 인증, 페이지네이션, 에러 처리
3. TDD 선택 시: 각 엔드포인트마다 Red-Green-Refactor 사이클 적용

**Review/Refactoring 모드:**
- 로드된 스킬의 해당 모드 지침을 따른다

코드 작성 전 관련 reference 파일을 반드시 먼저 읽는다.
