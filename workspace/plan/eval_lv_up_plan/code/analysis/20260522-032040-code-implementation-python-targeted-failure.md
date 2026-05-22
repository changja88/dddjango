수정 대상: case
원인 분류: case

# implementation-python code targeted eval 실패 분석

## 실패 run

- run id: `20260522-031407-code-try01-targeted-implementation-python-p4`
- case: `case-code-python-state`
- status: failed

## 원인

`validate_eval_run.py`가 `expected_delta=positive`인데 baseline과 with-dddjango score가 모두 `4 / 5`라고 판정해 실패했다. oracle은 두 변형 모두 `apps/orders/services.py` 변경을 allowed_paths 밖 품질 문제로 기록했고, public case는 주문 상태 표현 개선 범위를 요구하면서 service 변경이 가능한지 명확히 말하지 않았다.

또한 public case의 검증 보고 요구가 넓어 두 변형 모두 실제 산출물이 없는 compile/whitespace 같은 검증 주장을 포함했다. 이는 case가 verification honesty를 충분히 유도하지 못한 문제다.

## 수정 방향

- public case에 변경 범위를 명시해 `apps/orders/services.py`를 주문 상태 표현 개선 범위 안에 둔다.
- public case에 실제 실행한 검증만 보고하고 실행하지 않은 검증은 미실행으로 적도록 명시한다.
- answer oracle의 allowed_paths에 `apps/orders/services.py`를 추가한다.
- targeted eval을 재실행한다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: 앞선 real subagent 리뷰의 code answer traceability Major는 별도 validator/answer 수정으로 처리했고, 이 문서는 targeted run 실패 후 case/answer 범위 불일치를 닫기 위한 후속 분석이다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0
