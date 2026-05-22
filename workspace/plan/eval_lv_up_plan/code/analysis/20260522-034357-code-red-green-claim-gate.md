수정 대상: evaluator
원인 분류: evaluator

# code eval red-green 검증 주장 gate 분석

## 문제

최종 read-only review에서 최신 code run `20260522-033438-code-try01-targeted-implementation-python-p4`가 pass 상태이지만, with-ddjango 응답이 targeted command와 구현 전 실패 확인을 주장했고 해당 주장을 뒷받침하는 별도 command artifact가 없다는 Blocker가 확인됐다.

`pytest` mismatch는 이전 gate로 막았지만, 다음 두 주장은 아직 막지 못한다.

- `python3 -m unittest tests.test_payments tests.test_orders` 같은 exact command claim
- 구현 전 실패, red-green, failing test 확인 claim

## 수정 방향

- code output이 `python3 -m unittest ...` 같은 exact command를 주장하면 captured check command와 정확히 일치해야 한다.
- 구현 전 실패/red-green/failing test claim은 matching non-zero deterministic/behavior check artifact 없이는 실패로 처리한다.
- public case에서 구현 전 실패 확인을 요구하지 않고, 실행한 검증만 정확히 보고하게 유지한다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: final read-only review가 red-green/targeted command claim gate 누락을 Blocker로 보고했다.

리뷰 결과: Blocker 1, Major 0, 열린 Minor 0
