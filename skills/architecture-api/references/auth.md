# 인증과 인가 레퍼런스

인증(Authentication)과 인가(Authorization)의 차이, 인증 메커니즘 선택 기준, API 보안 원칙.

---

## 인증 vs 인가

| 구분 | 인증 (Authentication) | 인가 (Authorization) |
|------|---------------------|---------------------|
| 질문 | "너는 누구인가?" | "너는 이걸 할 수 있는가?" |
| 시점 | 인가보다 먼저 | 인증 후에 수행 |
| HTTP 코드 | 401 Unauthorized | 403 Forbidden |
| 실패 시 | WWW-Authenticate 헤더로 인증 방법 안내 | 권한 부족 메시지 |

- 인증이 있어야 인가가 있다
- 401은 이름이 Unauthorized지만 실제로는 **인증(Authentication)** 오류다

---

## 인증 메커니즘 선택 기준

| 방식 | 적합 | 특징 |
|------|------|------|
| **API Key** | 서버 간 통신, 내부 API | 단순, 사용자 식별 불가 |
| **OAuth 2.0** | 서드파티 접근 권한 위임 | 표준화, 복잡하지만 유연 |
| **JWT (Bearer Token)** | 무상태 인증, 마이크로서비스 | 자체 포함(self-contained), 만료 관리 필요 |

---

## 보안 원칙

- **비밀 정보를 쿼리 파라미터에 담지 않는다** -- URL은 서버/프록시 로그에 기록됨
- 인증 정보는 `Authorization` 헤더에 전달
- 모든 API 통신에 HTTPS 사용
