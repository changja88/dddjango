수정 대상: case

# architecture-implementation-patterns negative/routing case 계획

## 수정 범위

- 추가: `workspace/develop/eval/response/cases/plugin/public/case-response-architecture-pattern-restraint.md`
- 추가: `workspace/develop/eval/response/answer/case-response-architecture-pattern-restraint.yaml`

## 절차

1. Public case는 단순 Django CRUD/조회/필드 변경 수준의 요청으로 작성한다.
2. Public case에 private oracle field name, prior run finding, answer-only 기준을 넣지 않는다.
3. Answer oracle은 heavy architecture pattern 회피와 route-out 판단을 검증한다.
4. 기존 positive case와 함께 inventory에서 사용 조건과 제외 조건이 모두 닫히는지 확인한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `make eval-one BUCKET=response CASE=case-response-architecture-pattern-restraint TRY_NUMBER=1 SCOPE=targeted TOPIC=architecture-pattern-restraint EXTRA_ARGS=--rerun JOBS=1`

## 완료 조건

- `architecture-implementation-patterns` 개별 skill 평가에 positive와 negative/routing case가 모두 존재한다.
- answer oracle이 source reference보다 과도한 요구를 하지 않는다.
- targeted eval에서 with-ddjango가 heavy-pattern restraint를 통과한다.
