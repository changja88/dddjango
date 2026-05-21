수정 대상: skill
원인 분류: progressive disclosure duplication

# implementation-tdd P1 boundary guidance 중복 분석

## 평가 범위

- source skill: `dddjango/skills/implementation-tdd/SKILL.md`
- bundled reference: `dddjango/skills/implementation-tdd/references/test-list.md`
- 리뷰 근거: real subagent `skill-creator` 관점 리뷰

## 현재 판정

`SKILL.md` Runtime Rules의 boundary-policy 세부 규칙이 `references/test-list.md`의 boundary/decision-axis 규칙과 상당 부분 중복된다. 해당 규칙은 중요하지만, `skill-creator` 기준상 상세 reference material은 한 곳에 두고 `SKILL.md`에는 핵심 실행 규칙과 reference discoverability를 남기는 편이 drift risk를 줄인다.

## 수정 필요성

- 수정 이유: boundary cases 중요성은 유지하되, 세부 예외와 예시는 `references/test-list.md`로 모아 progressive disclosure를 개선한다.
- 수정 범위: `SKILL.md` Runtime Rules의 boundary 관련 3개 bullet을 짧은 필수 규칙 1개로 축약한다.
- 수정하지 말아야 할 범위: `references/test-list.md`는 이미 상세 기준을 충분히 담고 있으므로 수정하지 않는다. eval files는 수정하지 않는다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real subagent `skill-creator` 관점 리뷰가 중복에 따른 drift risk를 Minor로 지적했다. 메인 판단도 이를 유효한 열린 Minor로 채택한다.

skill-creator 리뷰: `SKILL.md`는 짧고 핵심 절차 중심이어야 하며, 상세 reference material은 bundled references로 분리하는 것이 권장된다.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

- Minor 1: boundary-policy guidance가 `SKILL.md`와 `references/test-list.md`에 중복되어 drift risk가 있다.

## 완료 조건

- `SKILL.md`가 boundary cases를 필수 runtime rule로 유지한다.
- detailed boundary examples and independent-axis rules are discoverable through `references/test-list.md`.
- 수정 후 source skill과 runtime cache 동기화 여부를 다시 확인한다.
