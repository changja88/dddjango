수정 대상: evaluator

# plugin trigger-routing negative claim validator 계획

## 수정 범위

- `workspace/scripts/validate_eval_run.py`
- `workspace/scripts/test_validate_eval_run.py`

## 절차

1. generic execution negative pattern에 `아님`, `아닌`을 추가한다.
2. plugin response의 routing exclusion 문장이 eval/validator 실행 claim으로 오인되지 않는 테스트를 추가한다.
3. `test_validate_eval_run.py`를 실행한다.
4. `case-plugin-trigger-routing` pass run을 재검증한다.

## 완료 조건

- 실제 실행 주장은 event evidence가 계속 필요하다.
- "이 skill이 아님" 같은 라우팅 제외 문장은 실행 주장으로 실패하지 않는다.
