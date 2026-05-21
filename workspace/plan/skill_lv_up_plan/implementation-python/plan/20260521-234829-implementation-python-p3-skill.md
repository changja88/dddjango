# Implementation Python P3 Skill Plan

## 수정 이유

P3 평가에서 `implementation-python` skill의 progressive disclosure 구조와 대부분의 handoff는 적절했지만, source/reference governance handoff, API/DB 결정 owner 분리, repository/UoW/ports/outbox pattern decision handoff, Clean Code function-shape handoff가 충분히 직접 드러나지 않았다. 이 skill을 Python 언어 계층의 contract 표현과 implementation mechanics로 좁히고, source audit, architecture decision, maintainability refactor 판단은 소유 skill로 넘기도록 routing을 보강한다.

## 수정 범위

- `dddjango/skills/implementation-python/SKILL.md`
- `dddjango/skills/implementation-python/agents/openai.yaml`
- Source 수정 후 runtime cache sync 필요 여부 확인

## 수정하지 말아야 할 범위

- `workspace/reference/implementation-python/**`는 수정하지 않는다.
- `dddjango/skills/implementation-python/references/*.md`는 새 P3 finding 없이는 수정하지 않는다.
- 다른 skill과 reference는 수정하지 않는다.
- `workspace/develop/eval/**`는 수정하지 않는다.

## 작업 체크리스트

- [x] `SKILL.md` frontmatter에 `source-reference-audit` handoff를 추가한다.
- [x] `SKILL.md` frontmatter에 `architecture-implementation-patterns` handoff를 추가한다.
- [x] Routing에 source/reference governance, provenance, bundled reference parity, runtime cache sync audit, leakage/boundary review는 `source-reference-audit` 책임이라고 추가한다.
- [x] REST/API contract handoff와 DB schema/transaction/locking/rollout handoff를 별도 bullet로 분리한다.
- [x] repository/UoW/ports/outbox/service-layer pattern decision은 `architecture-implementation-patterns` 책임이고, 이 skill은 선택된 boundary의 Python 표현만 맡는다고 명시한다.
- [x] function split, flag-argument 제거, responsibility separation 같은 maintainability refactor 판단은 `implementation-cleancode`가 맡고, 이 skill은 Python call-signature mechanics만 맡는다고 명시한다.
- [x] `agents/openai.yaml` default_prompt를 boundary-aware prompt로 좁힌다.
- [x] source reference의 broad source/runtime scope gap과 stale Repository/UoW fallback은 reference follow-up으로 분류한다.
- [x] Source 수정 후 runtime cache와 diff를 확인하고, 차이가 있으면 runtime-sync 분석/계획을 작성한 뒤 cache sync를 수행한다.
- [x] real subagent review 또는 sequential fallback review를 수행한다.
- [x] 검증 명령을 실행한다.
- [x] 동일 P3 기준으로 재평가해 Blocker 0, Major 0, 열린 Minor 0인지 확인한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-python /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python`

## 완료 조건

- Direct responsibility와 handoff 기준이 충돌 없이 드러난다.
- `source-reference-audit`, `architecture-ddd`, `architecture-api`, `architecture-db`, `architecture-implementation-patterns`, `implementation-django`, `implementation-django-ninja`, `implementation-cleancode`, `implementation-test`, `workflow-dddjango-subagents`와 역할이 겹치지 않는다.
- `SKILL.md`는 핵심 절차 중심이고 500줄 미만이다.
- Bundled references는 `SKILL.md`에서 1단계 직접 링크로 발견된다.
- Source skill과 runtime cache가 동기화된다.
- 검증 명령이 통과한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.

## 완료 결과

- P3 source skill 수정과 runtime cache sync를 완료했다.
- skill-creator 관점 real subagent review는 target skill 기준 Blocker 0, Major 0, Minor 0으로 종료했다.
- 독립 P3 boundary real subagent review는 수정 후 Blocker 0, Major 0, Minor 0으로 통합했다.
- Source reference scope/provenance gap은 `reference_lv_up_plan/implementation-python/analysis/20260521-235142-implementation-python-p3-reference.md`에 후속 분석으로 남겼다.
- Target source/runtime `diff -qr`는 통과했다.
- Required validators는 통과했다.
