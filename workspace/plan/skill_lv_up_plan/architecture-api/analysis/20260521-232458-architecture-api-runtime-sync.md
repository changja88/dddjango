수정 대상: runtime-sync

# architecture-api runtime cache 동기화 분석

## 점검 범위

- Source: `dddjango/skills/architecture-api/`
- Runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api/`

## 현재 상태

`architecture-api` P3 skill 수정 후 source skill과 runtime cache가 달라졌다.

차이 파일:

- `SKILL.md`
- `agents/openai.yaml`

Bundled reference 파일은 수정하지 않았으므로 차이가 없어야 한다.

## 원인

P3 progressive disclosure 수정은 source skill에 먼저 적용했다. Codex runtime은 cache의 skill을 읽을 수 있으므로 source와 runtime cache parity를 맞춰야 한다.

## 필요한 조치

- source `dddjango/skills/architecture-api/` 내용을 runtime cache의 동일 skill 경로로 동기화한다.
- 동기화 후 `diff -qr`로 차이가 없는지 확인한다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

### 리뷰 통합

- 두 real-subagent 리뷰 모두 architecture-api source/runtime cache parity가 맞는 상태를 확인했다.
- 이후 bundled reference와 metadata Minor 수정이 추가되어 runtime cache를 다시 동기화했고, `diff -qr` 재검증 대상으로 둔다.

## skill-creator 리뷰

- runtime cache가 source skill과 다르면 실제 skill 사용자가 stale guidance를 받을 수 있으므로 cache parity를 완료 조건으로 둔다.

## 재평가

- source skill과 runtime cache는 최종 동기화 후 `diff -qr`로 다시 확인한다.
- runtime cache 동기화 외 추가 skill/source reference 수정은 필요하지 않다.
