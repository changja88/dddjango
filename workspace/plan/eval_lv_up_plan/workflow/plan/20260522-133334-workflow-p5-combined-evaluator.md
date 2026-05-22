수정 대상: evaluator

# workflow P5 combined evaluator 계획

## 수정 범위

- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 순서

1. workflow answer list를 순회해 combined P5 case를 판정하는 helper를 추가한다.
2. `validate_coverage("workflow", answers)`에서 combined P5 helper가 false면 finding을 추가한다.
3. 결여된 answer는 실패하고 조건을 모두 갖춘 answer는 통과하는 단위 테스트를 추가한다.
4. bucket validator와 관련 테스트를 실행한다.

## 완료 조건

- workflow bucket은 tag 조합이 여러 case에 흩어진 상태만으로 P5 complete처럼 통과하지 않는다.
- Direct risky-write answer는 combined P5 workflow coverage로 인정되지 않는다.
- Validator 테스트가 회귀 방지 증거를 남긴다.
