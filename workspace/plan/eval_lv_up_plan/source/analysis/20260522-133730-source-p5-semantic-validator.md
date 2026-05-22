수정 대상: evaluator

# P5 source semantic validator 분석

## 배경

source bucket에는 eval traceability case가 있으나 validator는 metadata/cache, routing exclusion, provisional/DRF 중심으로 특화되어 있어 per-case traceability proof를 강제하지 않는다.

## 원인 분류

- 분류: `evaluator`
- 문제: `case-source-eval-traceability`가 public case path, answer path, case id, source basis, coverage label, leakage boundary, run artifact mapping을 빠뜨려도 bucket validator가 통과할 수 있다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

## 수정 방향

source eval-traceability answer semantic validator를 추가해 per-case traceability evidence terms를 확인한다.
