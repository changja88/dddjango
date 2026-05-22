수정 대상: skill

# P5 source-reference-audit 중복 정책 분석

## 배경

P5 source/runtime governance 연계 평가 중 `skill-creator` 관점 real subagent 리뷰가 `source-reference-audit`의 always-loaded `SKILL.md`와 bundled reference `references/source-governance.md` 사이에 같은 governance 결정이 넓게 중복된다고 지적했다.

## 원인 분류

- 분류: `skill`
- 원인: `SKILL.md`가 `source-governance.md`를 읽으라고 안내하면서도 path boundary, metadata/cache sync, leakage/public wording, eval traceability, validation coverage 세부 결정을 다시 길게 보유한다.
- 위험: source/runtime governance 문구를 바꿀 때 skill body와 reference 중 하나만 갱신되어 P5 cache/source sync와 public leakage 판정이 서로 어긋날 수 있다.

## 판단

`SKILL.md`에는 trigger, routing, reference loading, validator가 요구하는 최소 runtime guardrail 문구를 남기고, 세부 결정은 `source-governance.md`를 source of truth로 유지하는 것이 맞다. 다만 현재 validator가 `SKILL.md` 안의 특정 guardrail phrase를 확인하므로 section 자체와 핵심 문구는 보존해야 한다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
- skill-creator 리뷰: Major 1, Minor 0 for this skill.
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 수정 방향

- `SKILL.md`의 세부 정책 나열을 줄이고 `source-governance.md`를 owning reference로 명확히 한다.
- validator-required headings/phrases는 유지한다.
- public wording, runtime-facing path boundary, eval traceability, validation coverage는 짧은 guardrail 형태로 남긴다.
