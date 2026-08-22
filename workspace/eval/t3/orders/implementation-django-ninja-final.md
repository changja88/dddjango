# T3 발주 — implementation-django-ninja-final

- 원문: `dddjango/skills/implementation-django-ninja/references/final.md` (현재 1021행 — **센서스 1019행에서 드리프트: 아래 행 번호는 참고값, spec은 반드시 현재 파일에서 재확정**)
- 스코프: REF 21절 · 규범 182문장 (파일럿 기이관 절 제외됨)
- 산출: `workspace/eval/t3/specs/implementation-django-ninja-final.spec.json` + `workspace/eval/t3/worksheets/implementation-django-ninja-final.md`

| section_key | 헤딩 | 센서스 행 | 규범 수 | 운반체 | 재진술 | 비고 |
|---|---|---|---|---|---|---|
| s001 | Django Ninja API 구현 종합 가이드 | 1–15 | 3 | none | Y:implementation-django-ninja-skill/s003 | 서두 blockquote 위임+greenfield 기본 목표 — P0 «서두» 규범 3이 전부 이 절에 귀속 |
| s004-1.1 | 1.1 Django Ninja skill의 역할 | 35–48 | 1 | none | N | «다룬다» 1문장만 보수적 포함, 책임 bullet 8항은 명사구(P0 승계) |
| s005-1.2 | 1.2 다른 source reference로 위임할 책임 | 49–60 | 4 | none | Y:implementation-django-ninja-skill/s003 | 순수 소유 배정 절 — 3중 라우팅 표면의 본문측 |
| s006-1.3 | 1.3 Router thinness 원칙 | 61–80 | 3 | none | N | 허용 5·금지 5 목록은 명사구, 지배 문장 계수 |
| s008-2.1 | 2.1 Router 등록 | 83–99 | 11 | none | N | 버전 핀 규율 밀도 높음, 확인 5항 명사구 |
| s009-2.2 | 2.2 Operation 선언 | 100–191 | 25 | code | Y:implementation-django-ninja-final/s023-6.2 | 2-path(예외/Result) 규칙이 §6.2와 거의 동일 반복(P0 발견 5) |
| s010-2.3 | 2.3 클래스 컨트롤러 (ninja-extra) — 신규 표준 | 192–305 | 38 | code | Y:implementation-django-ninja-final/s024-6.3 | «오류/415 이유 강등 금지» 문장 §6.3과 중복. 핀 규율은 §2.1 참조라 사본 아님 |
| s012-3.1 | 3.1 Request/response schema 분리 | 308–341 | 17 | none | N | birth-enum·discriminator. 외부 이슈 앵커 vitalik/django-ninja#1308 인용 |
| s013-3.2 | 3.2 ModelSchema 사용 기준 | 342–364 | 1 | code | N | 확인 4항은 의문형 목록(체크박스 아님), 예제 주석 속 규칙 제외 |
| s014-3.3 | 3.3 Resolver와 computed field | 365–372 | 2 | none | N | - |
| s016-4.1 | 4.1 Authentication | 375–391 | 9 | none | Y:implementation-django-ninja-final/s023-6.2 | auth 실패 규칙(None/AuthenticationError·request.auth ErrorSchema 금지) §6.2 framework 오류 경계와 반복(P0 발견 5) |
| s017-4.2 | 4.2 Authorization | 392–406 | 5 | none | N | - |
| s019-5.1 | 5.1 Filtering과 sorting | 409–440 | 7 | code | N | 예시 코드 앞 괄호 문장(«신규 표면은 §2.3 형태») 포함 |
| s020-5.2 | 5.2 Pagination | 441–468 | 7 | code | N | «offset이 단순» 권고 산문 제외(P0 승계) |
| s024-6.3 | 6.3 콘텐츠 협상 실패 (406/415) | 827–853 | 15 | none | Y:implementation-django-ninja-final/s010-2.3 | 강등 금지 문장만 §2.3과 중복, 나머지 고유 |
| s025-7 | 7. Idempotency-Key | 854–872 | 8 | none | N | - |
| s026-8 | 8. OpenAPI | 873–900 | 5 | none | N | candidate 10항 명사구 |
| s028-9.1 | 9.1 공개 HTTP 검증 범위 | 903–943 | 8 | code | N | candidate 8항 명사구, TestClient(router) 증거 부정 규칙 |
| s029-9.2 | 9.2 검증 보고 기준 | 944–959 | 3 | none | N | Not run 보고 정직성 규칙 |
| s030-10 | 10. DRF-to-Ninja migration | 960–984 | 4 | none | N | Migration checklist 10항은 명사구 불릿(체크박스 아님) |
| s031-11 | 11. 라우팅 기준 | 985–1000 | 6 | none | Y:implementation-django-ninja-skill/s003 | 3중 라우팅 표면(frontmatter·«언제 쓰나»·§1.2) |
