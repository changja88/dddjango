# implementation-tdd P2 runtime sync 계획

## 수정 이유

source skill의 P2 수정 사항이 runtime cache에 반영되어야 Codex runtime이 source와 같은 skill 내용을 사용한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/agents/openai.yaml`

## 수정하지 말아야 할 범위

- 다른 runtime cache skill은 수정하지 않는다.
- source reference와 bundled references는 이번 sync에서 수정하지 않는다.
- optional `openai.yaml` fields를 추가하지 않는다.

## 체크리스트

- [x] source `SKILL.md` 변경분을 runtime cache에 반영한다.
- [x] source `agents/openai.yaml` 변경분을 runtime cache에 반영한다.
- [x] `diff -qr`로 parity를 확인한다.

## 검증 명령

```bash
diff -qr dddjango/skills/implementation-tdd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd
```

## 완료 조건

- source skill과 runtime cache skill의 recursive diff가 없다.
