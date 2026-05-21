수정 대상: runtime-sync

# implementation-django runtime cache 동기화 계획

## 수정 이유

runtime cache는 실제 Codex plugin runtime에서 사용되는 skill 사본이다. source skill을 수정한 뒤 cache를 동기화하지 않으면 P3 종료 조건인 source/runtime parity를 만족할 수 없다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django/agents/openai.yaml`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django/references/models-orm.md`

## 수정하지 말아야 할 범위

- 다른 runtime skill cache는 수정하지 않는다.
- source reference와 다른 skill은 수정하지 않는다.
- runtime cache에 분석/계획 문서를 추가하지 않는다.

## 체크리스트

- [x] source `SKILL.md`를 runtime cache에 반영한다.
- [x] source `agents/openai.yaml`를 runtime cache에 반영한다.
- [x] source `references/models-orm.md`를 runtime cache에 반영한다.
- [x] `diff -qr`로 source/runtime parity를 확인한다.

## 검증 명령

```bash
diff -qr dddjango/skills/implementation-django /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django
```

## 완료 조건

- `diff -qr` 출력이 없다.
