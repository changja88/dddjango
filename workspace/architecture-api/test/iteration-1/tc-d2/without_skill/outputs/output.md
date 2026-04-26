# API 버전 전략 설계

## 1. 버전 관리 전략

### 1.1 버전 식별 방식: URI Path Versioning

```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

**선택 근거:**
- 외부 파트너 50개사가 연동 중이므로, 가장 직관적이고 명시적인 방식이 필요하다.
- Header 기반(`Accept: application/vnd.example.v2+json`)이나 Query Parameter 방식(`?version=2`)은 파트너 개발자가 놓치기 쉽다.
- URI Path 방식은 문서화, 디버깅, 로그 분석 시 버전이 즉시 식별된다.

### 1.2 버전 범위 정책

| 구분 | 정책 |
|------|------|
| Major 버전 (v1, v2) | URI Path에 반영. Breaking Change가 있을 때만 올린다. |
| Minor 변경 | 동일 버전 내에서 하위 호환성을 유지하며 필드 추가, 선택적 파라미터 추가 등을 수행한다. |
| Patch/Fix | 동일 버전 내에서 버그 수정. 별도 버전 표기 없음. |

### 1.3 버전별 독립 라우팅 구조

```
/api/
  v1/
    routes/
      users.py
      payments.py
    schemas/
      user_schema.py
      payment_schema.py
  v2/
    routes/
      users.py
      payments.py
    schemas/
      user_schema.py
      payment_schema.py
  shared/
    services/        # 버전 간 공유 비즈니스 로직
    repositories/    # 데이터 접근 계층
    middleware/      # 인증, 로깅 등 공통 미들웨어
```

**핵심 원칙:**
- Route와 Schema는 버전별로 분리한다.
- 비즈니스 로직(Service Layer)은 가능한 한 공유하되, 버전별 차이는 어댑터 패턴으로 처리한다.
- 데이터 접근 계층은 공유한다.

### 1.4 동시 운영 가능 버전 수 제한

**최대 2개 Major 버전을 동시에 운영한다.**

- v2 출시 시점에 v1은 Deprecated 상태로 전환한다.
- v3가 필요해지면, v1은 반드시 종료된 상태여야 한다.
- 3개 이상의 버전을 동시에 운영하지 않는다.

---

## 2. v1 -> v2 마이그레이션 계획

### 2.1 마이그레이션 타임라인

```
[M0]          [M1]          [M3]          [M6]          [M9]          [M12]
 |             |             |             |             |             |
 v2 설계완료    v2 Beta       v2 GA         v1 일부       v1 전체       v1 종료
 변경사항 공지   파트너 테스트   v2 정식 출시   엔드포인트     Sunset        서비스 중단
               환경 제공                    Sunset        Header 적용
```

| 시점 | 이벤트 | 상세 |
|------|--------|------|
| M0 (현재) | 설계 완료 및 사전 공지 | 변경사항 문서 배포, 파트너 전체 공지 |
| M1 | v2 Beta 출시 | Sandbox 환경에서 파트너 테스트 가능. 피드백 수집. |
| M3 | v2 GA (정식 출시) | v2 프로덕션 사용 가능. v1과 v2 병행 운영 시작. |
| M6 | v1 레거시 엔드포인트 Sunset | 제거 예정이었던 레거시 엔드포인트 먼저 종료. |
| M9 | v1 전체 Sunset Header 적용 | v1 전체 응답에 `Sunset` 헤더 포함. |
| M12 | v1 서비스 종료 | v1 엔드포인트 404 반환. |

### 2.2 파트너별 마이그레이션 지원

**파트너 등급 분류:**

| 등급 | 기준 | 지원 수준 |
|------|------|-----------|
| Tier 1 (상위 10개사) | 월 API 호출량 상위 20%, 또는 매출 기여도 상위 | 전담 엔지니어 배정, 1:1 마이그레이션 지원, 별도 일정 협의 가능 |
| Tier 2 (중간 25개사) | 일반적인 사용량 | 마이그레이션 가이드 제공, 그룹 Q&A 세션, 이메일 지원 |
| Tier 3 (하위 15개사) | 소량 사용 또는 비활성 | 마이그레이션 가이드 제공, 셀프 서비스 지원 |

### 2.3 변경 사항 매핑 문서

모든 Breaking Change에 대해 아래 형식의 매핑 문서를 제공한다.

```
## 사용자 모델 구조 변경

### v1 (기존)
GET /v1/users/{id}
Response:
{
  "id": 123,
  "name": "홍길동",
  "email": "hong@example.com",
  "address": "서울시 강남구"
}

### v2 (변경)
GET /v2/users/{id}
Response:
{
  "id": "usr_abc123",
  "profile": {
    "display_name": "홍길동",
    "email": "hong@example.com"
  },
  "addresses": [
    {
      "type": "primary",
      "line1": "서울시 강남구",
      "country": "KR"
    }
  ]
}

### 마이그레이션 가이드
- id: 정수 -> 문자열(접두사 포함)로 변경. 기존 정수 ID는 `usr_{id}` 형식으로 매핑됨.
- name -> profile.display_name 으로 이동.
- address: 단일 문자열 -> 구조화된 배열로 변경.
```

### 2.4 마이그레이션 보조 도구

| 도구 | 설명 |
|------|------|
| Compatibility Proxy | v1 요청을 v2로 변환하는 프록시 계층. 긴급 상황에서 파트너가 코드 변경 없이 v2 백엔드를 사용할 수 있도록 임시 지원. |
| Migration Checker API | `GET /v1/migration/status` - 해당 파트너의 v1 사용 현황과 마이그레이션 진행률을 반환. |
| Dual-Write 기간 | 데이터 모델 변경 시 v1/v2 양쪽에 데이터를 동시 기록하여 전환 중 데이터 불일치를 방지. |

---

## 3. v1 Deprecation 일정과 프로세스

### 3.1 Deprecation 단계

```
Stage 1: ANNOUNCED (M0 ~ M3)
  - 공지 발송, 문서 업데이트
  - v1 API 정상 동작
  - 응답 헤더: Deprecation: true

Stage 2: DEPRECATED (M3 ~ M9)
  - v2 GA 출시 이후
  - v1 API 정상 동작하지만, 신규 기능 추가 없음
  - 응답 헤더: Deprecation: true, Sunset: <날짜>
  - 보안 패치만 적용

Stage 3: SUNSET (M9 ~ M12)
  - v1 응답에 경고 본문 포함
  - Rate Limit 단계적 축소 (기존의 50% -> 25%)
  - 모니터링 강화: 아직 v1을 사용하는 파트너에게 주간 알림 발송

Stage 4: RETIRED (M12~)
  - v1 엔드포인트가 410 Gone 반환
  - 응답 본문에 v2 마이그레이션 가이드 링크 포함
```

### 3.2 Deprecation 응답 헤더 규격

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 01 Apr 2027 00:00:00 GMT
Link: <https://api.example.com/docs/migration/v1-to-v2>; rel="successor-version"
X-API-Warn: "This API version is deprecated. Please migrate to v2."
```

- `Deprecation` 헤더: RFC 8594 준수.
- `Sunset` 헤더: RFC 8594 준수. 서비스 종료 예정일을 명시.
- `Link` 헤더: 후속 버전 문서로의 링크를 제공.

### 3.3 레거시 엔드포인트 제거 프로세스

제거 예정인 레거시 엔드포인트는 별도의 빠른 일정을 따른다.

| 시점 | 조치 |
|------|------|
| 즉시 | 레거시 엔드포인트 목록 공지. 해당 엔드포인트 사용 파트너 개별 통지. |
| M1 | 레거시 엔드포인트 응답에 `Sunset` 헤더 추가. |
| M3 | Rate Limit를 현재의 50%로 축소. 대체 엔드포인트 안내 강화. |
| M6 | 레거시 엔드포인트 종료 (410 Gone). v1의 나머지 엔드포인트보다 6개월 먼저 종료. |

### 3.4 커뮤니케이션 채널

| 채널 | 용도 | 빈도 |
|------|------|------|
| 이메일 (파트너 기술 담당자) | 공식 공지, 일정 변경, 긴급 알림 | 주요 마일스톤마다 |
| Developer Portal 공지사항 | 상세 마이그레이션 가이드, FAQ | 상시 업데이트 |
| API 응답 헤더 | Deprecation/Sunset 알림 | 매 요청마다 |
| Changelog (RSS/Webhook) | 변경 이력 자동 알림 | 변경 발생 시 |
| 분기별 파트너 웨비나 | Q&A, 마이그레이션 진행 공유 | 분기 1회 |

---

## 4. 하위 호환성 유지 규칙

### 4.1 동일 Major 버전 내에서 허용되는 변경 (Non-Breaking)

| 변경 유형 | 허용 여부 | 예시 |
|-----------|-----------|------|
| 응답 필드 추가 | 허용 | 새로운 선택적 필드 추가 |
| 선택적 요청 파라미터 추가 | 허용 | 기본값이 있는 새 쿼리 파라미터 |
| 새 엔드포인트 추가 | 허용 | `GET /v1/users/{id}/preferences` |
| 새 enum 값 추가 (응답) | 허용 | status에 새 값 추가 |
| 에러 메시지 문구 변경 | 허용 | 에러 코드는 유지, 메시지만 변경 |
| 성능 개선 | 허용 | 응답 시간 단축 |

### 4.2 동일 Major 버전 내에서 금지되는 변경 (Breaking)

| 변경 유형 | 금지 | 예시 |
|-----------|------|------|
| 기존 필드 제거 또는 이름 변경 | 금지 | `name` -> `display_name` |
| 기존 필드 타입 변경 | 금지 | `id: int` -> `id: string` |
| 필수 파라미터 추가 | 금지 | 기존 요청에 새 필수 필드 추가 |
| URL 경로 변경 | 금지 | `/users` -> `/members` |
| HTTP 메서드 변경 | 금지 | `PUT` -> `PATCH` |
| 인증 방식 변경 | 금지 | API Key -> OAuth |
| 에러 코드 체계 변경 | 금지 | 에러 코드 번호 재배치 |
| 기존 enum 값 제거 | 금지 | status에서 기존 값 삭제 |
| 페이지네이션 방식 변경 | 금지 | offset -> cursor 전환 |
| 기본 정렬 순서 변경 | 금지 | 리스트 API의 기본 정렬 변경 |

### 4.3 호환성 검증 자동화

```yaml
# CI/CD 파이프라인에 통합
api-compatibility-check:
  steps:
    - name: OpenAPI Spec Diff
      description: |
        이전 배포 버전의 OpenAPI 스펙과 현재 스펙을 비교하여
        Breaking Change를 자동 탐지한다.
      tool: oasdiff 또는 openapi-diff
      fail_on: breaking-change

    - name: Contract Test
      description: |
        파트너가 실제 사용하는 요청/응답 패턴을 기반으로
        계약 테스트를 수행한다.
      tool: Pact 또는 Dredd

    - name: Shadow Traffic Test
      description: |
        프로덕션 트래픽의 복사본을 새 버전에 보내
        응답 차이를 검출한다.
      condition: Major 버전 출시 전
```

### 4.4 버전 간 호환성 보장 체크리스트

새로운 배포 전에 반드시 확인해야 할 항목:

```
[ ] OpenAPI Spec Diff에서 Breaking Change가 없는가?
[ ] 기존 통합 테스트가 모두 통과하는가?
[ ] 새로 추가된 필드에 기본값이 설정되어 있는가?
[ ] 새로 추가된 파라미터가 선택적(optional)인가?
[ ] 응답 필드의 타입이 변경되지 않았는가?
[ ] Deprecation 예정 필드에 경고가 문서화되어 있는가?
[ ] 파트너 SDK(제공하는 경우)가 업데이트되었는가?
```

### 4.5 Versioning Governance

| 역할 | 책임 |
|------|------|
| API Review Board | Breaking Change 여부 최종 판단, Major 버전 출시 승인 |
| API Product Owner | 버전 일정 관리, 파트너 커뮤니케이션 총괄 |
| API Platform Team | 버전 라우팅, 호환성 검증 인프라 운영 |
| Partner Engineering | 파트너별 마이그레이션 지원, 피드백 수집 |

---

## 요약

| 항목 | 결정 |
|------|------|
| 버전 식별 | URI Path (`/v1/`, `/v2/`) |
| 동시 운영 버전 | 최대 2개 |
| v2 Beta | M1 (1개월 후) |
| v2 GA | M3 (3개월 후) |
| v1 레거시 엔드포인트 종료 | M6 (6개월 후) |
| v1 전체 종료 | M12 (12개월 후) |
| Breaking Change 정책 | 동일 Major 버전 내 금지, Major 버전 변경 시에만 허용 |
| 호환성 검증 | OpenAPI Diff + Contract Test + Shadow Traffic |
| Deprecation 표준 | RFC 8594 (Deprecation, Sunset 헤더) |
