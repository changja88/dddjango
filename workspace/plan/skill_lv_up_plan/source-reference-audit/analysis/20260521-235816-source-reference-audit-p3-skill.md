수정 대상: skill
원인 분류: p3-boundary-progressive-disclosure-gap
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 2

# source-reference-audit P3 skill 분석

## 평가 범위

- Source skill: `dddjango/skills/source-reference-audit/SKILL.md`
- UI metadata: `dddjango/skills/source-reference-audit/agents/openai.yaml`
- Bundled reference: `dddjango/skills/source-reference-audit/references/source-governance.md`
- Source reference: `workspace/reference/source-reference-audit/reference/final.md`
- Runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit/`
- Neighbor handoff evidence: architecture, implementation, test, workflow skill `SKILL.md` files

## P3 초기 판정

| 기준 | 판정 | 근거 |
|---|---|---|
| 직접 책임 | 충분 | `SKILL.md`는 source/reference governance, provenance, source gap, runtime metadata/cache sync, leakage, validation coverage boundary, eval traceability boundary를 직접 책임으로 둔다. |
| handoff 기준 | 부분 부족 | 실제 DDD/API/DB/Django/Python/test/workflow 설계와 구현은 다른 skill로 넘기지만, frontmatter의 `validation coverage`, `eval traceability` 표현이 일반 테스트 coverage/eval 작업까지 과하게 trigger할 수 있다. |
| skill 간 책임 충돌 | 열린 Minor | 본문과 `agents/openai.yaml`은 eval traceability와 validation coverage를 explicit/requested governance scope로 제한하지만, frontmatter description은 같은 제한을 충분히 드러내지 않는다. |
| progressive disclosure | 열린 Minor | `SKILL.md`는 101줄로 짧고 bundled reference는 1단계 직접 링크지만, bundled reference를 기본 로딩처럼 지시하고 일부 세부 규칙이 `SKILL.md`와 reference에 중복되어 drift risk가 있다. |
| reference 발견성 | 충분 | `references/source-governance.md`는 `SKILL.md`에서 직접 링크되며 nested reference가 없다. |
| source reference 충분성 | 충분 | source reference는 role/path boundary, provenance, source gap/provisional, DRF guardrail, leakage, validation coverage, eval traceability, runtime metadata/cache sync를 다룬다. source reference 후속 수정은 필요 없다. |
| runtime cache sync | 충분 | 초기 `diff -qr` 결과 source skill과 runtime cache는 일치했다. source 수정 뒤 별도 runtime-sync 루프가 필요하다. |

## Subagent 리뷰/순차 fallback

Subagent 리뷰/순차 fallback: real-subagent.

- skill-creator 관점 subagent: Blocker 0, Major 0, Minor 2. Frontmatter의 validation/eval trigger가 과하게 넓고, bundled reference가 기본 로딩처럼 되어 progressive disclosure가 약하다고 보고했다.
- 독립 P3 audit subagent: Blocker 0, Major 0, Minor 2. 일부 neighboring skill의 reverse handoff가 빠졌고, `SKILL.md`와 bundled reference 사이에 세부 정책 중복이 있다고 보고했다.
- Main 통합 판단: frontmatter over-trigger와 bundled reference 기본 로딩/중복은 target skill의 열린 Minor로 채택한다. Neighboring skill reverse handoff는 유용한 후속 관찰이지만 이번 목표의 수정 범위가 `source-reference-audit/**`이고, source-reference-audit 자체의 outward handoff는 충분하므로 target skill의 열린 문제로 남기지 않는다.

## skill-creator 리뷰

- 목적 명확성: 충분. source/reference evidence와 runtime boundary audit 목적은 명확하다.
- trigger description: validation coverage/eval traceability는 source/reference governance 범위와 explicit request 조건을 frontmatter에서 더 분명히 해야 한다.
- progressive disclosure: `SKILL.md`는 500줄 미만이며 reference는 1단계 직접 링크다. 다만 source-governance reference는 필요할 때 읽도록 gating을 좁혀야 한다.
- reference 중복/누락: validator가 요구하는 핵심 boundary 문구는 `SKILL.md`에 남겨야 하지만, 상세 decision source는 bundled reference로 안내하고 `SKILL.md`에서는 반복을 최소화해야 한다.
- validation integrity: 실제 실행한 validation, diff, review만 보고하라는 규칙은 유지되어야 한다.

## 수정 방향

- `SKILL.md` frontmatter에서 validation coverage와 eval traceability를 source/reference governance, boundary, explicit eval-pack review 맥락으로 제한한다.
- Routing에서 일반 test coverage, eval 실행/평가, application behavior 설계/구현은 owning skill 또는 workflow로 넘긴다는 handoff를 명확히 한다.
- Source Loading에서 `source-governance.md`를 항상 읽는 지시가 아니라 boundary/provenance/gap/leakage/metadata/cache/eval-traceability 세부 판단이 필요할 때 읽는 bundled reference로 바꾼다.
- `SKILL.md`와 `source-governance.md`의 중복은 validator-required 핵심 문구 수준으로 제한하고, 세부 source decision은 bundled reference를 decision summary로 가리킨다.
- `agents/openai.yaml` default prompt는 이미 conditional wording을 담고 있으므로 source 수정 후 의미상 일치 여부만 재확인한다.

## 수정하지 말아야 할 범위

- `workspace/reference/source-reference-audit/**`는 source gap이 아니므로 수정하지 않는다.
- Neighboring skill reverse handoff 보강은 이번 source-reference-audit target skill의 좁은 수정 범위를 벗어나므로 수정하지 않는다.
- `workspace/scripts/**`, eval pack, 다른 skill은 수정하지 않는다.
- Runtime cache는 source 수정 후 차이가 생길 때 별도 runtime-sync 분석/계획을 작성한 뒤 동기화한다.

## 재평가 기준

- 직접 책임과 handoff 기준이 frontmatter, Routing, Source Loading에서 충돌하지 않아야 한다.
- `validation coverage`와 `eval traceability`가 일반 test/eval 작업이 아니라 source/reference governance 또는 explicit eval-pack audit 맥락으로 제한되어야 한다.
- `SKILL.md`는 500줄 미만이고 bundled reference는 1단계 직접 링크로 발견 가능해야 한다.
- Bundled reference는 필요할 때 로딩되는 세부 decision summary여야 하며, `SKILL.md`와 불필요한 중복을 만들지 않아야 한다.
- Source skill과 runtime cache가 동기화되어야 한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이어야 한다.

## 최종 재평가

P3 수정 후 real-subagent post-edit 리뷰 2개를 실행했다.

- skill-creator 관점 post-edit review: 이전 frontmatter over-trigger, progressive disclosure, responsibility boundary 우려가 닫혔다고 판정했다. Blocker 0, Major 0, 열린 Minor 0.
- 독립 P3 post-edit review: 직접 책임/handoff, role overlap, `SKILL.md` 500줄 미만, one-level bundled reference, 조건부 reference loading, source/runtime cache parity를 통과로 판정했다. Blocker 0, Major 0, 열린 Minor 0.

최종 target-scope 판단:

- `SKILL.md` frontmatter와 Routing은 validation coverage/eval traceability를 source evidence, review scope, explicit internal eval-pack traceability로 제한한다.
- 실제 DDD/API/DB/Django/Python/test/workflow 설계, 구현, 테스트 mechanics, eval 실행, evaluator 구현은 owning skill 또는 process로 넘긴다.
- `source-governance.md`는 `SKILL.md`에서 1단계 직접 링크되고, 필요한 세부 source-governance decision이 있을 때 읽는 bundled reference로 gate가 조정됐다.
- `SKILL.md`는 102줄로 500줄 미만이다.
- Neighboring skill reverse handoff 보강은 유용한 후속 관찰이지만, 이번 target skill의 outward handoff가 충분하고 objective의 수정 범위가 `dddjango/skills/source-reference-audit/**`이므로 열린 target-scope Minor로 남기지 않는다.
- Source reference 자체는 role/path boundary, provenance, source gap/provisional, DRF guardrail, leakage, validation coverage, eval traceability, runtime metadata/cache sync를 이미 다루므로 후속 reference 분석은 작성하지 않는다.

최종 판정:

- Blocker 0
- Major 0
- 열린 Minor 0

검증 evidence:

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`: 통과.
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`: 통과.
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: 통과.
- `diff -qr dddjango/skills/source-reference-audit /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit`: 출력 없음.
