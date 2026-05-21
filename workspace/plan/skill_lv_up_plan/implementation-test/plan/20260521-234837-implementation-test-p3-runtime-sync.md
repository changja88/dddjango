# implementation-test P3 Runtime Sync Plan

## 수정 이유

P3 source skill 수정 뒤 runtime cache가 달라졌다. 종료 조건에는 source skill과 runtime cache 동기화 확인이 포함되므로 cache를 source와 맞춰야 한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test/agents/openai.yaml`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test/references/factories-property-tests.md`

## 수정하지 말아야 할 범위

- 다른 runtime skill cache는 수정하지 않는다.
- source reference, eval pack, validator는 수정하지 않는다.
- runtime cache에 source-authoring plan이나 analysis 문서를 복사하지 않는다.

## 작업 체크리스트

- [x] source skill의 변경 파일 3개를 runtime cache에 복사한다.
- [x] post-edit metadata 보정 파일을 runtime cache에 다시 복사한다.
- [x] `diff -qr`로 source/runtime sync를 확인한다.
- [x] required validators를 실행한다.

## 검증 명령

- `diff -qr dddjango/skills/implementation-test /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- `diff -qr` 출력이 없다.
- P3 skill analysis에서 확인한 열린 Minor가 cache drift 때문에 재발하지 않는다.

## 검증 결과

- `diff -qr dddjango/skills/implementation-test /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test`: 통과, 출력 없음
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`: 통과, `OK: plan constraints passed`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`: 통과, 23 tests OK
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: 통과, `OK: validation passed with 0 warning(s)`
