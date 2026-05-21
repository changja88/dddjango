# implementation-tdd P2 review-fix runtime sync 계획

## 수정 이유

source skill의 재평가 수정분을 runtime cache에 반영해야 runtime skill과 source skill이 같은 내용을 가리킨다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/SKILL.md`

## 수정하지 말아야 할 범위

- 다른 runtime cache skill은 수정하지 않는다.
- `agents/openai.yaml`과 bundled references는 이번 재평가 수정에서 변경하지 않았으나 source와 함께 recursive sync해 parity를 유지한다.

## 체크리스트

- [ ] source skill 폴더를 target runtime cache에 동기화한다.
- [ ] `diff -qr`로 parity를 확인한다.

## 검증 명령

```bash
diff -qr dddjango/skills/implementation-tdd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd
```

## 완료 조건

- `diff -qr`가 출력 없이 성공한다.
