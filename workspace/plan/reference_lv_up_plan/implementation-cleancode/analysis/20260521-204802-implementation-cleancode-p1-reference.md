수정 대상: reference

# implementation-cleancode P1 reference 분석

## 평가 기준

- 대상 reference: `workspace/reference/implementation-cleancode/reference/final.md`
- 기준 범위: responsibility separation, naming, function shape, encapsulation, abstraction, SOLID, duplication, error handling, legacy review, fat model/view/router, maintainability
- 판단 방식: `final.md`를 우선 근거로 보고, 부족 여부 확인을 위해 `review.md`, `internal.md`, `external.md`에서 Django/Fat View/Router/Model 관련 근거를 검색했다.

## 현재 판정

| 항목 | 판정 | 근거 |
|---|---|---|
| 책임 분리 | 충분 | `final.md`의 SRP, 역할/책임/협력, 변경 이유 기준, 코드 스멜 카탈로그가 판단 기준을 제공한다. |
| 이름 짓기 | 충분 | `final.md` 2장과 요약표가 의도, 검색성, 한 개념 한 단어, 불리언 이름, 범위별 길이를 다룬다. |
| 함수 형태 | 충분 | `final.md` 3장이 추상화 수준, 인수 수, 플래그 인수, 명령/조회 분리, 부수 효과를 다룬다. |
| 캡슐화/추상화 | 충분 | `final.md` 6-8장이 정보 은닉, 깊은 모듈, 객체 책임, 설계 레드 플래그를 다룬다. |
| SOLID | 충분 | `final.md` 9장이 SRP/OCP/LSP/ISP/DIP의 판단 기준과 예시를 제공한다. |
| 중복/DRY | 충분 | `final.md` 13장이 지식 중복과 우연한 유사 코드의 차이를 다룬다. |
| 오류 처리 | 충분 | `final.md` 12장이 오류 상태 제거, 예외, 추상화 수준, 계약, assertion/오류 처리를 다룬다. |
| 레거시 리뷰 | 충분 | `final.md` 16장이 seam, sprout method, wrap method, characterization test를 다룬다. |
| 유지보수성 | 충분 | `final.md` 1장, 7장, 15장, 17장이 복잡성, 변경 증폭, cognitive load, refactoring process를 다룬다. |
| Fat Model/View/Router | 부족 | `final.md`에는 generic `RequestRouter` 예시는 있으나 Django/dddjango에서 model/view/router/schema/template에 비즈니스 규칙이 흩어지는 경우를 판정하는 전용 기준이 없다. runtime skill은 이 범위를 명시하므로 source reference가 직접 근거를 제공해야 한다. |

## 원인

- 현재 reference는 범용 클린 코드 원칙을 충분히 제공하지만, dddjango 플러그인의 clean-code skill이 실제로 라우팅하는 Django 유지보수성 사례를 source reference가 직접 뒷받침하지 못한다.
- 특히 Fat Model, Fat View, Fat Router, schema/template business logic, service/selector로의 단순 이동이 항상 정답은 아니라는 판단 기준이 빠져 있다.

## 영향

- skill이 Fat View/Router 비즈니스 로직을 다루는 것은 현재 runtime 목적과 맞지만, source reference만으로는 그 런타임 지침의 provenance가 약하다.
- reference 문제가 있는데 skill만 보강하면 P1 금지 사항인 "reference 문제가 있는데 skill만 수정"에 해당한다.

## 리뷰 방식과 결과

리뷰 방식: real-subagent
- Subagent 리뷰/순차 fallback: real-subagent 결과를 재평가에 통합했다. reference gap을 먼저 닫은 뒤 skill-creator 관점과 독립 P1 감사 관점 리뷰를 수행했다.
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
- 초기 Major 1: Django/ddjango 특화 Fat Model/View/Router 판단 기준이 source reference에 없었다.
- 재평가: source reference 보강 후 독립 subagent가 reference sufficient로 판정했다. 남은 Blocker, Major, 열린 Minor는 없다.

## 결론

`workspace/reference/implementation-cleancode/reference/final.md`에 Django/dddjango 유지보수성 판단 기준을 추가한다. 범용 원칙은 충분하므로 전체 구조를 다시 쓰지 않고, 책임 분리와 리팩토링 사이에 framework boundary smell을 판단할 수 있는 작은 절을 추가한다.
