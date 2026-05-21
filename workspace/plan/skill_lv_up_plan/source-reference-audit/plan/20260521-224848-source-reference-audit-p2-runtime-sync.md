# source-reference-audit P2 runtime sync 계획

## 수정 이유

P2 skill 수정으로 source skill과 runtime cache가 달라졌다. 목표 종료 조건은 source skill과 runtime cache가 같은 내용을 가리키는지 확인하라고 요구하므로 cache sync가 필요하다.

## 수정 범위

- `dddjango/skills/source-reference-audit/SKILL.md` 내용을 runtime cache `SKILL.md`에 반영한다.
- `dddjango/skills/source-reference-audit/agents/openai.yaml` 내용을 runtime cache `agents/openai.yaml`에 반영한다.
- `dddjango/skills/source-reference-audit/references/source-governance.md` 내용을 runtime cache `references/source-governance.md`에 반영한다.

## 수정하지 말아야 할 범위

- 다른 runtime cache skill은 수정하지 않는다.
- source skill의 추가 리팩터링은 하지 않는다.
- source reference와 eval pack은 수정하지 않는다.

## 작업 체크리스트

- [x] source `SKILL.md`를 runtime cache `SKILL.md`로 동기화한다.
- [x] source `agents/openai.yaml`을 runtime cache `agents/openai.yaml`로 동기화한다.
- [x] source `references/source-governance.md`를 runtime cache로 동기화한다.
- [x] `diff -qr`로 source/runtime cache parity를 확인한다.
- [x] validators를 실행한다.

## 검증 명령

```bash
diff -qr dddjango/skills/source-reference-audit /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
```

## 완료 조건

- source skill과 runtime cache가 diff 없이 일치한다.
- runtime cache에는 P2에서 수정한 frontmatter description과 default_prompt가 반영되어 있다.
- 검증 명령이 통과한다.
- runtime-sync 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
