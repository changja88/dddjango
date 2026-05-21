수정 대상: reference
원인 분류: source gap

# implementation-tdd P1 reference 분석

## 평가 범위

- source reference: `workspace/reference/implementation-tdd/reference/final.md`
- 비교 대상: `dddjango/skills/implementation-tdd/SKILL.md`, `dddjango/skills/implementation-tdd/references/*.md`
- P1 기준: test list, failing tests before implementation, Red-Green-Refactor, Inside-Out vs Outside-In, acceptance/unit loops, boundary cases, refactoring checkpoints, state vs behavior verification, AI-assisted TDD

## 현재 판정

`final.md`는 Red-Green-Refactor, 테스트 목록, 실패 테스트 우선, Inside-Out/Outside-In, 상태/행위 검증, 이중 루프, 리팩토링 체크포인트, AI 보조 TDD를 판단하기에 충분하다.

다만 boundary cases 기준은 일반 원칙으로 충분히 닫혀 있지 않다. `external.md`에는 mutation testing 예시에서 `10`과 `11` 같은 경계값 예제가 있고, `final.md`에는 AI 보조 TDD 예시의 edge case 표현이 있지만, 여러 독립 결정축이 있는 정책에서 각 축별 허용 경계와 가장 가까운 거부/보완 사례를 테스트 목록에 넣어야 한다는 일반화된 기준은 없다.

현재 runtime skill은 `test-list.md`와 `SKILL.md`에서 경계 정책, 유효 기간, 만료일, 독립 결정축을 구체적으로 안내한다. 이 안내는 TDD skill의 실제 오답 방지에 필요하지만, source reference가 그 수준을 명시적으로 뒷받침하지 않으면 reference 부족을 skill 규칙으로 덮는 상태가 된다.

## 수정 필요성

- 수정 이유: P1 기준의 `boundary cases`를 source reference만으로 판단할 수 있게 만든다.
- 수정 범위: `workspace/reference/implementation-tdd/reference/final.md`의 테스트 목록 섹션에 boundary/decision-axis 테스트 목록 규칙을 추가한다.
- 수정하지 말아야 할 범위: eval case, answer oracle, evaluator, runtime skill, bundled references는 이 reference gap의 직접 수정 대상이 아니다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real subagent 2개를 실행했다. 하나는 `skill-creator` 관점, 하나는 source/reference/runtime P1 관점이다. 이 분석 작성 시점에는 리뷰가 진행 중이며, 최종 재평가 분석과 종료 보고에서 결과를 통합한다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

- Major 1: boundary cases에 대한 source reference 일반 규칙이 부족하다.

## 완료 조건

- `final.md`가 boundary cases, 독립 결정축, inclusive/exclusive 경계, 유효 기간/만료일 예시를 일반 원칙으로 설명한다.
- runtime skill의 boundary guidance가 source reference와 충돌하지 않는다.
- 수정 후 skill 반영도와 runtime sync를 별도로 재평가한다.
