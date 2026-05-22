수정 대상: evaluator

# P5 runtime semantic validator 수정 계획

## 수정 범위

- `workspace/scripts/validate_eval_bucket_pack.py`

## 순서

1. runtime wrong-routing answer validator를 추가한다.
2. runtime stale-cache/cache-source consistency answer validator를 추가한다.
3. 기존 runtime answer validation 흐름에 연결한다.
4. runtime bucket validator와 script test를 실행한다.

## 완료 조건

- runtime bucket structural pass가 wrong-routing/stale-cache undercheck를 숨기지 않는다.
