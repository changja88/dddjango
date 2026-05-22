수정 대상: evaluator

# architecture-ddd P4 code 평가 개선 계획

## 수정 범위

- `workspace/develop/eval/code/cases/plugin/public/case-code-ddd-order-placement.md`
- `workspace/develop/eval/code/answer/case-code-ddd-order-placement.yaml`
- `workspace/scripts/eval_code_behavior_checks.py`

## 절차

1. public case에 `Order` lifecycle 상태를 외부에서 직접 바꾸지 말라는 공개 요구를 추가한다.
2. answer oracle에 aggregate-owned lifecycle state 보호와 상태 관찰/변경 경계를 추가한다.
3. hidden behavior check에서 외부 direct assignment와 service direct mutation을 검증한다.
4. 관련 validator와 behavior check 테스트를 실행한다.
5. targeted eval은 sandbox 제한 때문에 실행 가능 여부를 별도 보고한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_eval_code_behavior_checks.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- 필수 전체 검증 단계에서 plan constraints, skill docs, 관련 bucket validators를 다시 실행한다.
- targeted eval 후보: `make eval-one BUCKET=code CASE=case-code-ddd-order-placement TRY_NUMBER=1 SCOPE=targeted TOPIC=architecture-ddd-order-lifecycle EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- order direct DDD case가 aggregate behavior뿐 아니라 lifecycle state 외부 변경 방지도 검증한다.
- answer oracle이 source reference보다 과하거나 부족하지 않다.
- public case에 private oracle이나 이전 run finding이 없다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0으로 닫힌다.

