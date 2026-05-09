# dddjango Spec

## 관련 문서

- [Reference Index](reference-index.md)
- [DDD Implementation Standard](ddd-implementation-standard.md)
- [Skill Hierarchy](skill-hierarchy.md)
- [Skill Contracts](skill-contracts.md)
- [Workflow](workflow.md)
- [Validation Plan](validation-plan.md)
- [Plugin Structure](plugin-structure.md)
- [Skill Authoring Inputs](skill-authoring.md)

## 1. 목표

`dddjango`는 DDD 기반 애플리케이션을 Python/Django 생태계에서 일관되게 구현하기 위한 Claude Code와 Codex 공통 플러그인이다.

핵심 목표는 에이전트가 구현 세부에 바로 뛰어들지 않고, 먼저 도메인 경계, 유비쿼터스 언어, 애그리거트, 불변식, 유스케이스를 정리한 뒤 이를 Django ORM, application service, selector, Django Ninja API, pytest 테스트로 매핑하게 만드는 것이다.

`dddjango`의 API 구현 표준은 Django Ninja로 둔다. DRF는 신규 구현 표준이 아니라 레거시 코드 리뷰, 마이그레이션, 비교 참고 자료로만 다룬다.

단순 CRUD나 지원 하위 도메인에는 Django다운 최소 구조를 유지하고, 복잡한 도메인 규칙이 있는 작업에는 DDD 모델링과 구현 아키텍처 패턴을 필요한 만큼 적용한다.

복합적이거나 위험한 작업에는 역할 분해와 전문 스킬 조합으로 도메인 모델, 구현 매핑, 데이터 모델, API 계약, 테스트, 리뷰를 통합한다.

Claude Code와 Codex 양쪽에서 같은 요청에 대해 같은 설계 결론과 같은 구현 기준을 따르게 한다.

## 2. 설계 원칙

전략 설계가 전술 패턴보다 먼저다.

하위 도메인, 바운디드 컨텍스트, 컨텍스트 맵, 유비쿼터스 언어를 먼저 판단하고, 그 다음에 애그리거트, 엔티티, 값 객체, repository, service, event 같은 전술 패턴을 적용한다.

Core domain에는 도메인 모델의 표현력과 불변식 보호를 우선한다. Supporting domain이나 단순 CRUD에는 Django 모델, QuerySet, service 함수 중심의 간단한 구조를 허용한다. Generic domain에는 외부 솔루션이나 기존 라이브러리 사용을 우선 고려한다.

애그리거트는 불변식을 지키는 최소 경계로 잡는다. 하나의 트랜잭션에서 여러 애그리거트를 동시에 바꾸는 설계는 기본 선택이 아니며, 필요한 경우 도메인 이벤트, eventual consistency, outbox 같은 패턴을 별도로 검토한다.

Django ORM 모델과 도메인 모델은 항상 분리하지 않는다. 불변식이 단순하고 Django 모델만으로 충분히 표현되면 Django 모델을 도메인 객체로 사용할 수 있다. 반대로 도메인 규칙이 ORM, HTTP, 외부 SDK, 프레임워크 세부사항에 묶이면 도메인 객체와 인프라 구현을 분리한다.

API 계층은 유스케이스를 외부에 노출하는 adapter다. Django Ninja Router는 요청 검증, 인증/인가 연결, 유스케이스 호출, 응답 변환을 담당하고, 핵심 비즈니스 규칙을 소유하지 않는다.

테스트는 구현 후 확인용만이 아니라 도메인 규칙과 API 계약을 명세하는 수단이다. 도메인 규칙, 상태 전이, 정책이 있는 작업은 테스트 목록과 실패 테스트를 먼저 고려한다.

## 3. 스킬 종류

### Core DDD

- `architecture-ddd`: 하위 도메인, 바운디드 컨텍스트, 유비쿼터스 언어, 컨텍스트 맵, 애그리거트, 값 객체, 불변식, 도메인 이벤트를 다룬다.
- `architecture-implementation-patterns`: DDD 모델을 코드 구조로 옮기기 위한 layered architecture, hexagonal architecture, clean architecture, ports/adapters, repository, CQRS, event sourcing, outbox, dependency inversion, anti-corruption layer를 다룬다.

### Implementation Mapping

- `implementation-django`: 도메인 모델과 유스케이스를 Django model, ORM, QuerySet, Manager, service, selector, migration, transaction, Django test 관용구로 매핑한다.
- `implementation-django-ninja`: 유스케이스와 API 계약을 Django Ninja Schema, Router, auth, pagination, FilterSchema, Problem Details, TestClient로 구현한다.
- `implementation-django-web`: Django template, static files, base template, component include, CSS/JS, TemplateView, HTMX, CSRF for AJAX를 다룬다.
- `implementation-python`: 도메인 개념과 구현 계약을 Python 타입 힌트, dataclass, Protocol, Enum, pydantic v2, async, 예외 처리, Ruff/typecheck 기준으로 표현한다.

### Supporting Architecture

- `architecture-db`: 도메인 모델을 지지하는 관계형 데이터 모델링, 정규화, 제약조건, 인덱스, 트랜잭션, 격리 수준, 쿼리 성능, 운영 마이그레이션 전략을 다룬다.
- `architecture-api`: 도메인 유스케이스를 외부에 노출하는 REST 리소스, URL 구조, HTTP 메서드, 상태 코드, Problem Details, 페이지네이션, 버전 관리, 하위 호환성, rate limiting, idempotency key, OpenAPI 계약을 다룬다.

### Quality

- `implementation-cleancode`: 책임 분리, 이름, 함수, 캡슐화, SOLID, 추상화, 중복 판단, 주석, 리팩터링, 레거시 코드 리뷰를 다룬다.
- `implementation-tdd`: 도메인 규칙을 테스트 목록, Red-Green-Refactor, Inside-Out/Outside-In, AI 보조 TDD 흐름으로 명세화한다.
- `implementation-test`: 도메인 불변식과 유스케이스를 검증하는 pytest, fixture, test double, mock, factory, property-based testing, testcontainers, coverage, mutation testing, 테스트 냄새를 다룬다.

### Workflow

- `workflow-dddjango-subagents`: 복합 DDD/Django 작업의 역할 분해, subagent 조정, 순차 실행 fallback, 결과 통합을 다룬다.

## 4. 산출물 기준

`dddjango`가 만드는 산출물은 도메인 판단과 구현 판단이 분리되어 추적 가능해야 한다.

설계 산출물은 도메인 경계, 용어, 컨텍스트 맵 관계 패턴, 통합 방식, 애그리거트, 불변식, 유스케이스, 트랜잭션 경계, API 계약, 데이터 제약을 명시해야 한다.

구현 산출물은 Django/Python 관용구를 따르되, 비즈니스 규칙이 HTTP adapter, serializer/schema, ORM 쿼리 세부사항, 외부 SDK에 흩어지지 않게 해야 한다.

검증 산출물은 테스트 결과, diff, 로그, 실행 출력, 리뷰 findings 같은 실제 artifact를 우선한다. 실행하지 않은 검증을 완료했다고 말하지 않는다.
