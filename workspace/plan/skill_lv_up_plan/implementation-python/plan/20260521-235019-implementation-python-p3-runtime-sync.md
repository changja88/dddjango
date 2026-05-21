# Implementation Python P3 Runtime Sync Plan

## 수정 이유

P3 source skill 수정 후 `dddjango/skills/implementation-python/SKILL.md`, `dddjango/skills/implementation-python/agents/openai.yaml`과 runtime cache가 달라졌다. Runtime에서 로드되는 skill이 source와 동일한 P3 책임 경계, handoff 기준, UI prompt를 사용하도록 cache를 동기화한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python/agents/openai.yaml`

## 수정하지 말아야 할 범위

- `dddjango/skills/implementation-python/references/*.md`는 이번 runtime-sync에서 변경하지 않는다.
- 다른 runtime skill cache는 수정하지 않는다.
- `workspace/reference/**`와 `workspace/develop/eval/**`는 수정하지 않는다.

## 작업 체크리스트

- [x] Source/cache diff를 확인한다.
- [x] Source `SKILL.md`와 `agents/openai.yaml`을 runtime cache 동일 경로에 동기화한다.
- [x] `diff -qr`로 source/cache parity를 재확인한다.

## 검증 명령

- `diff -qr dddjango/skills/implementation-python /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python`

## 완료 조건

- Source skill과 runtime cache가 동일하다.
- Runtime cache가 P3 수정 내용을 포함한다.
- 동기화 범위가 `implementation-python` runtime cache로 제한된다.
