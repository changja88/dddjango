수정 대상: case
원인 분류: case

# source provisional status case 분석

## 문제

`source` bucket의 `case-source-provisional-drf` public case와 answer oracle은 `architecture-implementation-patterns`, `implementation-django-ninja`, `implementation-django-web` 영역을 전용 source reference가 부족한 대상으로 고정한다. 현재 저장소에는 세 영역 모두 `workspace/reference/<area>/reference/final.md`가 존재한다.

특히 P4 대상인 `architecture-implementation-patterns`는 `final.md`가 layered/clean/hexagonal, ports/adapters, dependency direction, repository/UoW, CQRS, event sourcing, saga, outbox, ACL, service layer, risky write handoff를 다룬다.

## 영향

- P4 기준 4: answer oracle이 현재 reference보다 부족한 판단을 요구한다.
- P4 기준 5: source case가 current-state source audit이 아니라 오래된 provisional 상태를 검증한다.
- Public case가 "전용 source reference가 부족한"이라는 단정으로 현재 source status 분류를 방해한다.

## 수정 방향

- Public case는 source reference status와 DRF guardrail을 함께 점검하되 부족 여부를 단정하지 않게 고친다.
- Answer oracle은 dedicated source reference가 있으면 dedicated로 인정하고, 없거나 범위가 부족한 경우에만 provisional/gap으로 분류하도록 고친다.
- DRF guardrail은 별도 row로 유지한다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 2, 열린 Minor 1

수정 후 real-subagent 리뷰에서 DRF guardrail 축과 source validator semantic coverage가 부족하다는 Major, eval goal wording이 file-existence-only reasoning으로 읽힐 수 있다는 Minor가 확인됐다. 후속 수정은 `20260522-105641-source-drf-guardrail-validator.md`에서 닫는다.
