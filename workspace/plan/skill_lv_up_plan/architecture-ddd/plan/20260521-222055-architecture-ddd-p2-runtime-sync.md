# architecture-ddd P2 runtime sync 계획

## 수정 이유

P2에서 source skill의 `SKILL.md` frontmatter와 `agents/openai.yaml` UI metadata를 수정했다. runtime cache가 source skill과 다르면 실제 Codex runtime에서는 이전 metadata가 사용될 수 있으므로 cache 동기화가 필요하다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd/agents/openai.yaml`

## 수정하지 말아야 할 범위

- runtime cache의 다른 skill은 수정하지 않는다.
- source reference, eval pack, validator는 수정하지 않는다.
- bundled references는 source에서 변경하지 않았으므로 runtime에서도 변경하지 않는다.

## 작업 체크리스트

- [x] source `SKILL.md`를 runtime cache에 반영한다.
- [x] source `agents/openai.yaml`을 runtime cache에 반영한다.
- [x] `diff -qr`로 source/cache parity를 확인한다.
- [x] 검증 명령과 리뷰 결과를 분석 문서에 반영한다.

## 검증 명령

```bash
diff -qr dddjango/skills/architecture-ddd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd
```

## 완료 조건

- source skill과 runtime cache의 `diff -qr` 출력이 비어 있다.
- runtime cache가 P2 source skill metadata와 같은 내용을 가리킨다.
