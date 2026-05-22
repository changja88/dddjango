수정 대상: evaluator

# P5 plugin semantic validator 수정 계획

## 수정 범위

- `workspace/scripts/validate_eval_bucket_pack.py`

## 순서

1. plugin bucket answer semantic validator 함수를 추가한다.
2. packaging, agents metadata, trigger quality, reference split, cache/source consistency, leakage sentinel case의 필수 근거와 behavior term을 확인한다.
3. 기존 구조 validator 흐름에서 bucket이 `plugin`일 때 실행한다.
4. plugin bucket validator와 script test를 실행한다.

## 완료 조건

- plugin bucket structural pass가 P5 governance answer undercheck를 숨기지 않는다.
