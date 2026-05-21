# implementation-tdd P3 runtime cache sync 계획

## 수정 이유

P3 skill 수정으로 source skill과 runtime cache가 달라진다. Codex 런타임이 사용하는 cache가 source와 다르면 사용자가 수정 결과를 즉시 사용할 수 없고, P3 종료 조건의 source/runtime cache 동기화도 충족하지 못한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/agents/openai.yaml`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/references/bdd-atdd.md`

## 수정하지 말아야 할 범위

- 다른 skill cache는 수정하지 않는다.
- 기존 runtime cache reference 파일은 source reference 파일이 바뀌지 않았으므로 임의로 다시 작성하지 않는다.
- source skill 외부의 package metadata는 수정하지 않는다.

## 체크리스트

- [ ] source `SKILL.md`를 runtime cache `SKILL.md`에 복사한다.
- [ ] source `agents/openai.yaml`을 runtime cache `agents/openai.yaml`에 복사한다.
- [ ] source `references/bdd-atdd.md`를 runtime cache `references/bdd-atdd.md`에 복사한다.
- [ ] `diff -qr`로 source/cache parity를 확인한다.
- [ ] skill docs validator를 실행해 runtime cache phase까지 확인한다.

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
diff -qr dddjango/skills/implementation-tdd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd
```

## 완료 조건

- source skill과 runtime cache 사이에 `diff -qr` 차이가 없다.
- 필수 skill docs 검증이 통과한다.
