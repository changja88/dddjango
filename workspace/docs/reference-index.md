# Reference Index

이 문서는 `workspace/reference` 아래의 기존 reference가 어떤 설계 결론의 근거인지 정리한다. 스킬 개발 전에는 이 문서를 기준으로 어떤 reference를 읽어야 하는지 판단한다.

## Architecture

| 영역 | 주요 문서 | 기준으로 삼을 내용 |
|---|---|---|
| DDD | `workspace/reference/architecture-ddd/reference/final.md` | 전략 설계 우선, 하위 도메인 유형, 바운디드 컨텍스트, 유비쿼터스 언어, 컨텍스트 맵, 애그리거트, 도메인 이벤트 |
| Implementation Patterns | 전용 source reference 필요. 임시로 `architecture-ddd/reference/final.md`, `implementation-django/reference/final.md`, `implementation-python/reference/final.md`를 조합 | layered/hexagonal/clean architecture, ports/adapters, repository, CQRS, outbox, ACL, 의존성 방향 |
| DB | `workspace/reference/architecture-db/reference/final.md` | 개념/논리/물리 모델링, 정규화, 제약조건, 인덱스, 트랜잭션, 격리 수준, 쿼리 최적화 |
| API | `workspace/reference/architecture-api/reference/final.md` | REST 리소스, HTTP 메서드, 상태 코드, RFC 9457 Problem Details, 인증/인가, 페이지네이션, 버전 관리, rate limiting, idempotency key, OpenAPI |

## Implementation

| 영역 | 주요 문서 | 기준으로 삼을 내용 |
|---|---|---|
| Django | `workspace/reference/implementation-django/reference/final.md` | Django 설계 철학, 모델/QuerySet/Manager, 뷰, 마이그레이션, 성능, 보안, 테스트, 서비스 레이어 |
| Django Ninja | 전용 source reference 필요. 임시로 `architecture-api/reference/final.md`와 사용자 제품 결정을 조합 | Router, Schema/ModelSchema, auth, pagination, FilterSchema, Problem Details, OpenAPI, TestClient |
| Django Web | 전용 source reference 필요. 임시로 `implementation-django/reference/final.md`의 template/view/static 관련 내용을 조합 | template inheritance, static files, TemplateView, component include, HTMX, CSRF for AJAX |
| Python | `workspace/reference/implementation-python/reference/final.md` | 타입 힌트, Optional/Union, dataclass, Protocol, modern Python, 명시적 타입 계약 |
| Clean Code | `workspace/reference/implementation-cleancode/reference/final.md` | 이름, 함수, 캡슐화, 깊은 모듈, SOLID, 오류 처리, 중복, 리팩터링, 레거시 코드 |
| TDD | `workspace/reference/implementation-tdd/reference/final.md` | Red-Green-Refactor, 고전/런던 학파, Inside-Out/Outside-In, 테스트 우선 설계 |
| Test | `workspace/reference/implementation-test/reference/final.md` | 테스트 피라미드, pytest, fixture, test double, mock, factory, property-based testing, coverage, mutation testing |
| Workflow | 생성 전 authoring source: `workspace/docs/workflow.md`; 생성 후 runtime bundled reference: `dddjango/skills/workflow-dddjango-subagents/references/` | 역할 분해, handoff contract, sequential fallback, integration priority |

## Reference 사용 원칙

`final.md`는 스킬 설계의 기본 근거로 사용한다.

`internal.md`와 `external.md`는 `final.md`의 결론이 애매하거나, 특정 개념의 원출처와 세부 논거가 필요할 때만 읽는다.

`review.md`는 reference 자체의 선택과 정리 과정에서 어떤 이견이 있었는지 확인할 때 사용한다.

스킬의 `SKILL.md`에는 reference의 긴 설명을 복사하지 않는다. 핵심 절차와 판단 기준만 두고, 상세 지식은 해당 스킬의 `references/`로 분리한다.

## Reference Gap

다음 first-class skill은 현재 전용 source reference가 부족하다.

| Skill | 처리 |
|---|---|
| `architecture-implementation-patterns` | 전용 source reference를 만들기 전까지 DDD, Django, Python reference에서 필요한 패턴만 조합한다. |
| `implementation-django-ninja` | 전용 Django Ninja source reference가 필요하다. 만들기 전까지 DRF 문서를 신규 구현 근거로 사용하지 않는다. |
| `implementation-django-web` | 전용 Django Web source reference가 필요하다. 만들기 전까지 Django reference의 template/static/view 부분만 사용한다. |
| `workflow-dddjango-subagents` | `workspace/docs/workflow.md`를 source로 삼고, 이후 `dddjango/skills/workflow-dddjango-subagents/references/`로 runtime reference를 생성한다. |

전용 source reference가 부족한 skill은 최종 authoring 전에 source reference를 만들거나, `skill-authoring.md`에서 provisional skill로 표시한다.

## DRF Guardrail

`implementation-django/reference/final.md`의 DRF 섹션은 신규 API 구현 지침이 아니다.

DRF 관련 내용은 다음 경우에만 사용한다.

- 레거시 코드 리뷰
- DRF-to-Django-Ninja 마이그레이션
- 기존 DRF API와 Django Ninja 구현의 비교
- 하위 호환성 영향 분석

신규 API 구현은 `implementation-django-ninja` 기준으로 작성한다.

## Reference에서 도출한 제품 결정

| 결정 | 근거 |
|---|---|
| DDD 전략 설계를 전술 패턴보다 먼저 둔다 | `architecture-ddd/reference/final.md` |
| Core/Supporting/Generic 하위 도메인에 따라 구현 강도를 달리한다 | `architecture-ddd/reference/final.md` |
| 관계형 DB 설계는 도메인 불변식을 지지하는 방향으로 한다 | `architecture-db/reference/final.md` |
| API 설계는 REST와 RFC 9457 Problem Details를 기준으로 한다 | `architecture-api/reference/final.md` |
| 신규 API 구현 표준은 Django Ninja로 둔다 | 사용자 제품 결정. 전용 Django Ninja source reference가 필요하다. |
| Django 구현은 Django 철학을 따르되 복잡한 도메인에서는 서비스/경계 분리를 허용한다 | `implementation-django/reference/final.md`, DDD reference |
| 테스트는 TDD와 pytest 기준을 함께 사용한다 | `implementation-tdd/reference/final.md`, `implementation-test/reference/final.md` |
