수정 대상: answer
원인 분류: answer underclaim

# coupon TDD compile claim 분석

## 범위

- bucket: `code`
- case: `case-code-coupon-tdd`
- run id: `20260522-105005-code-try01-targeted-implementation-tdd-p4`

## 현상

targeted eval에서 baseline과 with-dddjango 응답이 모두 compile 확인을 실행했다고 보고했지만, answer oracle의 deterministic check에는 unittest만 있어 compile command artifact가 생성되지 않았다.

`validate_eval_run.py`는 실행 주장과 command artifact를 대조하므로 다음 finding으로 실패했다.

- baseline: `output claims compileall execution without matching check command artifact`
- with-dddjango: `output claims compileall execution without matching check command artifact`

## 판단

모델 출력이 compile 확인을 반복적으로 보고하고 있고, compile 검증 자체는 code-backed fixture에서 허용 가능한 최소 정적 검증이다. 공용 prompt에 private 기준을 넣지 않고 answer oracle의 deterministic check에 compileall을 추가해 실행 증거와 claim gate를 일치시킨다.

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

재평가 결과: `20260522-112629-code-try01-targeted-implementation-tdd-p4`가 passed이고 compileall command artifact가 생성됐다.
