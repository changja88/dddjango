수정 대상: case
원인 분류: case

# architecture-implementation-patterns negative/routing case 분석

## 문제

독립 `skill-creator` 관점 리뷰에서 `case-response-architecture-pattern-selection`이 positive case로는 충분하지만, `architecture-implementation-patterns`의 제외 조건과 route-out 조건을 public negative case로 직접 검증하지 않는다는 Major가 나왔다.

기존 `case-response-simple-rename`은 단순 rename에서 broad workflow와 repository/UoW 과적용을 막지만, `architecture-implementation-patterns` 자체의 layered/hexagonal/repository/outbox/CQRS/saga/ACL 제외 기준을 명시적으로 평가하지 않는다.

## 영향

- P4 기준 2인 positive/negative case 사용 조건과 제외 조건 검증이 약하다.
- skill의 "simple CRUD/tiny edit에는 heavy pattern을 도입하지 않는다"는 핵심 경계가 개별 skill 평가로 닫히지 않는다.

## 수정 방향

- `response` bucket에 architecture pattern restraint negative case를 추가한다.
- Public case는 단순 Django CRUD 조회/필드 수준 작업에서 repository/UoW/hexagonal/outbox/CQRS/saga/ACL을 도입해야 하는지 묻되, 파일 수정 없이 짧은 판단을 요구한다.
- Answer oracle은 heavy pattern 회피, Django-native/model/service/selector 수준 유지, 필요한 owning skill handoff, 검증 정직성을 판정한다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 1, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: skill-creator 관점 subagent가 negative/routing coverage 부족을 Major로 보고했다. 본 분석은 해당 Major를 닫기 위한 후속이다.

skill-creator 리뷰: trigger exclusion과 validation integrity 기준으로 public negative case가 필요하다는 지적을 채택한다.
