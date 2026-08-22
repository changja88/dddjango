---
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->
name: architecture-api
description: REST/HTTP API 계약 설계 지식 — 리소스·메서드 의미론, 요청/응답 계약, 상태 코드, dddjango-code-json 기본과 선택형 RFC 9457 에러 프로필, 페이지네이션·버전관리·하위 호환성·Rate Limiting·멱등성 키·OpenAPI. REST/HTTP 계약(엔드포인트 설계, 상태 코드 선택, 에러 프로필, 버전·하위 호환성 결정, OpenAPI 반영)을 새로 정의하거나 변경할 때 먼저 로드한다. JSON 직렬화·라우터 구현은 implementation-django-ninja, 서버렌더 표현계층은 implementation-django-web, 도메인 모델·애그리거트는 dddjango:architecture-ddd, 데이터 신뢰성·트랜잭션은 architecture-db로 위임.
user-invocable: false
---

# REST API 계약 설계

## 언제 쓰나
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

REST API 계약(리소스 설계, HTTP 메서드 의미론, 상태 코드, 요청/응답 본문·헤더, 에러 형식, 페이지네이션, 버전 관리, 하위 호환성, Rate Limiting, 멱등성 키, OpenAPI)을 결정하거나 변경할 때 로드한다. 경계:

- JSON 직렬화·Router·Schema 구현 → `implementation-django-ninja`
- 서버렌더 표현계층(템플릿·폼·HTMX) → `implementation-django-web`
- 도메인 전략·애그리거트·경계 설계 → `architecture-ddd`
- 데이터 신뢰성·트랜잭션·outbox 전달 → `architecture-db`
- Django ORM·서비스 레이어 구현 → `implementation-django`

## 핵심 운영 원칙
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- RFC 9110 HTTP 의미론 우선: 메서드 안전성·멱등성을 정확히 지키고, PUT은 전체 교체, PATCH는 부분 수정, POST는 non-idempotent 생성으로 구분 (§2)
- URL은 명사·복수형·케밥케이스 리소스로 설계하고 동사 행위를 URL에 포함하지 않는다 (§3)
- 에러 프로필은 기존 배포 계약을 먼저 보존하고, 새 dddjango Ninja 범위에는 `dddjango-code-json`(`application/json` + 별도로 승인된 프로젝트별 exact 오류 schema shape + BC `ErrorCode`)을 선택한다. 플러그인 기본 property 목록은 없으며 shape 변경은 별도 사용자 승인이 필요하다. RFC 9457 Problem Details는 별도 요구가 있을 때만 선택하고 두 프로필의 wire 필드는 한 범위에서 섞지 않는다 — 혼합 금지의 주어는 wire 필드다: **신규 범위**는 RFC 9457 wire 를 선택해도 표준 controller 레시피로 구현하고(preserve-established 범위는 native 보존 관할 — 이 문장의 대상 아님), 이 조합의 G2 게이트 취급은 아직 profile 열거에 없어 채택 시 G1 표면화(STOP) 대상이다 (§5.4, §6)
- 요청/응답 계약은 상태 코드별 body·header·schema까지 포함해 명시적으로 기록하고, 계약 체크리스트(Resource·Method·Request·Response·Error·Auth·Compatibility·OpenAPI)를 엔드포인트 변경마다 검토한다 (§5)
- 페이지네이션은 데이터 특성(정렬 안정성, 실시간성, 딥 페이지 여부)에 따라 오프셋·커서·페이지 방식 중 선택하고 선택 기준을 명시한다 (§9)
- 버전 전략(URL·헤더·쿼리파라미터)과 하위 호환성·Deprecation 프로세스를 API 변경 전에 결정한다 (§10, §11)
- duplicate-sensitive 요청(결제·생성)에는 `Idempotency-Key` 정책(scope·replay·conflict 계약)을 함께 정한다 (§13)
- 모든 계약 결정은 OpenAPI에 반영한다 — path·method·schema·response·security·header를 빠짐없이 기술한다 (§14)

## 상세 레퍼런스
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

주제별로 [`references/final.md`](references/final.md)의 해당 절을 따른다:

| 주제 | 절 |
|---|---|
| REST 아키텍처 원칙 | §1 |
| HTTP 메서드와 멱등성 | §2 |
| URL/리소스 설계 규칙 | §3 |
| HTTP 상태 코드 | §4 |
| 요청/응답 계약 | §5 |
| 에러 프로필 선택 / RFC 9457 프로필 | §5.4 / §6 |
| HTTP 헤더와 콘텐츠 협상 | §7 |
| 인증과 인가 | §8 |
| 페이지네이션 | §9 |
| 버전 관리 | §10 |
| 하위 호환성과 Deprecation | §11 |
| Rate Limiting | §12 |
| 멱등성 키 (Idempotency-Key) | §13 |
| OpenAPI | §14 |

각 절은 [`references/final.md`](references/final.md)에서 필요한 항목만 읽는다(전체 로드 불필요).
