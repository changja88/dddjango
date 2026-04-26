# HTTP 헤더와 콘텐츠 협상 레퍼런스

표현 헤더, 콘텐츠 협상, 캐시 관련 헤더를 정리한다.

---

## 표현 관련 헤더

| 헤더 | 용도 | 예시 |
|------|------|------|
| Content-Type | 미디어 타입 + 인코딩 | `application/json` |
| Content-Encoding | 압축 방식 | `gzip` |
| Content-Language | 자연 언어 | `ko` |
| Content-Length | 바이트 단위 길이 | `1024` |

---

## 콘텐츠 협상 (Content Negotiation)

클라이언트가 선호하는 표현을 요청하는 방식.

| 요청 헤더 | 협상 대상 |
|----------|----------|
| Accept | 미디어 타입 |
| Accept-Language | 자연 언어 |
| Accept-Encoding | 압축 방식 |

**Quality Values (q값)**: 0~1 사이 값으로 우선순위 지정. 생략 시 1. 구체적인 것이 우선한다.

```
Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8
```

---

## 캐시 관련 헤더

| 헤더 | 용도 |
|------|------|
| Cache-Control | 캐시 정책 (max-age, no-cache, no-store, must-revalidate) |
| ETag / If-None-Match | 해시 기반 검증 (가장 정확) |
| Last-Modified / If-Modified-Since | 날짜 기반 검증 |

**304 Not Modified**: 리소스가 변경되지 않았으면 본문 없이 304 응답. 클라이언트는 로컬 캐시 사용.
