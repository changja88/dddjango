수정 대상: runtime-sync

# implementation-tdd P2 review-fix runtime sync 분석

## 원인

P2 재평가 수정으로 source `SKILL.md`에서 DDD ownership routing wording을 제거하고 pytest-bdd/Gherkin routing을 본문에 추가했다. runtime cache는 source 수정 직후 stale 상태가 된다.

## 동기화 대상

- source: `dddjango/skills/implementation-tdd/`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/`

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

- post-change 리뷰에서 source/runtime parity 확인 필요성이 재확인됐다.

## 완료 조건

- source와 runtime cache의 recursive diff가 없다.
