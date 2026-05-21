수정 대상: runtime-sync

# architecture-api runtime cache 동기화 계획

## 수정 이유

`dddjango/skills/architecture-api/`의 P3 수정이 runtime cache에 반영되지 않았다. runtime cache가 stale하면 Codex가 source와 다른 skill 지침을 사용할 수 있다.

## 수정 범위

- 동기화 대상:
  - `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api/SKILL.md`
  - `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api/agents/openai.yaml`
- 변경하지 말아야 할 범위:
  - 다른 skill cache
  - source reference
  - eval pack

## 수정 절차

1. source skill 디렉터리를 runtime cache의 architecture-api skill 디렉터리로 복사한다.
2. `diff -qr`로 source와 runtime cache 차이가 없는지 확인한다.
3. 검증 명령을 실행해 plan/skill 문서 제약을 확인한다.

## 체크리스트

- [ ] runtime cache `SKILL.md`가 source와 같다.
- [ ] runtime cache `agents/openai.yaml`이 source와 같다.
- [ ] runtime cache bundled reference가 source와 같다.
- [ ] `diff -qr` 결과가 비어 있다.

## 검증 명령

```bash
diff -qr dddjango/skills/architecture-api /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api
```

## 완료 조건

- source skill과 runtime cache가 byte-level directory comparison에서 일치한다.
- 최종 P3 검증 명령이 통과한다.
