# Implementation Django Ninja P3 Runtime Sync Plan

## 수정 이유

P3 source skill 수정 후 runtime cache의 `SKILL.md`, `auth-pagination-filtering.md`, `problem-details-openapi.md`가 source와 달라졌다. runtime cache를 source canonical skill과 동기화해야 실제 런타임에서 책임 경계와 handoff 수정이 반영된다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-ninja/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-ninja/references/auth-pagination-filtering.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-ninja/references/problem-details-openapi.md`

## 수정하지 말아야 할 범위

- Runtime cache의 다른 skill과 다른 reference는 수정하지 않는다.
- `agents/openai.yaml`, `router-schema.md`, `testclient.md`는 source 수정이 없으므로 덮어쓰지 않는다.
- Source reference와 eval artifact는 수정하지 않는다.

## 작업 체크리스트

- [x] Source `SKILL.md`를 runtime cache `SKILL.md`로 복사한다.
- [x] Source `references/auth-pagination-filtering.md`를 runtime cache 같은 경로로 복사한다.
- [x] Source `references/problem-details-openapi.md`를 runtime cache 같은 경로로 복사한다.
- [x] 독립 P3 boundary review 후 추가된 `source-reference-audit` handoff를 runtime cache에 재동기화한다.
- [x] `diff -qr`로 source/runtime cache parity를 확인한다.
- [x] Required validation command를 실행한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-django-ninja /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-ninja`

## 완료 조건

- Runtime cache가 source skill과 동일하다.
- 검증 명령이 통과한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.

## 완료 결과

- Runtime cache sync를 완료했다.
- Target source/runtime `diff -qr`는 통과했다.
- Required validators 중 global plan/skill validators는 unrelated current-worktree findings 때문에 실패했다.
