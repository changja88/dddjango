# implementation-test P3 Skill Plan

## 수정 이유

P3 기준은 skill 간 책임 경계와 handoff가 겹치지 않고, `SKILL.md`는 핵심 절차와 routing만 담으며, 세부 자료는 bundled reference로 필요한 때 로딩되도록 요구한다. 현재 구조는 대체로 충분하지만 API 관련 metadata 표현이 계약 설계와 test mechanics를 약하게 분리하고, source/reference governance handoff가 누락되어 있으며, pytest-bdd reference 안에 작은 중복이 있다.

## 수정 범위

- `dddjango/skills/implementation-test/SKILL.md`
- `dddjango/skills/implementation-test/agents/openai.yaml`
- `dddjango/skills/implementation-test/references/factories-property-tests.md`
- source 수정 후 필요한 runtime cache `implementation-test` 동기화

## 수정하지 말아야 할 범위

- `workspace/reference/implementation-test/**`는 source gap으로 판정하지 않았으므로 수정하지 않는다.
- `workspace/scripts/**` validator hook 추가는 이번 P3의 skill-only 수정 범위를 벗어나므로 수정하지 않는다.
- 다른 skill의 책임 문구는 현재 reciprocal boundary가 충분하므로 수정하지 않는다.
- eval pack, answer oracle, generated run artifact는 수정하지 않는다.

## 작업 체크리스트

- [x] `SKILL.md` frontmatter의 API wording을 test mechanics 중심으로 좁힌다.
- [x] `SKILL.md` Routing에 `source-reference-audit` handoff를 추가한다.
- [x] `SKILL.md` Runtime Rules에서 risky write tests가 이미 결정된 invariant/API/DB criteria를 검증한다는 경계를 명확히 한다.
- [x] `agents/openai.yaml`의 `short_description`과 `default_prompt`를 API contract test wording으로 좁힌다.
- [x] `factories-property-tests.md`의 pytest-bdd Given/When/Then 중복을 제거한다.
- [x] source 수정 뒤 runtime-sync 분석/계획을 작성하고 runtime cache를 동기화한다.
- [x] `diff -qr`로 source/runtime sync를 확인한다.
- [x] required validators를 실행한다.
- [x] P3 재평가에서 Blocker 0, Major 0, 열린 Minor 0인지 확인한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-test /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test`

## 완료 조건

- 직접 책임과 handoff 기준이 `SKILL.md`와 metadata에서 충돌 없이 드러난다.
- API 계약 설계, DB/domain 결정, production implementation, TDD flow, source audit가 `implementation-test` 책임과 분리된다.
- `SKILL.md`는 500줄 미만이고 bundled references는 1단계 직접 링크로 발견 가능하다.
- 불필요한 중복과 깊은 reference 연결이 없다.
- Runtime cache와 source skill이 일치한다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.

## 검증 결과

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`: 통과, `OK: plan constraints passed`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`: 통과, 23 tests OK
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: 통과, `OK: validation passed with 0 warning(s)`
- `diff -qr dddjango/skills/implementation-test /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test`: 통과, 출력 없음

## 리뷰 결과

- Pre-edit real-subagent review: Blocker 0, Major 0, Minor 2.
- Post-edit real-subagent review: Blocker 0, Major 0, Minor 1. `Django TestClient` wording ambiguity를 보고했고 `Django Ninja TestClient`로 수정했다.
- 최종 재평가: Blocker 0, Major 0, 열린 Minor 0.
