# architecture-ddd runtime sync 계획

## 수정 이유

P1에서는 source skill과 runtime cache 동기화 여부까지 종료 조건에 포함한다. source skill을 수정한 뒤 runtime cache가 갱신되지 않으면 실제 Codex runtime은 수정 전 지침을 사용할 수 있다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd/references/tactical-patterns.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd/agents/openai.yaml`

## 수정하지 말아야 할 범위

- 다른 runtime skill cache는 수정하지 않는다.
- plugin manifest, eval pack, source reference는 runtime sync 작업에서 수정하지 않는다.

## 작업 체크리스트

- [x] source skill 수정 후 source/runtime diff를 확인한다.
- [x] 변경된 architecture-ddd runtime cache 파일만 source skill과 동일하게 갱신한다.
- [x] `diff -qr`로 source/runtime 차이가 없는지 재확인한다.
- [x] skill docs validator를 실행해 source skill 문서 구조를 확인한다.

## 검증 명령

```bash
diff -qr dddjango/skills/architecture-ddd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
```

## 완료 조건

- `diff -qr` 출력이 비어 있다.
- runtime cache가 source skill의 수정 내용을 그대로 반영한다.
- P1 재평가에서 runtime-sync 관련 열린 Minor가 없다.
