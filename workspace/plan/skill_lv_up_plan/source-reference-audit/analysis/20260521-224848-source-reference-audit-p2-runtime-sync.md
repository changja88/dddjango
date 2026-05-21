수정 대상: runtime-sync

# source-reference-audit P2 runtime sync 분석

## 평가 요약

P2 skill 수정 후 source skill과 runtime cache가 달라졌다. runtime cache는 사용자가 지정한 대상이므로 source skill 수정 내용을 반영해 동기화해야 한다.

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

Subagent 리뷰/순차 fallback: P2 real-subagent 리뷰에서 수정 전 cache parity는 확인됐다. 메인 에이전트가 source skill 수정 후 `diff -qr`를 실행해 `SKILL.md`와 `agents/openai.yaml` 차이를 확인했다.

skill-creator 리뷰: runtime cache 자체는 skill-creator의 authoring 대상은 아니지만, `agents/openai.yaml` metadata가 source skill과 semantic alignment를 유지하려면 runtime cache도 같은 파일 내용을 가리켜야 한다.

## 근거

- source 파일 수정 대상:
  - `dddjango/skills/source-reference-audit/SKILL.md`
  - `dddjango/skills/source-reference-audit/agents/openai.yaml`
- runtime cache 대상:
  - `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit/SKILL.md`
  - `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit/agents/openai.yaml`
- `diff -qr dddjango/skills/source-reference-audit /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit` 결과 두 파일 차이가 확인됐다.

## 발견 사항

### Major 1. P2 source 수정 후 runtime cache 불일치

종료 조건은 source skill과 runtime cache sync 확인을 요구한다. 현재 runtime cache는 P2 source 수정 전 내용을 유지하므로 동기화가 필요하다.

허용 claim:

- runtime cache는 source skill 수정 직후 불일치 상태다.
- 동기화 후 실제 diff evidence로 parity를 확인해야 한다.

금지 claim:

- 동기화 전 상태에서 source/runtime cache가 일치한다고 보고한다.

## 수정 필요 범위

- runtime cache의 `SKILL.md`
- runtime cache의 `agents/openai.yaml`

## 수정하지 말아야 할 범위

- runtime cache 외 다른 cache skill은 수정하지 않는다.
- source reference, eval pack, 다른 skill은 수정하지 않는다.
- runtime cache 물리 경로를 runtime-facing allowed reference로 만들지 않는다.

## 재평가 기준

- source skill과 runtime cache가 `diff -qr` 기준으로 동일하다.
- 필수 validators가 통과한다.
- runtime-sync 관련 열린 Blocker, Major, Minor가 없다.

## 최종 재평가

`SKILL.md`, `agents/openai.yaml`, `references/source-governance.md`를 runtime cache에 동기화했다. 최종 `diff -qr`는 출력 없이 종료했고, runtime-sync 관련 열린 Blocker, Major, Minor는 없다.
