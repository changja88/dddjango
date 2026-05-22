수정 대상: evaluator

# code clean-code validator integrity 분석

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

## 배경

implementation-cleancode P4에서 `case-code-fat-model`은 code bucket의 supporting case로 Fat Model/service responsibility split과 side-effect timing을 검증한다. targeted eval은 통과했지만, 독립 리뷰가 code bucket validator에 clean-code source/runtime linkage enforcement가 없다고 지적했다.

## 원래 발견 증거

- `workspace/develop/eval/code/answer/case-code-fat-model.yaml`
  - intent와 reference_basis는 implementation-cleancode 기준을 사용한다.
  - coverage_tags에 `implementation-cleancode`가 없어 clean-code 전용 structural check 대상으로 식별되지 않는다.
- `workspace/scripts/validate_eval_bucket_pack.py`
  - response bucket에는 `validate_response_cleancode_answer`가 있다.
  - code bucket에는 DDD/Django/Django Ninja 검증만 있고 clean-code supporting answer 검증이 없다.

## 원인 분류

evaluator. 현재 case는 수동으로 정렬됐지만, evaluator가 code bucket clean-code supporting case의 reference_basis와 behavior semantics를 보장하지 않는다.

## gap 분류

Major. targeted eval evidence가 있어도 validator enforcement가 없으면 향후 answer basis drift를 구조적으로 막지 못한다.

## 보조 Minor

일부 이전 analysis 문서의 상단 리뷰 결과와 본문 gap 분류가 모순된다. 이는 runtime/eval 동작을 깨지는 않지만 audit traceability를 약하게 한다.

## 수정 후 닫힘 증거

- `workspace/develop/eval/code/answer/case-code-fat-model.yaml`
  - coverage_tags에 `implementation-cleancode`를 추가했다.
  - clean-code source/runtime/bundled reference basis를 유지한다.
- `workspace/scripts/validate_eval_bucket_pack.py`
  - code bucket에서 `implementation-cleancode` answer의 source/runtime/bundled basis와 responsibility, side-effect boundary, regression test, overengineering restraint term을 검증한다.
- `workspace/scripts/test_validate_eval_bucket_pack.py`
  - basis 누락, semantic term 누락, neutral supporting case baseline 허용을 테스트한다.
- stale analysis summary는 본문 gap 분류와 맞게 수정했다.
- 검증:
  - `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py` 통과
  - `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code` 통과
  - `make eval-one BUCKET=code CASE=case-code-fat-model TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-cleancode-p4 EXTRA_ARGS=--rerun JOBS=1` 통과, run id `20260522-023324-code-try01-targeted-implementation-cleancode-p4`

## 수정 방향

- 위 Major와 보조 Minor는 수정 후 닫혔다.
