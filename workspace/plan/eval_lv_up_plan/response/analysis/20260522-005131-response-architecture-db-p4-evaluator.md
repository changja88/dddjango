수정 대상: evaluator
원인 분류: evaluator undercheck

# architecture-db P4 evaluator 분석

## 문제

현재 validator는 response bucket의 일반 coverage tag만 확인한다. architecture-db P4에서 요구한 schema/ERD, keys, constraints/indexes, transaction/isolation/locking, idempotency storage, duplicate prevention, EXPLAIN, rollout/backfill/migration safety를 구조적으로 보장하지 못한다.

또한 `validate_eval_run.py`와 `validate_eval_protocol.py`는 with-dddjango prompt-input artifact의 존재만 확인하고, 비어 있거나 JSON으로 파싱할 수 없는 경우를 잡지 못했다. 실패한 targeted run에서 zero-byte prompt-input artifact가 남았기 때문에 leakage/source-boundary evidence가 약해질 수 있다.

## 근거

- `workspace/scripts/validate_eval_bucket_pack.py`의 response required coverage는 broad family tag 중심이다.
- `workspace/scripts/validate_eval_run.py`와 `workspace/scripts/validate_eval_protocol.py`의 prompt-input 검증은 file existence 중심이었다.
- 실패한 targeted run의 `case-response-db-schema-modeling-with-dddjango-prompt-input.json`은 zero-byte artifact였지만, 해당 조건을 별도 검사하는 구조가 없다.

## 수정 방향

- response bucket validator에 architecture-db P4 direct coverage tag 검사를 추가한다.
- 검사 대상은 answer oracle coverage tags이며, 다음 tag가 response bucket 안에 있어야 한다.
  - `schema-modeling`
  - `keys-cardinality-optionality`
  - `constraints-indexes`
  - `transaction-locking`
  - `isolation-retry`
  - `idempotency-storage`
  - `duplicate-prevention`
  - `query-performance`
  - `operational-rollout`
  - `migration-safety`
- `validate_eval_run.py`와 `validate_eval_protocol.py`는 prompt-input artifact를 non-empty JSON object 또는 array로 검증한다.
- TDD 순서로 validator tests를 먼저 추가해 실패를 확인한 뒤 production script를 수정한다.

## 리뷰 방식

리뷰 방식: real-subagent

- 독립 리뷰: validator가 architecture-db P4 dimensions를 강제하지 않는 Major, prompt-input artifact validation 약함 Major.
- skill-creator 관점 리뷰: validation integrity Blocker/Major.
- 후속 skill-creator 관점 리뷰: prompt-input 검증이 protocol validator에는 미반영된 Minor.

리뷰 결과: Blocker 1, Major 2, 열린 Minor 1
