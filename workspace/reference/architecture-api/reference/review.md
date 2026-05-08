# API 설계 원칙 Internal vs External 리뷰

> Internal: Go_Deeper/Wiki/REST&SOAP [REST], Go_Deeper/Wiki/Http [HTTP], Go_Deeper/Book/Architecture/DesigningAPIS [API Book]
> External: Microsoft/Google API Design Guide [MS/G], Stripe Blog/Docs [Stripe], IETF RFC 9457 [RFC], GitHub Docs [GH], restfulapi.net [RA], Wikipedia/Ben Morris [Wiki]

---

## A. Conflicts (상호 충돌)

### [A-1] REST 정의의 깊이 차이

**상충 유형**: 관점 불일치

| | Internal | External |
|---|---------|----------|
| 출처 | Go_Deeper/Wiki/REST&SOAP [REST] | Microsoft/Google API Design Guide [MS/G], restfulapi.net [RA] |
| 주장 | REST를 학술적으로 정의 (로이 필딩 논문, ROA, 무상태 원칙). "표준이 없다", "메서드가 4개뿐" 등 한계점을 명시 | URL 설계 규칙, HTTP 메서드-리소스 매트릭스, 필터링/정렬/페이지네이션 패턴 등 실전 설계 규약에 집중. REST의 한계를 언급하지 않음 |

**분석**: 직접 모순은 아니다. Internal은 REST의 본질("아이디어 모음")과 한계를 강조하는 학술적 관점이고, External은 REST를 이미 전제로 놓고 "어떻게 잘 설계하는가"를 다룬다. Internal의 "메서드가 4개뿐"이라는 서술은 External의 메서드 매트릭스(HEAD, OPTIONS 등 포함하면 더 많음)와 약간의 긴장이 있다.

**추천**: 병합 (Internal의 원칙/한계 이해를 기반으로, External의 실전 규약을 설계 가이드로 배치)

---

### [A-2] HTTP 메서드 범위

**상충 유형**: 불일치

| | Internal | External |
|---|---------|----------|
| 출처 | Go_Deeper/Wiki/REST&SOAP [REST] | Microsoft API Design [MS], IETF Draft [RFC] |
| 주장 | "사용할 수 있는 메서드가 4개뿐이다" (GET, POST, PUT, DELETE) | 멱등성 테이블에서 7개 메서드 나열: GET, HEAD, OPTIONS, PUT, DELETE, POST, PATCH. PATCH를 PUT과 구분하여 부분 수정 용도로 명시 |

**분석**: Internal은 REST의 한계를 설명하면서 주요 4개만 언급했지만, External은 HEAD, OPTIONS, PATCH를 포함하여 7개를 다룬다. 특히 PATCH(부분 수정)와 PUT(전체 교체)의 구분은 실전에서 중요한데, Internal에서는 이 구분이 없다.

**추천**: External 채택 (PATCH vs PUT 구분은 API 설계에서 핵심적. Internal의 4개 메서드 서술을 확장해야 함)

---

## B. Overlaps (중복)

### [B-1] HTTP 상태 코드

| 항목 | Internal | External |
|------|---------|----------|
| 범위 | 1xx~5xx 전체 분류, 주요 코드(200/201/202/204, 400/401/403/404, 500/503), 리다이렉션(301/302/304), PRG 패턴 | 429 Too Many Requests (Rate Limiting), RFC 9457 에러 응답 형식 (403 예시) |
| 일관성 | 일관됨 |
| 상세도 | Internal이 훨씬 상세 (체계적 분류). External은 특정 코드만 깊이 다룸 |

**추천**: 병합 유지 -- Internal의 체계적 상태 코드 분류를 기반으로, External의 429/RFC 9457 상세 내용으로 보충

### [B-2] 인증 vs 인가 구분

| 항목 | Internal | External |
|------|---------|----------|
| 범위 | 독립 섹션(섹션 6)에서 인증/인가를 비교 테이블로 정리. 401/403 매핑, "401 네이밍이 아쉬움" 지적 | 섹션 1.3에서 HTTP 메서드-리소스 매트릭스 내 간접 언급만 |
| 일관성 | 일관됨 (External이 인증/인가를 거의 다루지 않음) |

**추천**: Internal 채택 -- 인증/인가 구분은 API 설계의 핵심 개념이며, Internal의 정리가 명확함

### [B-3] 콘텐츠 협상과 헤더

| 항목 | Internal | External |
|------|---------|----------|
| 범위 | 표현 헤더(Content-Type/Encoding/Language/Length), 콘텐츠 협상(Accept 계열), Quality Values, 캐시 헤더(Cache-Control/ETag), 인증 헤더, 쿠키 헤더 | Rate Limit 헤더(X-RateLimit-*), Retry-After, HAL Content-Type(application/hal+json), Problem Details Content-Type(application/problem+json) |
| 일관성 | 일관됨 (다른 헤더를 다룸) |

**추천**: 병합 유지 -- Internal은 HTTP 기본 헤더, External은 API 전용 헤더. 양쪽 모두 필요

### [B-4] REST 자원 기반 설계

| 항목 | Internal | External |
|------|---------|----------|
| 범위 | "모든 자원은 고유한 ID(URI)", "URI로 자원 식별" -- 원칙 수준 | 명사 사용, 복수 명사, 계층적 하위 리소스, 케밥 케이스, 후행 슬래시 금지, DB 구조 비반영 -- 구체적 규칙 |
| 일관성 | 완전히 일관됨 (같은 원칙의 추상 vs 구체) |

**추천**: 병합 (Internal의 원칙 -> External의 구체적 규칙 순서로 배치)

---

## C. Decisions Needed (사용자 결정 필요)

### [C-1] GraphQL/gRPC 포함 여부

Internal은 REST vs SOAP 비교만 다루고, External은 REST 전용이다. 현대 API 생태계에서 GraphQL(BFF 패턴), gRPC(마이크로서비스 간 통신)는 주요 대안이다.

**결정 필요**:
1. 스킬 범위를 REST 전용으로 할 것인가, GraphQL/gRPC도 포함할 것인가?
2. 포함한다면 각 프로토콜별 독립 섹션으로 할 것인가, REST와의 비교 테이블 수준으로 할 것인가?

---

### [C-2] HATEOAS 커버리지 깊이

External 섹션 7에서 HATEOAS를 다루며, HAL 형식 예시와 함께 "업계 현실: 대부분 Level 2에서 멈춤"이라는 실용적 관점을 제시한다. 그러나 HAL, JSON:API, Siren, JSON-LD 등 형식 표준이 난립하는 상황이다.

**결정 필요**:
3. HATEOAS를 "알아야 하지만 대부분 안 쓴다" 수준으로 짧게 다룰 것인가 (실용주의)?
4. HAL 형식을 표준 예시로 채택할 것인가, JSON:API 등 다른 형식도 비교할 것인가?

---

### [C-3] OpenAPI 명세 상세도

Internal 섹션 5에서 OpenAPI의 용도와 스웨거와의 관계를 개념 수준으로 다룬다. 그러나 실제 OpenAPI YAML/JSON 작성법, 스키마 정의, 코드 생성 등 실전 내용이 없다.

**결정 필요**:
5. OpenAPI를 "개념 소개" 수준으로 유지할 것인가, YAML 작성 예시와 도구 활용까지 다룰 것인가?
6. OpenAPI 상세 가이드를 별도 스킬(tool-openapi 등)로 분리할 것인가?

---

### [C-4] WebSocket/SSE (실시간 API) 포함 여부

양쪽 모두 요청-응답(request-response) 패턴만 다룬다. 실시간 통신(WebSocket, Server-Sent Events, Long Polling)은 현대 API 설계에서 빈번한 주제다.

**결정 필요**:
7. 실시간 API 패턴을 architecture-api에 포함할 것인가?
8. 포함한다면 개념/선택 기준 수준인가, 구현 패턴까지인가?

---

### [C-5] architecture-api와 implementation-django(DRF)의 경계

External의 내용 중 일부는 구현에 가깝다: Rate Limiting 알고리즘(Fixed Window, Token Bucket 등), Idempotency-Key 서버 구현, RFC 9457 에러 응답 구현 등. 이들은 DRF(Django REST Framework) 구현과 직접 겹칠 수 있다.

**결정 필요**:
9. architecture-api에는 "무엇을 왜" (원칙, 패턴, 선택 기준)만 두고, "어떻게" (DRF serializer, throttling 설정 등)는 implementation-django로 이동할 것인가?
10. Rate Limiting 알고리즘 상세(Token Bucket 등)는 아키텍처 지식인가, 구현 지식인가?

---

### [C-6] API Gateway 패턴 포함 여부

양쪽 모두 API Gateway를 다루지 않는다. API Gateway는 인증, Rate Limiting, 라우팅, 로드 밸런싱 등을 중앙 집중화하는 아키텍처 패턴으로, External에서 다룬 Rate Limiting, 인증 등과 밀접하다.

**결정 필요**:
11. API Gateway 패턴(Kong, AWS API Gateway, Nginx 등)을 architecture-api에 포함할 것인가?
12. 포함한다면 아키텍처 패턴 수준인가, 특정 도구 설정까지인가?

---

### [C-7] SOAP 상세도

Internal에서 REST vs SOAP 비교 테이블을 제시하지만, SOAP 자체를 깊게 다루지는 않는다. SOAP은 레거시 시스템 통합에서 여전히 만날 수 있다.

**결정 필요**:
13. SOAP을 REST와의 비교 테이블 수준으로 유지할 것인가, 제거할 것인가?

---

## D. Gaps (양쪽 모두에서 누락된 주제)

### [D-1] API 보안 패턴

Internal이 인증/인가 개념과 401/403을 다루지만, 구체적 보안 메커니즘이 없다. OAuth 2.0 플로우, JWT 구조와 검증, API Key 관리, CORS 정책, CSRF 방어 등은 API 설계의 핵심 주제다. Internal에 OAuth 출처 표시가 있으나 실제 내용은 인증/인가 구분에 그친다.

### [D-2] API 설계 프로세스 (Design-First vs Code-First)

API를 먼저 명세로 설계하고 구현하는 Design-First 접근과, 코드를 먼저 작성하고 명세를 자동 생성하는 Code-First 접근의 비교가 없다. Internal이 OpenAPI 용도를 언급하지만 설계 프로세스 자체는 다루지 않는다.

### [D-3] API 응답 포맷 표준화

성공 응답의 공통 구조(envelope 패턴, 메타데이터 포함 방식)가 없다. External의 RFC 9457은 에러 응답만 다룬다. 성공 응답의 일관된 포맷(`{data, meta, links}` 등)은 API 사용성에 큰 영향을 미친다.

### [D-4] Bulk/Batch 연산 패턴

대량 생성/수정/삭제 API 설계 패턴이 없다. 단건 CRUD만 다루고 있다. 실전에서는 `POST /orders/batch`, 부분 성공 처리(207 Multi-Status), 비동기 배치 처리(202 Accepted + polling) 등이 빈번하다.

### [D-5] API 문서화 전략

Internal이 OpenAPI의 존재를 언급하지만, API 문서화 전략(자동 생성 vs 수동 작성, 예시 응답 포함, 변경 이력 관리, Developer Portal 구성)을 체계적으로 다루지 않는다.

### [D-6] 캐싱 전략 (API 계층)

Internal이 HTTP 캐시 헤더(Cache-Control, ETag)를 다루지만, API 계층의 캐싱 전략(CDN 캐싱, 서버 사이드 캐싱, 캐시 무효화 전략, 조건부 요청 패턴)이 없다. 헤더 지식과 전략 수준 가이드 사이에 간극이 있다.

### [D-7] 하위 호환성과 Deprecation 정책

External이 버전 관리 전략을 다루지만, 기존 API의 하위 호환 유지 규칙(필드 추가는 OK, 필드 제거는 breaking change 등)과 Deprecation 프로세스(Sunset 헤더, 마이그레이션 기간 등)가 없다.

### [D-8] API 테스트 전략

Contract Testing(Pact), Integration Testing, Consumer-Driven Contract 등 API 테스트 패턴이 양쪽 모두 누락. API 설계와 테스트 가능성(testability)의 관계도 다루지 않는다.

---

## 요약

### Conflicts

| 번호 | 주제 | 상충 유형 | 추천 |
|------|------|-----------|------|
| A-1 | REST 정의의 깊이 | 관점 불일치 | 병합 |
| A-2 | HTTP 메서드 범위 | 불일치 | External |

**총 2건** (직접 모순 0건, 불일치 2건) -- 심각한 충돌은 없으며 추상 수준과 범위의 차이

### Overlaps

| 번호 | 주제 | 일관성 | 추천 |
|------|------|--------|------|
| B-1 | HTTP 상태 코드 | 일관 | 병합 |
| B-2 | 인증 vs 인가 | 일관 | Internal |
| B-3 | 헤더 | 일관 | 병합 |
| B-4 | REST 자원 설계 | 일관 | 병합 |

**총 4건** -- 모든 중복이 일관적이며, Internal(원칙)과 External(실전)의 보완 구조

### Decisions

| 번호 | 결정 사항 | 영향 범위 |
|------|----------|----------|
| 1-2 | GraphQL/gRPC 포함 여부 | 스킬 범위 |
| 3-4 | HATEOAS 커버리지 깊이 | 스킬 상세도 |
| 5-6 | OpenAPI 명세 상세도 | 타 스킬과 경계 |
| 7-8 | WebSocket/SSE 포함 여부 | 스킬 범위 |
| 9-10 | architecture-api vs implementation-django 경계 | 타 스킬과 경계 |
| 11-12 | API Gateway 패턴 포함 여부 | 스킬 범위 |
| 13 | SOAP 상세도 | 스킬 상세도 |

**총 13건의 결정 필요**

### Gaps

| 번호 | 누락 주제 | 중요도 |
|------|----------|--------|
| D-1 | API 보안 패턴 (OAuth, JWT, CORS) | 높음 |
| D-2 | API 설계 프로세스 (Design-First vs Code-First) | 중간 |
| D-3 | API 응답 포맷 표준화 | 중간 |
| D-4 | Bulk/Batch 연산 패턴 | 중간 |
| D-5 | API 문서화 전략 | 중간 |
| D-6 | 캐싱 전략 (API 계층) | 높음 |
| D-7 | 하위 호환성과 Deprecation 정책 | 높음 |
| D-8 | API 테스트 전략 | 중간 |

**총 8건의 Gap** (높음 3건, 중간 5건)
