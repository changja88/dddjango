# Implementation Django Ninja P3 Skill Plan

## 수정 이유

P3 평가에서 `implementation-django-ninja` skill의 핵심 구조는 적절하지만, idempotency, rate limiting, versioning 관련 reference loading label과 bundled reference 표현이 `architecture-api`, `architecture-db`, `implementation-django`의 결정 책임과 겹쳐 보일 수 있었다. 이 skill의 책임을 이미 정해진 API/DB/domain 계약을 Django Ninja adapter에 연결하는 범위로 좁혀 표현한다.

## 수정 범위

- `dddjango/skills/implementation-django-ninja/SKILL.md`
- `dddjango/skills/implementation-django-ninja/references/auth-pagination-filtering.md`
- `dddjango/skills/implementation-django-ninja/references/problem-details-openapi.md`
- Source 수정 후 runtime cache sync 필요 여부 확인

## 수정하지 말아야 할 범위

- `workspace/reference/implementation-django-ninja/**`는 수정하지 않는다.
- `dddjango/skills/implementation-django-ninja/agents/openai.yaml`은 새 finding 없이는 수정하지 않는다.
- 다른 skill과 reference는 수정하지 않는다.
- `workspace/develop/eval/**`는 수정하지 않는다.

## 작업 체크리스트

- [x] `SKILL.md` Source 경계에 "이미 정해진 REST/DB/domain 계약을 Django Ninja adapter로 연결" 기준을 추가한다.
- [x] `SKILL.md` Reference Loading에서 rate-limit/versioning/idempotency 표현을 adapter wiring과 OpenAPI/error reflection 중심으로 좁힌다.
- [x] `auth-pagination-filtering.md`에서 rate limiting/versioning strategy 결정은 `architecture-api`로 넘기고, 이 reference는 기존 strategy 연결만 다룬다고 명시한다.
- [x] `problem-details-openapi.md`에서 idempotency behavior 결정과 storage/transaction 소유권은 외부 skill로 넘기고, 이 reference는 header binding, service handoff, Problem Details/OpenAPI 표시를 다룬다고 명시한다.
- [x] 독립 P3 boundary review에서 발견된 `source-reference-audit` handoff Minor를 `SKILL.md` Routing에 반영한다.
- [x] Source 수정 후 runtime cache와 diff를 확인하고, 차이가 있으면 runtime-sync 분석/계획을 작성한 뒤 cache sync를 수행한다.
- [x] real subagent review 또는 sequential fallback review를 수행한다.
- [x] 검증 명령을 실행한다.
- [x] 동일 P3 기준으로 재평가해 Blocker 0, Major 0, 열린 Minor 0인지 확인한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-django-ninja /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-ninja`

## 완료 조건

- Direct responsibility와 handoff 기준이 충돌 없이 드러난다.
- `architecture-api`, `architecture-db`, `implementation-django`, `implementation-test`, `workflow-dddjango-subagents`, `source-reference-audit`와 역할이 겹치지 않는다.
- `SKILL.md`는 핵심 절차 중심이고 500줄 미만이다.
- Bundled references는 `SKILL.md`에서 1단계 직접 링크로 발견된다.
- Source skill과 runtime cache가 동기화된다.
- 검증 명령이 통과한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.

## 완료 결과

- P3 source skill 수정과 runtime cache sync를 완료했다.
- skill-creator 관점 real subagent review는 target skill 기준 Blocker 0, Major 0, Minor 0으로 종료했다.
- 독립 P3 boundary real subagent review의 열린 Minor 1개를 수정했고, 재평가 결과 Blocker 0, Major 0, 열린 Minor 0이다.
- Target source/runtime `diff -qr`는 통과했다.
- Required validators 중 target source/runtime parity는 통과했지만, global validators는 unrelated current-worktree findings 때문에 실패했다.
