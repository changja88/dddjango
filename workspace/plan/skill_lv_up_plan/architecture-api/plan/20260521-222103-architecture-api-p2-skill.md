# Architecture API P2 Skill Plan

## 수정 이유

P2 리뷰에서 `architecture-api` skill의 core 목적은 적절하지만, source reference와 runtime skill 사이에 HTTPS 보안 지침 강도 차이가 있고, 일부 trigger와 제외 조건이 frontmatter보다 본문에 더 강하게 드러나는 문제가 확인됐다. `agents/openai.yaml`도 `SKILL.md`의 request/response contract, content negotiation, deprecation 축을 더 직접적으로 반영해야 한다.

## 수정 범위

- `dddjango/skills/architecture-api/SKILL.md`
- `dddjango/skills/architecture-api/references/rest-contracts.md`
- `dddjango/skills/architecture-api/agents/openai.yaml`
- Source 수정 후 runtime cache 동기화: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api/`

## 수정하지 말아야 할 범위

- `workspace/reference/architecture-api/**`는 수정하지 않는다.
- `workspace/develop/eval/**`는 수정하지 않는다.
- `dddjango/skills/architecture-api/references/problem-details.md`, `pagination-versioning.md`, `idempotency-openapi.md`는 이번 finding과 직접 관련이 없으면 수정하지 않는다.
- `agents/openai.yaml`에 optional interface field를 새로 추가하지 않는다.

## 작업 체크리스트

- [x] `SKILL.md` frontmatter에 workflow/subagent 한국어 trigger와 non-REST 제외 조건을 반영한다.
- [x] `SKILL.md` routing 본문에 non-REST style과 gateway/HATEOAS 범위를 다른 skill 또는 일반 답변 대상으로 분리하라고 명시한다.
- [x] `rest-contracts.md`의 HTTPS 지침을 모든 API 통신에 적용되도록 source reference와 맞춘다.
- [x] `agents/openai.yaml` default prompt에 request/response contracts, content negotiation, deprecation을 반영한다.
- [x] Source skill 수정 후 runtime cache를 동일 내용으로 동기화한다.
- [x] 동일 P2 기준으로 재평가해 Blocker 0, Major 0, 열린 Minor 0인지 확인한다.

## 완료 결과

- P2 수정과 runtime cache sync를 완료했다.
- Architecture-api source/runtime diff와 plan validator는 통과했다.
- Required global skill validator는 통과했다.
- 최종 리뷰 결과는 Blocker 0, Major 0, 열린 Minor 0이다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/architecture-api /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api`

## 완료 조건

- `SKILL.md` 목적, trigger, 제외 조건이 frontmatter와 본문에서 충돌 없이 드러난다.
- Source reference의 HTTPS 보안 지침이 bundled runtime reference에서 약화되지 않는다.
- `agents/openai.yaml`이 `SKILL.md`의 주요 API 계약 범위를 덜거나 과장하지 않는다.
- Source skill과 runtime cache가 `diff -qr` 기준 동일하다.
- 검증 명령이 통과한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
