수정 대상: evaluator
원인 분류: evaluator undercheck

# architecture-db P4 local CRUD negative coverage 분석

## 문제

독립 리뷰에서 response bucket validator가 architecture-db P4 positive dimensions는 구조적으로 요구하지만, architecture-db 전용 제외 조건인 low-risk local CRUD restraint를 별도 coverage tag로 강제하지 않는 문제가 확인됐다.

기존 구조에서는 `simple-negative` 또는 일반 `overapplication-restraint`가 남아 있으면 `case-response-db-local-crud-restraint`가 삭제되거나 약화되어도 validator가 놓칠 수 있다. P4 기준은 positive 사용 조건뿐 아니라 제외 조건도 검증해야 하므로, DB 전용 negative dimension이 직접 architecture-db coverage로 잡혀야 한다.

## 근거

- `dddjango/skills/architecture-db/SKILL.md`는 simple field rename 또는 local CRUD without invariant/concurrency/rollout risk를 제외 조건으로 둔다.
- `workspace/develop/eval/response/cases/plugin/public/case-response-db-local-crud-restraint.md`는 no-risk local CRUD 상황을 공개 case로 잘 분리했다.
- `workspace/develop/eval/response/answer/case-response-db-local-crud-restraint.yaml`은 ERD, locking/isolation, idempotency, workflow/subagent overreach를 금지한다.
- 기존 `RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS`에는 이 DB-specific negative dimension이 없었다.

## 수정 방향

- response bucket structural validator의 architecture-db P4 required tag에 `db-local-crud-restraint`를 추가한다.
- `case-response-db-local-crud-restraint.yaml`의 coverage_tags에 같은 tag를 추가한다.
- validator test가 `migration-safety`와 `db-local-crud-restraint` 누락을 모두 잡도록 갱신한다.
- 이 변경은 evaluator/answer coverage metadata만 좁게 바꾸며 public case 문구는 바꾸지 않는다.

## 리뷰 방식

리뷰 방식: real-subagent

독립 subagent 리뷰에서 DB-specific local CRUD negative coverage가 structural validator에 의해 강제되지 않는 Major가 확인됐다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0
