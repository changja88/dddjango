수정 대상: answer

# P5 plugin reference split negative condition 분석

## 배경

plugin semantic validator 추가 후 `case-plugin-reference-split` answer가 reference file별 load condition과 negative condition을 요구하지만 문장이 validator가 확인하는 negative-condition proof를 안정적으로 드러내지 못했다.

## 원인 분류

- 분류: `answer`
- 대상 case: `case-plugin-reference-split`
- 문제: progressive disclosure 평가에서 각 bundled reference가 언제 로드되지 않아야 하는지도 확인해야 하지만 문장이 짧아 semantic check의 evidence term으로 약했다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

## 수정 방향

load conditions와 함께 skipped loading/use의 negative conditions를 명시한다.
