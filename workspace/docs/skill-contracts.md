# Skill Contracts

이 문서는 각 스킬의 책임 계약을 정의한다. 트리거 문서가 아니라, 스킬을 만들 때 흔들리지 않아야 하는 책임과 경계 문서다.

## `source-reference-audit`

책임:

- `workspace/docs`, `workspace/reference`, runtime bundled references 사이의 source-of-truth 관계를 점검한다.
- source provenance, conflict/gap decision, provisional/fallback source status, validation coverage, eval traceability, source/runtime boundary를 리뷰한다.
- source gap이나 provisional 영역에서 주장 가능한 내용과 주장하면 안 되는 내용을 구분한다.

입력:

- source/reference 감사 요청
- `workspace/docs` 문서
- `workspace/reference/*/reference/{final,review,internal,external}.md`
- runtime `dddjango/skills/*/SKILL.md`와 `references/*.md`
- 허용된 경우 eval public/answer 쌍과 validation artifact

출력:

- source inventory 또는 provenance crosswalk
- conflict/gap/provisional ledger with item status, source evidence, allowed claim, forbidden claim, and closure work
- validation coverage map with scenario/dimension, source basis, `coverage_tags`, expected evidence, gap/residual risk, and negative/honesty check columns
- eval traceability map that ties each bucket `eval_goal.md` to per-case `reference_basis` and `coverage_tags`
- source/runtime boundary와 leakage risk
- 실행한 검증과 실행하지 못한 검증

경계:

- 도메인/API/DB/Django 구현 결정을 대신 내리지 않는다.
- private oracle, prior run output, scoring note를 runtime skill, public case, source docs로 옮기지 않는다.
- source reference 본문을 runtime `SKILL.md`에 복사하지 않는다.

## `architecture-ddd`

책임:

- 하위 도메인 유형을 판단한다.
- 바운디드 컨텍스트와 컨텍스트 맵을 정리한다.
- 유비쿼터스 언어를 정리한다.
- 애그리거트, 엔티티, 값 객체, 불변식, 도메인 이벤트를 식별한다.

입력:

- 비즈니스 문제
- 기존 코드 또는 요구사항
- 도메인 용어
- 상태 전이와 정책

출력:

- 하위 도메인 판단
- 바운디드 컨텍스트
- 컨텍스트 맵 패턴, 방향성, 통합 방식, 선택 이유
- 핵심 용어
- 애그리거트 후보와 불변식
- 도메인 이벤트 후보, dispatch timing, consistency boundary
- 유스케이스 후보

경계:

- Django model, Router, migration 코드 구현을 직접 소유하지 않는다.
- 전략 설계 없이 전술 패턴부터 강제하지 않는다.

## `architecture-implementation-patterns`

책임:

- DDD 모델을 구현 구조로 옮길 아키텍처 패턴을 선택한다.
- layered, hexagonal, clean architecture, ports/adapters, repository, CQRS, outbox, ACL, UoW 같은 패턴의 적용 여부를 판단한다.
- 의존성 방향과 경계를 정한다.

입력:

- DDD 모델
- 유스케이스
- 외부 시스템
- 일관성 요구
- 기존 코드 구조

출력:

- 추천 구조
- 의존성 방향
- port/adapter 경계
- 적용하지 않을 패턴의 이유

경계:

- 모든 작업에 repository, interface, UoW를 강제하지 않는다.
- 단순 CRUD에 과한 구조를 만들지 않는다.

## `architecture-db`

책임:

- 도메인 모델을 지지하는 관계형 데이터 모델을 설계한다.
- 정규화, PK/FK, unique, check, not null, cascade, index, transaction, isolation을 판단한다.
- 운영 rollout 제약, backfill 위험, index lock 위험을 검토한다.

입력:

- 애그리거트와 엔티티
- 불변식
- 조회 패턴
- 쓰기 경합과 동시성 위험
- 마이그레이션 제약

출력:

- ERD/테이블 후보
- 제약조건
- 인덱스
- 트랜잭션/locking 기준
- rollout constraints, backfill/index-lock risk, rollback 고려사항

경계:

- Django migration 파일의 세부 구현은 `implementation-django`가 담당한다.
- ORM convenience만 보고 DB invariant를 포기하지 않는다.
- `RunPython`, `apps.get_model()`, `sqlmigrate`, migration 파일 작성은 담당하지 않는다.

## `architecture-api`

책임:

- 도메인 유스케이스를 REST API 계약으로 설계한다.
- resource, URL, HTTP method, status code, error, pagination, versioning, idempotency, OpenAPI 계약을 판단한다.

입력:

- 유스케이스
- 외부 클라이언트 요구
- 인증/인가 요구
- 오류 조건
- 호환성 요구

출력:

- endpoint 목록
- request/response contract
- status code
- Problem Details 오류 형식
- idempotency/versioning/pagination 기준
- OpenAPI schema/spec 영향

경계:

- Django Ninja 구현 세부는 `implementation-django-ninja`가 담당한다.
- 도메인 규칙을 API 계층으로 이동시키지 않는다.

## `implementation-django`

책임:

- 확정된 도메인 모델과 유스케이스를 Django model, ORM, QuerySet, Manager, service, selector, migration, transaction으로 구현한다.
- Django 성능, 보안, 설정, 구체적인 migration 파일 구현, 테스트 관용구를 적용한다.

입력:

- DDD 모델
- DB 설계
- 유스케이스
- 기존 Django 코드

출력:

- Django model/manager/queryset/service/selector 코드
- migration
- `RunPython`, `apps.get_model()`, `sqlmigrate`, `AddIndex`, expand/backfill/contract 구현
- transaction 처리
- Django 통합 테스트 acceptance criteria. 복합 workflow에서 테스트 파일 소유는 기본적으로 Test Agent가 맡는다.

경계:

- 핵심 비즈니스 규칙을 view, form, serializer/schema, signal에 흩어놓지 않는다.
- domain/application 판단 없이 Django 구조부터 만들지 않는다.

## `implementation-django-ninja`

책임:

- API 계약을 Django Ninja Router, Schema, auth, pagination, FilterSchema, Problem Details, TestClient로 구현한다.
- DRF 기반 신규 구현 요청은 Django Ninja 기준으로 전환한다.

입력:

- API 계약
- 유스케이스
- auth/permission 요구
- 오류 정책

출력:

- Router
- Schema/ModelSchema
- API error handling
- OpenAPI schema/spec 영향
- API test acceptance criteria. 복합 workflow에서 테스트 파일 소유는 기본적으로 Test Agent가 맡는다.

경계:

- Router에 비즈니스 규칙을 두지 않는다.
- DRF ViewSet/Serializer/APIView를 신규 표준으로 만들지 않는다.

## `implementation-django-web`

책임:

- Django template/static/frontend 작업을 구현한다.
- TemplateView, base template, include, static files, CSS/JS, HTMX, CSRF for AJAX를 다룬다.

입력:

- 화면 요구사항
- Django view/context
- static/template 구조

출력:

- template
- static asset
- view/context 코드
- 웹 테스트 또는 렌더링 확인

경계:

- API 구현 책임을 가져오지 않는다.
- 도메인 규칙을 template에 두지 않는다.

## `implementation-python`

책임:

- Python 타입과 언어 기능으로 도메인 개념과 구현 계약을 명확히 표현한다.
- 타입 힌트, dataclass, Enum, Protocol, modern Python, 예외 처리를 다룬다.

입력:

- 도메인 개념
- 함수/클래스 계약
- 기존 Python 코드

출력:

- 명시적 타입 계약
- `X | None`, built-in generics, Enum/StrEnum, dataclass, Protocol 적용 판단
- pydantic v2 boundary 판단
- Pythonic implementation
- Ruff/typecheck 친화 코드

경계:

- pydantic v2를 도메인 모델의 기본값으로 강제하지 않는다.
- 외부 입력 검증과 도메인 불변식을 혼동하지 않는다.

## `implementation-tdd`

책임:

- 도메인 규칙과 API 계약을 테스트 목록과 Red-Green-Refactor 흐름으로 명세화한다.
- Inside-Out/Outside-In 접근을 상황에 맞게 선택한다.

입력:

- 도메인 규칙
- 유스케이스
- 위험 조건
- API 계약

출력:

- 테스트 목록
- 실패 테스트
- 작은 구현 단계
- 리팩터링 체크포인트
- Test Agent가 소유할 테스트 파일 요구사항

경계:

- 테스트 작성법의 세부 도구 설명은 `implementation-test`가 담당한다.
- 테스트 없이 구현 완료를 주장하지 않는다.

## `implementation-test`

책임:

- pytest 기반 테스트 코드를 작성하고 품질을 검토한다.
- fixture, test double, mock, fake, factory, property-based testing, coverage, mutation testing을 다룬다.

입력:

- 테스트 대상 코드
- 검증해야 할 invariant
- 외부 의존성
- 테스트 실행 환경

출력:

- pytest test
- fixture/factory
- test double
- coverage 또는 mutation testing 제안
- 복합 workflow에서 `tests/**`, `conftest.py`, factory 파일 소유

경계:

- Mock을 모든 협력에 기본 적용하지 않는다.
- 테스트가 구현 세부에 과하게 결합되지 않게 한다.

## `implementation-cleancode`

책임:

- 책임 분리, 이름, 함수, 캡슐화, 추상화, 오류 처리, 중복, 리팩터링, 레거시 코드 리뷰를 담당한다.
- 도메인 규칙이 읽히고 보호되는 구조인지 검토한다.

입력:

- 기존 코드
- 변경 목표
- 도메인 판단
- 테스트 결과

출력:

- 리팩터링 제안
- 코드 변경은 Coordinator가 명시적으로 배정한 경우에만 직접 수행한다.
- 리뷰 findings
- 품질 위험

경계:

- 스타일 취향을 도메인 구조 판단보다 앞세우지 않는다.
- 성급한 추상화를 만들지 않는다.

## `workflow-dddjango-subagents`

책임:

- 복합 DDD/Django 작업을 역할로 나누고 결과를 통합한다.
- subagent를 사용할 수 있으면 실제로 위임하고, 사용할 수 없으면 같은 역할 순서로 순차 실행한다.

입력:

- 복합 작업 요청
- 기존 코드/문서
- 위험 요소
- 필요한 스킬 후보

출력:

- 역할 분해
- handoff contract
- 통합 판단
- 최종 구현/리뷰 결과

경계:

- 실제로 subagent를 사용하지 않았는데 사용했다고 말하지 않는다.
- 단순 작업에 역할 분해를 과하게 적용하지 않는다.

## 공통 필수 출력

### Risky Write Consistency Block

주문, 결제, 재고, 예약, 환불, 권한, ledger처럼 위험한 쓰기 작업에서는 관련 역할이 다음 항목을 남긴다.

- transaction owner
- locking 전략
- uniqueness 또는 idempotency 저장 위치
- `Idempotency-Key` API 동작
- 외부 side effect의 `transaction.on_commit()` 또는 domain event 처리
- isolation/retry 판단
- 통합 테스트 또는 동시성 테스트 기준
