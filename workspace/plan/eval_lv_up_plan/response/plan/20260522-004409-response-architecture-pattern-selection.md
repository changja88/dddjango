수정 대상: case

# architecture-implementation-patterns P4 response case 계획

## 수정 범위

- 추가: `workspace/develop/eval/response/cases/plugin/public/case-response-architecture-pattern-selection.md`
- 추가: `workspace/develop/eval/response/answer/case-response-architecture-pattern-selection.yaml`

## 절차

1. Public case는 파일 수정 없는 설계 답변 요청으로 작성한다.
2. 질문에는 이미 도메인/use case가 어느 정도 정해진 상황을 제공해 `architecture-ddd`가 아니라 `architecture-implementation-patterns`가 주 검증 대상이 되게 한다.
3. answer oracle은 다음을 필수 관찰점으로 둔다.
   - 가장 가벼운 충분 패턴 선택
   - layered/clean/hexagonal과 dependency direction 판단
   - ports/adapters, repository/UoW, service layer 선택 기준
   - CQRS, event sourcing, saga, outbox, ACL의 조건부 선택 또는 제외 이유
   - risky write consistency block과 owning skill handoff
   - false command/subagent/file-inspection claim 금지
4. Public case에는 answer field name, private scoring note, 이전 run finding을 넣지 않는다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `make eval-one BUCKET=response CASE=case-response-architecture-pattern-selection TRY_NUMBER=1 SCOPE=targeted TOPIC=architecture-pattern-selection EXTRA_ARGS=--rerun JOBS=1`
- 필수 공통 validator와 독립 리뷰는 수정 후 실행한다.

## 완료 조건

- response inventory에 `architecture-implementation-patterns` positive case가 생긴다.
- 기존 simple rename negative case와 함께 사용 조건/제외 조건 coverage가 닫힌다.
- validator와 targeted eval 결과가 evidence로 남는다.
