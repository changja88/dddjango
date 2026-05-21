# source-reference-audit P1 runtime sync 계획

## 수정 이유

Source skill을 수정한 뒤 runtime cache가 stale이면 Codex runtime은 개선된 `source-reference-audit` 지침을 사용하지 못한다. P1 종료 조건은 source skill과 runtime cache sync 확인을 요구한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit/agents/openai.yaml`

## 수정하지 말아야 할 범위

- 다른 cached skill은 수정하지 않는다.
- Source reference를 runtime cache에 복사하지 않는다.
- Runtime cache에 source skill과 다른 별도 수정은 넣지 않는다.

## 작업 체크리스트

- [x] source `SKILL.md`를 runtime cache `SKILL.md`로 복사한다.
- [x] source `agents/openai.yaml`을 runtime cache `agents/openai.yaml`로 복사한다.
- [x] source skill directory와 runtime cache directory의 diff를 확인한다.
- [x] validators를 실행한다.

## 검증 명령

```bash
diff -ru dddjango/skills/source-reference-audit /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
```

## 완료 조건

- source skill과 runtime cache가 파일 단위로 동일하다.
- validators가 통과한다.
- runtime sync 관련 Blocker 0, Major 0, 열린 Minor 0이다.
