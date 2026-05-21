# Architecture API P1 Skill Plan

## 수정 이유

Reference 보강 후 architecture-api skill이 P1의 request/response contract와 metadata coverage를 더 직접적으로 반영하게 만든다. 변경은 progressive disclosure를 유지하면서 runtime에서 필요한 선택 기준을 빠르게 찾게 하는 데 한정한다.

## 수정 범위

- `dddjango/skills/architecture-api/SKILL.md`
- `dddjango/skills/architecture-api/references/rest-contracts.md`
- `dddjango/skills/architecture-api/agents/openai.yaml`

## 수정하지 말아야 할 범위

- `dddjango/skills/architecture-api/references/problem-details.md`, `pagination-versioning.md`, `idempotency-openapi.md`는 source reference 보강 후 unsupported claim 여부만 확인하고 불필요하면 수정하지 않는다.
- Runtime cache는 source skill 수정 완료 후 별도 runtime-sync 계획으로 동기화한다.
- eval materials는 수정하지 않는다.

## 작업 체크리스트

- [x] `SKILL.md` reference loading에서 request/response contract를 `rest-contracts.md` 범위로 명시한다.
- [x] `SKILL.md` runtime rules에 request/response body/header/status 조합을 계약으로 기록하도록 보강한다.
- [x] `rest-contracts.md`에 request/response contract section을 추가한다.
- [x] `rest-contracts.md`에 content negotiation q-value와 specificity priority 기준을 추가한다.
- [x] `agents/openai.yaml`의 short/default prompt에 resource/URL/status/version/rate-limit/idempotency 신호를 보강한다.
- [x] source skill과 runtime cache diff를 확인한다.

## 완료 결과

- Skill 관련 Blocker 0, Major 0, 열린 Minor 0으로 재평가했다.
- Runtime cache sync까지 완료했다.
- 검증 명령은 모두 통과했다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Skill이 source reference의 API contract 기준을 충분히 반영한다.
- Bundled references와 `agents/openai.yaml`이 skill 목적과 충돌하지 않는다.
- skill-creator 관점 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
