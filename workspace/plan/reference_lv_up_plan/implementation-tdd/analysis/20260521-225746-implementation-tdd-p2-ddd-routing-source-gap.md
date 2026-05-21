수정 대상: reference

# implementation-tdd DDD routing source gap 후속 분석

## 발견 사항

P2 post-change 리뷰에서 `implementation-tdd` runtime의 `architecture-ddd` routing, aggregate/model ownership 표현이 `workspace/reference/implementation-tdd/reference/final.md`에서 직접 뒷받침되지 않는다는 source-basis gap이 확인됐다.

## 현재 P2 처리

- P2 skill 수정에서는 해당 DDD ownership routing 표현을 제거한다.
- TDD skill은 불명확한 행위/정책을 unresolved decision으로 분리하고 테스트 기대값을 고정하지 않는 범위만 유지한다.

## 후속 검토 필요성

향후 `implementation-tdd` source reference가 DDD skill과의 협업 경계를 명시할 필요가 있다면, 다음을 source reference 레벨에서 결정해야 한다.

- 불명확한 도메인 규칙 또는 모델 소유권이 TDD 전에 어떤 skill로 라우팅되어야 하는지
- TDD test list가 domain modeling decision과 만나는 경계
- DDD routing이 implementation-tdd runtime metadata에 들어갈 수 있는 조건

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

- post-change real-subagent 리뷰에서 source-basis gap으로 제기된 항목을 후속 reference 분석으로 분리했다.

## 완료 조건

- 이번 P2 runtime skill은 source-basis가 약한 DDD routing claim을 하지 않는다.
- reference 보강 여부는 별도 reference 개선 작업에서 판단한다.
