---
name: implementation-django-ninja
description: Django Ninja JSON API 어댑터 구현 지식 — Router/Schema/Operation, 인증·인가, 필터링·정렬·페이지네이션, Problem Details·상태 코드 매핑, Idempotency-Key, OpenAPI 계약 확인, TestClient HTTP 계약 검증, DRF-to-Ninja 마이그레이션. Router·Schema·API 어댑터 코드를 새로 작성하거나 리팩터링할 때 먼저 로드한다. REST 계약 설계는 architecture-api, 도메인 규칙·구조 패턴은 architecture-ddd, Django ORM·서비스·트랜잭션은 implementation-django, 테스트 픽스처·더블 구현은 implementation-test로 위임.
user-invocable: false
---

# Django Ninja JSON API 구현

## 언제 쓰나

Django Ninja Router/Schema/Operation·인증·필터링·페이지네이션·Problem Details·OpenAPI·TestClient 코드를 설계·작성할 때 로드한다. 경계:

- REST 리소스·URL·HTTP 메서드·상태 코드·헤더·콘텐츠 협상·버전·레이트리밋·idempotency 계약(키 정책) → `architecture-api` (idempotency 저장소·retention은 `architecture-db`)
- 애그리거트·상태 전이·불변식·유스케이스 경계·구조 패턴(repository/UoW/핵사고날/CQRS/outbox/ACL) → `architecture-ddd`
- ORM 쿼리·셀렉터·서비스·트랜잭션·마이그레이션·캐시·보안 구현 → `implementation-django`
- pytest 픽스처·팩토리·mock·테스트더블·동시성 테스트 구현 → `implementation-test`

## 핵심 운영 원칙

- Router는 HTTP 어댑터로 얇게: 요청 바인딩·auth hook·서비스 호출·응답 매핑만 (§1.3)
- Request/Response schema는 명시적으로 분리, ModelSchema는 내부 구현 보호가 확실할 때만 (§3.1–§3.2)
- 에러도 status별로 `response={...}`에 schema로 선언하고 `(status, schema)` 튜플로 반환 — operation 본문에서 수제 HttpResponse로 매핑을 우회하지 않는다(OpenAPI 미노출 방지). Problem Details RFC 9457 변환 (§2.2·§6.2)
- operation은 `summary`·`description`·`tags`로 문서화하고 반환 타입을 명시한다(`object` 금지) (§2.2)
- Idempotency-Key는 계약에 정의된 endpoint에만; 키 정책(scope·replay·conflict)은 `architecture-api`, 저장소·retention(테이블·unique constraint·fingerprint)은 `architecture-db`가 결정 (§7)
- 계약이 바뀌면 OpenAPI 생성 결과를 확인 (§8)
- 신규 API는 Django Ninja 목표, DRF는 legacy·migration 맥락에서만 보조 (§10)
- 라우팅 결정 전 계약·DB·도메인이 미결이면 각 소유 스킬 먼저 (§11)

## 상세 레퍼런스

주제별로 [`references/final.md`](references/final.md)의 해당 절을 따른다:

| 주제 | 절 |
|---|---|
| 책임 범위와 위임 경계·Router thinness 원칙 | §1 |
| Router 등록·Operation 선언 | §2 |
| Schema와 ModelSchema (request/response 분리·resolver) | §3 |
| 인증과 인가 | §4 |
| Filtering, sorting, pagination | §5 |
| 상태 코드와 Problem Details | §6 |
| Idempotency-Key | §7 |
| OpenAPI | §8 |
| TestClient와 검증 | §9 |
| DRF-to-Ninja 마이그레이션 | §10 |
| 라우팅 기준(스킬 선택 결정 트리) | §11 |

각 절은 [`references/final.md`](references/final.md)에서 필요한 항목만 읽는다(전체 로드 불필요).
