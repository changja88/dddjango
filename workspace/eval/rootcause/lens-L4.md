# Lens L4 — 부분 미완 (처방 스코프를 너무 좁게 앵커→형제 변종 누수)

> 정의: 처방이 맞지만 스코프를 너무 좁게 앵커해 같은 부류의 다른 변종이 누수. L3와 구별: L4는 *처방 설계 스코프*가 좁음, L3는 *탐지 메커니즘*이 못 봄(겹치면 둘 다·note에 구별).

| episode_id | mode | evidence_anchor | severity | is_open | note |
|---|---|---|---|---|---|
| ACL-EX | L4 | DEVLOG:404 DNR-14 "포트 도메인 예외에만 앵커→raw 인프라 예외 통과→500"; :376 DR-45 #1 "형제 예외 패밀리로 재현"; aclex-claude:8/21; DEVLOG:366 DR-44 보류근거 | critical | yes | DR-44가 포트 도메인-예외 패밀리에만 앵커→인프라 transient 형제(OperationalError/IntegrityError) 같은 500 잔존. 표준 빈틈 #1·sequential이라 영구 green |
| 깨진JSON | L4 | DEVLOG:377 DR-45 #2 "DR-35 변종(415 데코는 CT만)"; aclex-claude:13 "§2.5.3/§6.9 위반"; DEVLOG:271 | major | yes | DR-35 view 데코레이터가 content-type(415)만 가드→깨진 본문 ninja 400이 problem+json 중앙화 밖 누수(DR-35 형제) |
| P1a | L4 | DEVLOG:164 DR-23 "스크립트는 application_layer HTTP 누수만 고정밀…operation 수제·변수우회 비대상"; :169 DR-24; c4live-claude:112 | major | no | check-error-centralization을 application_layer로 좁게 앵커→presentation operation 수제·status snapshot 변종(C2) 비대상. **L3와 겹침**이나 뿌리는 처방 스코프=L4 |
| C4 | L4 | DEVLOG:246 DR-32 "저-recall…B형 보류"; :242 "domain_layer 유무로 C형/B형"; REMAINING:106 | major | no | C형(domain_layer 0개)에만 앵커→B형(메서드 존재+복제)·domain_layer 밖 형제 면제·미커버(의도적 보류지만 사촌 변종 누수=L4) |
| BC-FK | L4 | DEVLOG:286 DR-37 "규칙3이 도메인 객체 레벨로만→영속성/ORM 미확장…정반대 해석" | major | no | 규칙3이 도메인-참조 레벨에만 앵커→영속성/ORM(FK) 형제 미규정. DR-37이 규칙3을 영속성까지 확장해 *닫은* 사후 사례 |
| P4③ | L4 | DEVLOG:91·397 DNR-7 "이 규칙은 무관 앱에만…touched 데이터소스는 위치 이주"; :194 DR-26 | major | no(⚪) | catalog 이주 규칙이 처음 너무 넓게/모호하게 앵커→touched 데이터소스 형제 위치 회귀. DNR-7·DR-26이 스코프 좁혀 정정. 반복 비결정이라 ⚪ |
| NJ-4 | L4 | REMAINING:69 "openapi_extra-only(response= 누락)"; :16 백스톱 exit2; DEVLOG:221 | minor | yes | 오류 status 선언 백스톱이 openapi_extra-only 형태만·다른 선언 누락 변종 커버 불확정(약한 L4·라이브 발화 미검증) |

NEW (L4 아님): 위장-constraint=NEW:test-misattribution(처방 스코프 아닌 테스트 오귀속) · 위장-oversell=NEW:vacuous-concurrency-test(sequential vacuous green·ACL-EX 영구green 공범) · pytest-MISS=NEW:backstop-silent-on-absence(L3 인접·무설정 침묵).

핵심: L4는 "처방이 결함 공간보다 좁은 부분집합만 덮음". 가장 열린 L4 = ACL-EX(critical·표준 빈틈 #1)·깨진JSON(major·DR-35 형제). DR-37(BC-FK)·DR-32(C4)는 같은 P4③ 클래스의 *해결/보류* 선례 — 처방 스코프를 도메인/C형으로 좁게 잡았던 게 원인.
