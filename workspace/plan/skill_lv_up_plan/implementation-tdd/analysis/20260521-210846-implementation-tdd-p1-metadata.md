수정 대상: skill
원인 분류: metadata under-reflection

# implementation-tdd P1 skill 반영 분석

## 평가 범위

- source reference: `workspace/reference/implementation-tdd/reference/final.md`
- source skill: `dddjango/skills/implementation-tdd/SKILL.md`
- bundled references: `dddjango/skills/implementation-tdd/references/*.md`
- metadata: `dddjango/skills/implementation-tdd/agents/openai.yaml`

## 현재 판정

`SKILL.md`와 bundled references는 reference의 핵심 TDD 기준을 대부분 반영한다.

- test list: `SKILL.md` Runtime Rules와 `references/test-list.md`에 반영됨.
- failing tests before implementation: `SKILL.md` Runtime Rules와 `references/red-green-refactor.md`, `references/ai-assisted-tdd.md`에 반영됨.
- Red-Green-Refactor: `references/red-green-refactor.md`에 반영됨.
- Inside-Out vs Outside-In: `references/inside-out-outside-in.md`에 반영됨.
- acceptance/unit loops: `references/inside-out-outside-in.md` Double Loop에 반영됨.
- boundary cases: `SKILL.md` Runtime Rules와 `references/test-list.md`에 반영됨. source reference도 이번 P1 reference loop에서 보강됨.
- refactoring checkpoints: `references/red-green-refactor.md`에 반영됨.
- state vs behavior verification: `references/inside-out-outside-in.md`에 반영됨.
- AI-assisted TDD: `references/ai-assisted-tdd.md`에 반영됨.

부족한 부분은 `agents/openai.yaml`이다. 현재 `short_description`과 `default_prompt`가 test lists, failing tests, Red-Green-Refactor만 드러내며, skill의 중요한 선택 기준인 Inside-Out/Outside-In, boundary cases, state/behavior verification, AI-assisted honesty를 충분히 암시하지 못한다.

## 수정 필요성

- 수정 이유: UI metadata가 skill 목적을 좁게 보이게 하여 P1의 `agents/openai.yaml` 반영도 기준을 약하게 만든다.
- 수정 범위: `dddjango/skills/implementation-tdd/agents/openai.yaml`의 `short_description`, `default_prompt`.
- 수정하지 말아야 할 범위: `SKILL.md`와 bundled references는 현재 P1 기준에서 충분하므로 불필요하게 늘리지 않는다. eval files는 수정하지 않는다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real subagent 2개를 실행했다. 하나는 `skill-creator` 관점, 하나는 source/reference/runtime P1 관점이다. 이 분석 작성 시점에는 리뷰가 진행 중이며, 최종 재평가 분석과 종료 보고에서 결과를 통합한다.

skill-creator 리뷰: `/Users/hyun/.codex/skills/.system/skill-creator/SKILL.md`와 `references/openai_yaml.md`를 읽고 순차 기준도 적용했다. metadata는 짧아야 하지만, skill의 핵심 사용 축을 지나치게 생략하면 trigger chip과 기본 prompt가 실제 skill 범위를 축소한다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

- Major 1: `agents/openai.yaml` metadata가 skill 목적의 일부만 반영한다.

## 완료 조건

- `agents/openai.yaml`의 UI blurb가 25-64자 범위에서 TDD cycle과 approach/edge 선택을 함께 암시한다.
- `default_prompt`가 `$implementation-tdd`를 포함하고, test list, Red-Green-Refactor, approach/edge/verification choice를 짧게 요청한다.
- source skill 변경 후 runtime cache 차이를 확인하고 필요하면 runtime-sync 루프를 수행한다.
