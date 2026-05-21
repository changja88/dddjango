# architecture-ddd P3 runtime sync 계획

## 수정 이유

P3 skill handoff 수정이 source skill에만 반영되어 runtime cache와 차이가 발생했다. runtime cache가 source skill과 다르면 실제 Codex runtime에서 개선된 handoff 기준을 사용할 수 없으므로 cache parity를 맞춘다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd/SKILL.md`

## 수정하지 말아야 할 범위

- source skill은 이미 수정됐으므로 cache sync 과정에서 추가 변경하지 않는다.
- `agents/openai.yaml`과 bundled references는 이번 P3에서 변경하지 않았으므로 불필요하게 복사하지 않는다.
- 다른 runtime skill cache는 수정하지 않는다.

## 작업 체크리스트

- [x] source `SKILL.md`를 runtime cache `SKILL.md`로 복사한다.
- [x] `diff -qr`로 source/runtime cache parity를 확인한다.
- [x] 검증 결과를 분석 문서와 최종 보고에 반영한다.

## 검증 명령

```bash
diff -qr dddjango/skills/architecture-ddd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd
```

## 완료 조건

- source `architecture-ddd` skill과 runtime cache 사이에 차이가 없다.
- runtime-sync 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
