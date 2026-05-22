수정 대상: case
원인 분류: case coverage gap

# implementation-tdd P4 response 직접 coverage 분석

## 범위

- bucket: `response`
- 관련 skill: `dddjango/skills/implementation-tdd/`
- source reference: `workspace/reference/implementation-tdd/reference/final.md`
- 기존 관련 case:
  - `case-response-coupon-ambiguity`

## 현재 상태

`case-response-coupon-ambiguity`는 애매한 쿠폰 정책에서 구현 전 질문과 확인된 범위의 test list를 요구한다. 이 case는 `ambiguity`, `tdd`, `test-list`, `validation-honesty`를 검증하지만 P4 기준의 전체 축을 직접 검증하지 못한다.

누락 축:

- failing test first와 Red-Green-Refactor의 실행 정직성
- Inside-Out/Outside-In 선택 기준
- acceptance/unit double loop
- boundary cases의 각 축별 accepted/rejected pair
- refactoring checkpoint
- state vs behavior verification 선택
- mock role 기준
- BDD/ATDD가 TDD 흐름에서 갖는 위치와 `implementation-test` handoff
- pytest-bdd/Gherkin/fixture/factory mechanics 제외 조건

## 판단

관련 response case가 없으므로 P4 기준상 Major coverage gap이다. source reference와 runtime bundled references는 기준을 제공하므로 reference/skill 수정이 아니라 eval case/answer 추가가 주된 수정이다.

## Inventory

| bucket | case id | public | answer | evaluator 관련성 | 수정 여부 | targeted eval 필요 | run id | status |
|---|---|---|---|---|---|---|---|---|
| response | `case-response-coupon-ambiguity` | ambiguity/test list 중심 | ambiguity와 false Red/Green claim 중심 | 기존 validator 일반 구조만 확인 | 유지 | 아니오 | 미실행 | supporting |
| response | `case-response-tdd-loop-selection` | TDD 접근/loop/verification 선택 직접 요청 | implementation-tdd P4 직접 oracle | 새 direct coverage validator 대상 | 추가 | 예 | `20260522-104139-response-try01-targeted-implementation-tdd-p4` | passed |

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

재평가 결과: `case-response-tdd-loop-selection` targeted eval이 passed이고 RUN_VALIDATION findings가 없다.
