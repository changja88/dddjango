수정 대상: process
원인 분류: process

# P5 plugin manifest cache sync 분석

## 문제

최종 독립 리뷰에서 canonical plugin manifest와 installed runtime cache manifest가 다르다고 확인했다. Canonical `dddjango/.codex-plugin/plugin.json`은 DRF를 legacy maintenance, migration, compatibility, comparison work로 제한한다고 쓰지만, cache manifest는 DRF를 intentionally disallowed라고 쓴다.

## 영향

workflow skill files는 cache sync가 되었지만 plugin-level completion evidence에는 manifest/marketplace/cache coherence도 포함된다. manifest drift가 남으면 P5 plugin/cache/source completion honesty를 완료로 볼 수 없다.

## 수정 방향

- canonical plugin manifest를 installed runtime cache manifest로 동기화한다.
- `cmp`와 `validate_skill_docs.py --phase all`로 확인한다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: 최종 workflow-integrity review subagent가 manifest drift를 Major로 보고했다.

skill-creator 리뷰: 해당 없음. plugin manifest/cache process sync 문제다.
