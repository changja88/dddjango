---
description: Refactor code (auto-detect relevant skills based on code analysis)
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# 코드 리팩토링

사용자가 제시한 코드를 분석하고, 관련 스킬을 자동 선택하여 리팩토링한다.

## 1단계: 기본 스킬 로드

다음 스킬 파일을 순서대로 읽는다:

**기본 스킬 (항상 적용):**
1. `skills/implementation-cleancode/SKILL.md` 읽기
2. `skills/implementation-python/SKILL.md` 읽기
3. `skills/implementation-django/SKILL.md` 읽기

## 2단계: 코드 분석 및 추가 스킬 선택

사용자가 제시한 코드 또는 파일을 분석하여, 아래 기준에 따라 추가 스킬을 로드한다.
**해당하는 모든 스킬을 로드한다 (복수 가능).**

| 코드 특성 | 추가 로드 스킬 |
|----------|--------------|
| Django Ninja Schema/Router/API 코드 | `skills/implementation-django-ninja/SKILL.md` |
| Django 템플릿, 정적 파일, TemplateView | `skills/implementation-django-web/SKILL.md` |
| 테스트 코드 (pytest, TestCase) | `skills/implementation-test/SKILL.md` |
| 헥사고날/CQRS/이벤트소싱 구조 | `skills/architecture-implementation-patterns/SKILL.md` |
| DDD 패턴 (Aggregate, Repository, VO) | `skills/architecture-ddd/SKILL.md` |
| DB 스키마/인덱스/쿼리 최적화 이슈 | `skills/architecture-db/SKILL.md` |
| REST API 설계 이슈 (URL, 상태코드) | `skills/architecture-api/SKILL.md` |

## 3단계: Refactoring 모드 실행

로드된 모든 스킬의 **Refactoring 모드** 지침을 따른다:

1. 각 스킬의 Refactoring 체크리스트를 적용한다
2. Before/After/Reason 형식으로 변경사항을 제시한다
3. 각 변경을 해당 스킬의 컨벤션에 연결한다
4. 최종적으로 완전한 리팩토링 코드를 제공한다

코드 수정 전 관련 reference 파일을 반드시 먼저 읽는다.
