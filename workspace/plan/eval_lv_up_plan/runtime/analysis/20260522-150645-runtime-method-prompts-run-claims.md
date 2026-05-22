수정 대상: case

# runtime method prompts run-claim 분석

## 배경

runtime all-case targeted run `20260522-141300-runtime-try01-targeted-p5-runtime-all`에서 일부 with-ddjango 답변이 current-run artifact의 세부 finding을 인용하거나 실행 증거처럼 서술해 `validate_eval_run.py`의 unsupported eval execution claim gate에 걸렸다.

## 원인 분류

- 분류: `case`
- 대상 case: `case-runtime-baseline-isolation`, `case-runtime-private-material`, `case-runtime-stale-cache`
- 문제: public case가 검증 방법을 묻는 형태이면서도 "검증", "확인"을 요구해 실제 현재 실행 결과나 prior/current run finding을 인용하는 답변을 유도한다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent
리뷰 결과: Blocker 1, Major 1, 열린 Minor 0

## 수정 방향

public case에 실제 current-run finding을 인용하지 말고, 실행하지 않은 검증은 not-run/unknown으로 남기며 증거 종류와 판정 기준 중심으로 답하라고 명시한다.
