수정 대상: skill
리뷰 방식: sequential-fallback
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# workflow-dddjango-subagents P1 skill 반영 분석

## 평가 요약

Dedicated source reference 작성 후 `dddjango/skills/workflow-dddjango-subagents/`를 재평가했다. 기존 skill과 bundled references는 역할 분해, handoff, sequential fallback, cache sync의 핵심을 이미 포함하지만 새 source decision을 충분히 반영하려면 보강이 필요하다.

## Findings

| 등급 | 항목 | 근거 | 필요한 수정 |
|---|---|---|---|
| Resolved | critical path vs sidecar delegation 기준이 reference보다 약했다 | `SKILL.md`에 critical path 언급은 있으나 `delegation-rules.md`가 critical path, sidecar, advisory, shared write 구분을 source 수준으로 담지 않았다 | `SKILL.md`와 `delegation-rules.md`에 판단 기준을 보강했다 |
| Resolved | source/runtime boundary와 eval follow-up 분류가 runtime checklist에 약했다 | source reference는 runtime bundle/source 분리와 eval 문제 후속 분류를 명시하지만 runtime references에는 cache sync 중심으로만 표현됐다 | `integration-checklist.md`와 `SKILL.md`에 P1/검증 시 reporting 기준을 보강했다 |
| Resolved | 문서 언어가 한글 기본 원칙과 맞지 않았다 | workflow skill 및 bundled references가 대부분 영어 설명문이었다 | trigger vocabulary와 validator 문구는 보존하면서 설명문을 한글 중심으로 변경했다 |

## skill-creator 리뷰

순차 fallback으로 `skill-creator` 기준을 적용했다.

- Trigger description: explicit subagent, workflow, risky Django/DDD trigger와 opt-out negative routing이 포함되어 있어 유지 가능하다.
- Progressive disclosure: `SKILL.md`가 네 reference를 직접 링크하고 있어 구조는 적절하다. 다만 reference별 역할 설명을 source decision에 맞게 더 선명하게 해야 한다.
- Reference duplication: canonical role table은 `SKILL.md`와 `role-map.md`에 중복되지만 runtime validator와 immediate output guidance를 위해 허용 가능한 핵심 중복이다. 상세 판단은 references로 둔다.
- Validation integrity: 실제 subagent/result collection 정직성은 있으나, eval 문제를 P1에서 고치지 않는 분류 기준과 source/runtime boundary가 runtime guidance에 약하다.

## Subagent 리뷰/순차 fallback

Subagent 리뷰/순차 fallback: 순차 fallback. 이 단계에서는 먼저 source 반영 patch를 작성한 뒤 real subagent review를 별도 검증 단계에서 실행하는 것이 적절하다. 현재 findings는 patch 이후 재평가해야 한다.

## 결론

`SKILL.md`, `references/delegation-rules.md`, `references/role-map.md`, `references/handoff-contract.md`, `references/integration-checklist.md`, `agents/openai.yaml`을 수정했다. 이후 real subagent 리뷰에서 추가 지적된 eval follow-up label, eval/Serena honesty, runtime-sync 위치 detail도 보강했다.

## 재평가 결과

`diff -rq`로 source/cache parity를 확인했고 차이가 없었다. `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`는 `OK: validation passed with 0 warning(s)`로 통과했다. 열린 skill 반영 finding은 없다.
