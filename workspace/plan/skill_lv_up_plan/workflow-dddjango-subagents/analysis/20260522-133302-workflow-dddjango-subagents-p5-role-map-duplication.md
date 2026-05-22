수정 대상: skill

# P5 workflow role-map 중복 정책 분석

## 배경

P5 source/runtime governance 연계 평가 중 `skill-creator` 관점 real subagent 리뷰가 `workflow-dddjango-subagents`의 `SKILL.md` Canonical Roles section이 `references/role-map.md`, `delegation-rules.md`, `handoff-contract.md`, `integration-checklist.md`의 결정을 일부 중복한다고 지적했다.

## 원인 분류

- 분류: `skill`
- 원인: `SKILL.md`가 `role-map.md`를 exact/canonical source로 지정하면서도 role responsibility와 handoff/cache-sync 규칙 일부를 always-loaded body에 다시 담고 있다.
- 위험: role-map parity를 평가할 때 canonical reference와 runtime-visible skill body가 서로 다른 축으로 drift될 수 있다.

## 판단

Role 이름과 핵심 routing summary는 trigger clarity를 위해 `SKILL.md`에 남겨도 되지만, exact responsibility와 related skills는 `role-map.md`가 owning reference여야 한다. Governance/cache follow-up은 `source-reference-audit` handoff 기준을 유지해야 하므로 관련 문구는 축소하되 제거하지 않는다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
- skill-creator 리뷰: Major 0, Minor 1 for this skill.
리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

## 수정 방향

- `SKILL.md` Canonical Roles section을 role-map navigation 중심으로 줄인다.
- Django web ownership과 source-governance handoff처럼 P5 평가가 직접 요구하는 guardrail은 짧게 보존한다.
- 자세한 role responsibility는 `references/role-map.md`를 owning source로 유지한다.
