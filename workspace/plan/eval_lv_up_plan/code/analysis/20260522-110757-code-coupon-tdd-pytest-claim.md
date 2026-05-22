수정 대상: case
원인 분류: case ambiguity

# coupon TDD pytest claim 분석

## 범위

- bucket: `code`
- case: `case-code-coupon-tdd`
- run id: `20260522-110124-code-try01-targeted-implementation-tdd-p4`

## 현상

with-dddjango 응답이 `전체 pytest suite` 통과를 보고했지만 answer oracle의 deterministic check는 `python3 -m unittest`와 compileall만 실행한다. 현재 fixture는 unittest 기반이고 public case가 "unittest 또는 pytest"라고 열어 두어 모델이 실행 artifact가 없는 pytest 결과를 보고할 여지가 있다.

## 판단

원인은 public case의 검증 도구 표현이 넓은 것이다. 이 case는 TDD 방법론과 coupon boundary를 검증하며 pytest mechanics를 검증하지 않는다. public prompt를 unittest 중심으로 좁히고, pytest는 실제 실행하지 않았다면 보고하지 말라고 명시한다.

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

재평가 결과: `20260522-112629-code-try01-targeted-implementation-tdd-p4`가 passed이고 unsupported pytest claim finding이 없다.
