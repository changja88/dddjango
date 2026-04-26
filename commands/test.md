---
description: Write tests for existing code (pytest, fixtures, mocking, factory_boy)
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent
---

# 테스트 작성

사용자의 요청에 따라 기존 코드에 테스트를 작성한다.

## 1단계: 스킬 로드

다음 스킬 파일을 순서대로 읽고 지시사항을 따른다.
각 스킬의 Reference loading rules에 따라, 코드 생성 전 관련 reference를 로드한다.

**기본 스킬 (항상 적용):**
1. `skills/implementation-cleancode/SKILL.md` 읽기
2. `skills/implementation-python/SKILL.md` 읽기
3. `skills/implementation-django/SKILL.md` 읽기

**커맨드 전용 스킬:**
4. `skills/implementation-test/SKILL.md` 읽기

## 2단계: 모드 판단

사용자 요청에서 모드를 판단한다:
- "테스트 작성해줘", "테스트 추가해줘" → **Writing** 모드
- "테스트 코드 리뷰해줘" → **Review** 모드
- "테스트 코드 리팩토링해줘" → **Refactoring** 모드

모호하면 Writing 모드를 기본으로 한다.

## 3단계: 실행

판단된 모드에 따라 `implementation-test` 스킬의 해당 모드 지침을 따른다.
기본 스킬의 규칙(Python 관례, Django 관례, 클린코드 원칙)도 동시에 적용한다.

코드 작성 전 관련 reference 파일을 반드시 먼저 읽는다.
