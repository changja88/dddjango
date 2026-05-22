수정 대상: answer

# P5 plugin packaging traceability 분석

## 배경

독립 source-governance review에서 `case-plugin-packaging-sync`가 target behavior에는 marketplace entry와 `plugins/dddjango` coherence를 요구하지만 `reference_basis`에는 해당 표면을 직접 넣지 않아 packaging sync traceability가 약하다고 지적했다.

## 원인 분류

- 분류: `answer`
- 대상 case: `case-plugin-packaging-sync`
- 문제: `workspace/develop/eval/plugin/eval_goal.md`는 `.agents/plugins/marketplace.json`와 `plugins/dddjango`를 plugin packaging 기준으로 명시하지만 answer oracle의 `reference_basis`는 `plugin.json`까지만 직접 참조한다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 수정 방향

`reference_basis`에 `.agents/plugins/marketplace.json`와 `plugins/dddjango`를 추가해 manifest, marketplace, symlink/equivalent entry, canonical source가 같은 책임 계약으로 평가되게 한다.
