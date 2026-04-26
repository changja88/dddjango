# Rate Limiting과 멱등성 키 레퍼런스

Rate Limit 헤더와 429 응답, 알고리즘 선택 기준, Idempotency-Key 패턴과 동작 방식.

---

## Rate Limit 헤더

```
HTTP/2 200 OK
X-RateLimit-Limit: 60          # 윈도우 내 최대 요청 수
X-RateLimit-Remaining: 56      # 남은 요청 수
X-RateLimit-Reset: 1372700873  # 리셋 시각 (UTC epoch)
```

---

## 429 Too Many Requests

```
HTTP/2 429 Too Many Requests
Retry-After: 30
X-RateLimit-Remaining: 0
```

---

## 알고리즘 선택 기준

| 알고리즘 | 특징 | 적합 |
|---------|------|------|
| **Token Bucket** | 제어된 버스트 허용 | 퍼블릭 API 기본 |
| **Sliding Window** | 부드러움, 경계 문제 없음 | 정확한 제어 필요 |
| **Fixed Window** | 단순, 저오버헤드 | 간단한 내부 API |
| **Leaky Bucket** | 일정 출력, 버스트 없음 | 트래픽 셰이핑 |

---

## Rate Limiting 실전 원칙

- 비용 큰 작업(인증, DB) **전에** rate limit 검사
- 429 응답에 항상 `Retry-After` 헤더 포함
- Rate limit 정책을 API 문서에 명확히 기재

---

## Idempotency-Key 문제

POST는 멱등하지 않다. 네트워크 장애로 서버는 처리했지만 클라이언트가 응답을 못 받으면, 재시도 시 중복 생성 위험.

---

## Idempotency-Key 패턴

```
POST /v1/charges
Idempotency-Key: KG5LxSFa3M4fcVng
Content-Type: application/json

{"amount": 2000, "currency": "usd"}
```

---

## 동작 방식

1. 클라이언트가 고유 키 생성 (V4 UUID 권장)
2. 서버가 첫 요청의 상태 코드 + 응답 본문을 저장
3. 동일 키의 후속 요청은 저장된 결과를 반환
4. 키는 24시간 후 만료 (일반적 정책)
5. POST에만 적용 -- GET, PUT, DELETE는 이미 멱등

---

## Idempotency-Key 실전 원칙

- 결제, 주문 생성 등 **중복이 치명적인 POST**에 필수
- 멱등성 키를 내구성 있는 저장소(DB, Redis)에 보관
- 동일 키의 동시 요청에 대한 레이스 컨디션 처리 필요
