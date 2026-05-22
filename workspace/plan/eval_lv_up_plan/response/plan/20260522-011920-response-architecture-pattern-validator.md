수정 대상: evaluator

# architecture-implementation-patterns P4 coverage validator 계획

## 수정 범위

- 수정: `workspace/scripts/validate_eval_bucket_pack.py`
- 수정: `workspace/scripts/test_validate_eval_bucket_pack.py`
- 수정: `workspace/develop/eval/response/answer/case-response-architecture-pattern-selection.yaml`
- 추가된 negative case answer의 coverage tag 확인

## 절차

1. architecture-implementation-patterns P4 required tag set을 validator에 추가한다.
2. 누락 tag가 있으면 `architecture-implementation-patterns P4 coverage_tags missing` finding이 나오도록 한다.
3. 회귀 테스트를 추가하고 실패를 확인한 뒤 validator를 고친다.
4. response bucket validator를 재실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- 필수 공통 validator 재실행

## 완료 조건

- response bucket에서 implementation patterns P4 tag 누락이 자동 검출된다.
- 현재 positive/negative architecture-pattern cases가 required tag set을 만족한다.
