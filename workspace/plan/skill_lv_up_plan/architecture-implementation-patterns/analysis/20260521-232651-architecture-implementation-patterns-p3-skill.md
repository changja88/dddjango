수정 대상: skill
원인 분류: p3-handoff-progressive-disclosure

# architecture-implementation-patterns P3 skill 분석

## 평가 범위

- 대상 skill: `dddjango/skills/architecture-implementation-patterns/`
- source reference: `workspace/reference/architecture-implementation-patterns/reference/final.md`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-implementation-patterns/`
- 비교 표면: `SKILL.md`, `agents/openai.yaml`, bundled references, neighboring skill routing, workflow role map

## 현재 상태

`SKILL.md`는 40줄로 500줄 미만이며, 세부 판단은 `references/pattern-selection.md`, `references/ports-adapters.md`, `references/repository-uow.md`, `references/outbox-acl.md`에 1단계 직접 링크로 연결되어 있다. Pattern 선택, dependency direction, repository/UoW, outbox/saga/ACL, risky write handoff의 세부 기준은 bundled reference에 있고, `SKILL.md`에는 routing과 runtime 핵심 규칙만 남아 있어 progressive disclosure 구조는 적절하다.

Source reference는 이 skill의 dedicated source reference로 충분하며, fallback/provisional로 낮춰 말하지 말라는 honesty 기준도 명시한다. `SKILL.md`와 bundled references는 source reference의 주요 결정을 runtime-facing 언어로 반영한다.

## 발견 사항

| 분류 | 상태 | 근거 | 판단 |
|---|---|---|---|
| 구현 skill handoff | 열린 Minor | `SKILL.md`는 pattern 결정 후 concrete code를 "relevant implementation skill"로 넘기라고만 하며, source handoff table은 Django, Ninja, Python, Test, Workflow target을 더 명확히 구분한다. | 같은 결정을 서로 다르게 하지는 않지만 runtime routing 추론이 불필요하게 남는다. |
| source/reference audit handoff | 열린 Minor | `source-reference-audit`는 source/reference governance, runtime cache sync, metadata alignment, leakage, validation coverage를 소유한다. 현재 target `SKILL.md`는 DDD/DB/API/implementation/test/workflow handoff는 말하지만 source audit handoff는 직접 말하지 않는다. | P3 기준의 architecture/implementation/test/source audit/workflow 경계 명확성 보강이 필요하다. |
| `implementation-django` risky-write wording overlap | 외부 follow-up | `implementation-django` runtime rule은 DB/API/test details까지 포함한 broad consistency block을 요구한다. Target skill은 pattern decision만 소유하고 concrete DB/API/test detail을 handoff한다. | Neighboring skill의 wording overlap이며, 이번 P3의 수정 범위인 target skill 내부 변경으로는 직접 수정하지 않는다. Target skill의 handoff를 더 명확히 해 충돌 가능성을 낮춘다. |
| plugin eval provisional case stale | 외부 follow-up | Source reference는 dedicated reference이고 provisional/fallback claim을 금지한다. 독립 리뷰는 일부 plugin eval material이 stale provisional expectation을 가질 수 있다고 보고했다. | Skill/source/runtime 기준으로는 current target이 맞다. Eval pack 수정은 이번 P3 target과 명시 수정 범위 밖이므로 본 skill을 provisional 방향으로 되돌리지 않는다. |

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real-subagent 두 개를 사용했다. 하나는 skill-creator 관점으로 progressive disclosure, metadata, validation integrity를 확인했고, 다른 하나는 독립 P3 boundary 관점으로 neighboring skill overlap과 cache parity를 확인했다.

skill-creator 리뷰: `SKILL.md` purpose/trigger, one-level bundled reference, metadata alignment는 적절하다고 판단했다. 다만 concrete implementation handoff가 source table보다 약하다는 Minor를 제시했다. Plugin eval provisional case stale은 target skill 수정으로 해결할 문제가 아니라 외부 eval follow-up으로 분류한다.

초기 리뷰 결과: Blocker 0, Major 0, 열린 Minor 2

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

## 수정 판단

Target `SKILL.md` routing에 다음 두 가지를 좁게 반영한다.

- Concrete implementation handoff를 `implementation-django`, `implementation-django-ninja`, `implementation-django-web`, `implementation-python`, `implementation-test`로 명시한다.
- Source/reference governance, metadata, runtime cache sync, leakage, validation coverage, eval traceability 감사는 `source-reference-audit`로 넘긴다.

Bundled references는 이미 source reference의 세부 기준을 나눠 담고 있고, `SKILL.md`와 중복을 만들 정도로 같은 표를 복제하지 않으므로 수정하지 않는다.

## 재평가 기준

- `SKILL.md`가 500줄 미만을 유지한다.
- Runtime routing에서 architecture, implementation, test, source audit, workflow 책임 경계가 명시된다.
- Source reference 또는 bundled reference를 더 깊은 경로로 숨기지 않는다.
- Source skill과 runtime cache가 동일하다.
- 독립 리뷰의 target-skill Minor가 닫히고 외부 follow-up은 이번 target의 열린 Minor로 남기지 않는다.

## 재평가 결과

- `SKILL.md` routing에 concrete implementation handoff target과 `source-reference-audit` handoff를 명시했다.
- `SKILL.md`는 41줄로 500줄 미만이다.
- Bundled references는 모두 `SKILL.md`에서 1단계 직접 링크로 발견 가능하다.
- Source skill과 runtime cache는 `diff -qr` 출력 없이 동일하다.
- `implementation-django` risky-write wording overlap과 plugin eval provisional case stale은 target skill 내부 문제가 아니므로 이번 P3의 열린 Minor로 남기지 않는다.
