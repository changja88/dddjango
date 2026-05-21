수정 대상: runtime-sync

# implementation-python P2 runtime sync 계획

## 수정 이유

P2 skill 수정 후 source skill과 runtime cache가 다르다. 종료 조건은 source skill과 runtime cache 동기화를 요구하므로, source를 기준으로 runtime cache를 좁게 맞춘다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python/agents/openai.yaml`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python/references/*.md`

## 수정하지 말아야 할 범위

- 다른 runtime skill cache는 수정하지 않는다.
- source reference, eval pack, validators는 수정하지 않는다.
- source에 없는 runtime-only 파일을 추가하지 않는다.

## 작업 체크리스트

- [x] source `SKILL.md`를 runtime cache `SKILL.md`로 복사한다.
- [x] source `agents/openai.yaml`을 runtime cache `agents/openai.yaml`로 복사한다.
- [x] source `references/*.md`를 runtime cache `references/*.md`로 복사한다.
- [x] `diff -qr`로 source/runtime parity를 확인한다.
- [x] validators를 실행한다.

## 검증 명령

- `diff -qr dddjango/skills/implementation-python /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- source skill과 runtime cache가 같은 내용을 가진다.
- P2 종료 검증 명령이 통과한다.
- 리뷰 통합 결과가 Blocker 0, Major 0, 열린 Minor 0이다.

## 완료 확인

- source skill을 runtime cache에 동기화했다.
- `diff -qr dddjango/skills/implementation-python /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python` 결과 차이가 없다.
- P2 종료 검증 명령을 실행해 통과를 확인했다.
