수정 대상: runtime-sync
원인 분류: source/runtime cache drift
작업 ID: 20260521-222104-architecture-db-p2-runtime-sync

## 평가 범위

- source skill: `dddjango/skills/architecture-db/`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db/`

## 현재 평가

P2 수정으로 source skill의 `SKILL.md`, `agents/openai.yaml`, `references/schema-modeling.md`가 runtime cache와 달라졌다. `diff -qr`가 세 파일의 drift를 보고한다. Source skill이 P2 기준을 만족해도 runtime cache가 stale이면 실제 runtime에서 같은 trigger/metadata/reference boundary를 사용하지 못한다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: P2 독립 subagent들은 수정 전 source/runtime parity가 clean하다고 보고했다. 현재 drift는 P2 source 수정으로 새로 발생했다.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

skill-creator 리뷰: runtime cache는 source skill의 semantic routing과 UI metadata를 그대로 반영해야 한다.

## 수정 대상

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db/agents/openai.yaml`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db/references/schema-modeling.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db/references/transactions-locking.md`

수정하지 말아야 할 범위:

- runtime cache의 다른 skill 디렉터리
- source reference `workspace/reference/**`
- eval pack과 generated run artifact

## 재평가

Source `dddjango/skills/architecture-db/`를 runtime cache의 같은 상대 경로로 동기화했다. 최종 `diff -qr` 결과 출력이 없어 source/runtime parity가 확인됐다.
