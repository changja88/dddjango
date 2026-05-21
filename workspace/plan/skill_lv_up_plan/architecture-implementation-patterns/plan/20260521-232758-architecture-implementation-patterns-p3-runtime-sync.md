수정 대상: runtime-sync

# architecture-implementation-patterns P3 runtime-sync 계획

## 수정 이유

Source skill routing을 P3 기준에 맞게 보강하면서 runtime cache와 차이가 생겼다. Runtime cache는 Codex 플러그인 실행 표면이므로 source와 동일해야 한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-implementation-patterns/SKILL.md`

## 수정하지 말아야 할 범위

- Runtime cache의 bundled references와 `agents/openai.yaml`은 source와 차이가 없으므로 수정하지 않는다.
- Source reference, eval pack, validator는 수정하지 않는다.
- Runtime cache에 source에 없는 별도 내용을 추가하지 않는다.

## 작업 체크리스트

- [ ] Source `SKILL.md`를 runtime cache `SKILL.md`로 복사한다.
- [ ] `diff -qr`로 source/runtime cache 전체가 동일한지 확인한다.
- [ ] Plan constraint validator와 skill docs validator를 실행한다.
- [ ] Runtime-sync 관련 열린 Blocker, Major, Minor가 없는지 확인한다.

## 검증 명령

- `diff -qr dddjango/skills/architecture-implementation-patterns /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-implementation-patterns`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Source skill과 runtime cache skill이 동일하다.
- 검증 명령 결과를 실제 출력 기준으로 보고한다.
- Runtime-sync 관련 열린 Blocker, Major, Minor가 없다.
