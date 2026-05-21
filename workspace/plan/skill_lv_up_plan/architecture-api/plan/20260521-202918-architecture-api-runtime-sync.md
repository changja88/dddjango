# Architecture API Runtime Sync Plan

## 수정 이유

Source skill 변경으로 runtime cache와 차이가 발생했다. P1 종료 조건은 source skill과 runtime cache 동기화 확인을 요구하므로 변경된 세 파일을 cache에 반영한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api/agents/openai.yaml`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api/references/rest-contracts.md`

## 수정하지 말아야 할 범위

- Runtime cache의 다른 skill은 수정하지 않는다.
- Source skill에 없는 내용을 runtime cache에 직접 추가하지 않는다.
- Eval artifacts는 수정하지 않는다.

## 작업 체크리스트

- [x] source skill의 변경된 세 파일을 runtime cache에 복사한다.
- [x] `diff -qr dddjango/skills/architecture-api /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api`가 차이 없음으로 끝나는지 확인한다.
- [x] validator를 실행한다.

## 완료 결과

- Source skill과 runtime cache는 `diff -qr` 기준 차이가 없다.
- 검증 명령은 모두 통과했다.

## 검증 명령

- `diff -qr dddjango/skills/architecture-api /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Source skill과 runtime cache가 파일 단위로 동일하다.
- 검증 명령이 통과한다.
