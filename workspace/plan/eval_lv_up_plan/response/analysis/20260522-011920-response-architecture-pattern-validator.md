수정 대상: evaluator
원인 분류: evaluator

# architecture-implementation-patterns P4 coverage validator 분석

## 문제

독립 리뷰에서 `validate_eval_bucket_pack.py --bucket response`가 architecture-implementation-patterns P4 전용 coverage tag를 강제하지 않아, 새 case가 사라지거나 축소되어도 구조 검증이 P4 gap을 잡지 못한다는 Major가 나왔다.

기존 validator는 architecture-db/API P4 tag set만 별도 강제했고, implementation patterns의 layered/clean/hexagonal, dependency direction, ports/adapters, repository/UoW, CQRS/event sourcing, saga/outbox/ACL, service layer, risky write, negative restraint는 일반 response tag만으로는 보장되지 않았다.

## 수정 방향

- response bucket 전용 architecture-implementation-patterns P4 required coverage tag set을 추가한다.
- `test_validate_eval_bucket_pack.py`에 누락 tag를 실패시키는 회귀 테스트를 추가한다.
- 새 positive/negative case answer에 해당 tag를 부여해 현재 pack이 통과하게 한다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 2, 열린 Minor 1

Subagent 리뷰/순차 fallback: 독립 P4 eval review subagent가 validator coverage gap을 Major로 보고했다. 본 분석은 해당 Major를 닫기 위한 후속이다.

skill-creator 리뷰: validation integrity 관점에서 구조 validator가 P4 coverage 회귀를 잡아야 한다는 지적을 채택한다.
