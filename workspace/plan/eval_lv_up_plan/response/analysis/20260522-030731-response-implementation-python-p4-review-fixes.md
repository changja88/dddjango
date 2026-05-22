수정 대상: case
원인 분류: case

# implementation-python response 리뷰 후속 분석

## 문제

독립 P4 eval integrity real subagent 리뷰에서 `case-response-python-boundaries`가 direct implementation-python coverage로 `TypedDict`와 type narrowing을 요구하지만 public prompt가 그 판단을 충분히 유도하지 않는다는 Major가 확인됐다. 같은 리뷰에서 response direct coverage validator가 `mixed-boundary`, workflow/subagent/role-map 같은 P5 인접 tag를 배제하지 않아 mixed case가 direct P4 coverage로 계산될 수 있다는 Major도 확인됐다.

## 영향

- answer oracle이 public case보다 과도한 요구를 할 수 있다.
- targeted run이 `TypedDict`, `TypeIs`/`TypeGuard` 누락을 관찰하면서도 pass로 남을 수 있어 평가 목적과 판정이 약해진다.
- P4에서 닫아야 하는 개별 skill 평가에 P5 연계/workflow 평가가 섞일 위험이 있다.

## 수정 방향

- public case에 lightweight provider JSON shape 판단과 custom predicate/type narrowing 판단을 명시한다.
- answer oracle required behavior는 public prompt와 같은 판단을 검증하도록 유지하되 hidden-oracle pressure를 줄인다.
- `has_implementation_python_direct_coverage()`가 mixed/workflow/subagent/role-map tag를 direct coverage에서 제외하도록 한다.
- unit test로 mixed/P5 tag가 direct coverage로 계산되지 않는지 검증한다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: 독립 P4 eval integrity real subagent가 response positive case/evaluator에서 Major 3개를 보고했다.

리뷰 결과: Blocker 0, Major 3, 열린 Minor 0
