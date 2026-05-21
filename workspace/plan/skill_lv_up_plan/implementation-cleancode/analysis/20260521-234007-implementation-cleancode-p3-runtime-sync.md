수정 대상: runtime-sync

# implementation-cleancode P3 runtime sync 분석

## 평가 기준

- canonical source: `dddjango/skills/implementation-cleancode/`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode/`
- P3 종료 조건은 source skill과 runtime cache 동기화 확인을 요구한다.

## 현재 판정

| 항목 | 판정 | 근거 |
|---|---|---|
| source skill 수정 여부 | 수정됨 | P3 skill 계획에 따라 `dddjango/skills/implementation-cleancode/SKILL.md` routing과 Runtime Rules를 수정했다. |
| runtime cache parity | 불일치 | source 수정 직후 `diff -qr dddjango/skills/implementation-cleancode /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode`가 `SKILL.md` 차이를 보고했다. |
| sync 필요성 | 필요 | runtime cache가 이전 skill guidance를 계속 노출하면 P3 수정이 런타임에 반영되지 않는다. |

## 원인

- source skill의 routing과 progressive disclosure 문구를 수정했지만 runtime cache는 자동 갱신되지 않는다.

## 수정 필요 범위

- `dddjango/skills/implementation-cleancode/SKILL.md`를 runtime cache의 대응 파일로 복사한다.
- 다른 runtime cache 파일은 source와 차이가 없으면 수정하지 않는다.

## 수정하지 않는 범위

- `agents/openai.yaml`과 bundled references는 이번 P3 source 수정 대상이 아니며 diff가 없으면 복사하지 않는다.
- 다른 skill cache는 수정하지 않는다.

## 리뷰 방식과 결과

리뷰 방식: real-subagent
- Subagent 리뷰/순차 fallback: P3 skill 리뷰 subagent 중 하나가 수정 전 cache parity가 clean이라고 보고했다. source 수정 후에는 main agent가 diff와 sync 검증을 수행한다.
- skill-creator 리뷰: runtime cache parity는 source skill 수정 후 별도 diff 증거로 닫는다.
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
- 닫은 Minor 1: source 수정 후 runtime cache `SKILL.md`가 달랐고, canonical source를 runtime cache에 복사해 닫았다.

## 결론

runtime cache sync가 필요했고 canonical source `SKILL.md`만 runtime cache에 반영했다. 최종 parity는 검증 단계의 `diff -qr` 결과로 재확인한다.
