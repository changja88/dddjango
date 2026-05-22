수정 대상: evaluator

# P5 plugin semantic validator 분석

## 배경

독립 source-governance review에서 plugin bucket structural validation은 통과하지만 trigger routing, packaging sync, reference split, cache/source mismatch, leakage sentinel 같은 P5 governance semantics가 validator에서 충분히 강제되지 않는다고 지적했다.

## 원인 분류

- 분류: `evaluator`
- 문제: `validate_eval_bucket_pack.py`가 plugin bucket에 대해 coverage tag와 일반 answer shape는 확인하지만 P5 governance answer가 핵심 source basis와 expected behavior를 갖는지는 별도로 검사하지 않는다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 수정 방향

plugin answer semantic validator를 추가해 주요 P5 coverage tag별 필수 reference basis와 target behavior/evidence term을 확인한다.
