수정 대상: reference
원인 분류: source gap
대상: implementation-django-ninja
생성 시각: 2026-05-21 20:48:29 KST
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

## 최초 평가

`workspace/reference/implementation-django-ninja/reference/final.md`가 없어서
`implementation-django-ninja` skill이 전용 source reference 없이 runtime bundled
reference와 fallback source에 의존하고 있었다. 현재 source skill의 frontmatter와 본문도
전용 source 부재를 전제로 `provisional`이라고 설명한다.

P1 기준에서 source reference는 Django Ninja Router, Schema, endpoint, auth/permission,
pagination, filtering/sorting, Problem Details, OpenAPI, TestClient, DRF-to-Ninja
migration을 판단할 수 있어야 한다. reference area 자체가 없으므로 이 조건을 만족하지
못한다.

## 부족 항목

| 항목 | 현재 상태 | 영향 |
|---|---|---|
| Router/endpoint 기준 | 전용 source 없음 | Router thinness와 operation mapping 기준이 runtime에만 남음 |
| Schema/ModelSchema 기준 | 전용 source 없음 | request/response 분리와 model field 노출 기준의 source 추적 불가 |
| Auth/permission | architecture-api fallback뿐 | Django Ninja auth 연결과 401/403 mapping 기준 부족 |
| Filtering/sorting/pagination | runtime reference뿐 | FilterSchema/Query/pagination decorator 사용 기준의 source 부재 |
| Problem Details | architecture-api fallback뿐 | Django Ninja exception handler 연결 기준 부족 |
| OpenAPI | runtime reference뿐 | generated schema 검증 기준의 source 부재 |
| TestClient | runtime reference뿐 | Ninja TestClient scope와 보고 기준의 source 부재 |
| DRF-to-Ninja migration | runtime reference뿐 | greenfield DRF 요청 변환 기준의 source 부재 |

## 최초 판정

Blocker 1: 전용 source reference가 없으므로 skill 수정만으로 P1을 닫을 수 없다.

## 수정

`workspace/reference/implementation-django-ninja/reference/final.md`를 생성했다. 새 reference는
Django Ninja Router, endpoint operation, Schema/ModelSchema, auth/permission,
filtering/sorting, pagination, Problem Details/RFC 9457, Idempotency-Key, OpenAPI,
TestClient 검증, DRF-to-Ninja migration을 다룬다. REST contract, DB/transaction,
ORM/service, pytest fixture/test-double 세부 구현은 각 전용 source reference로 위임했다.

## 재평가

수정 후 독립 review 2건 모두 reference sufficiency 관련 Blocker 0, Major 0, 열린 Minor 0으로
판정했다. Review note는 bundled runtime reference가 source detail을 일부 압축한다는 수준이며
P1 closure를 막는 open Minor는 아니다.

최종 판정: Blocker 0, Major 0, 열린 Minor 0.

## Subagent 리뷰/순차 fallback

Subagent 리뷰를 실행했다. 수정 전 review는 dedicated source reference 부재를 Blocker로
확인했다. 수정 후 review 2건은 source reference가 P1 범위에 충분하다고 판정했다.

## skill-creator 리뷰

수정 전 reference 부재는 skill-creator 관점에서도 validation integrity 문제였다. 수정 후
source reference가 생겼고 runtime skill은 source보다 많은 결정을 임의로 담지 않도록 경계를
분리했다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`: 통과
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`: 통과
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: 통과
