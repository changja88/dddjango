# P1a·P1b·P2·P3 라이브 재테스트 — 실행 핸드오프 (2026-05-30)

> 너가 `/dddjango`를 직접 돌리고, 끝나면 내가 산출물을 13축으로 채점한다.
> 방식 정본: `FINAL-SMOKE-PLAN.md`(rev3). 정직 경계: **N=1 sanity** — "수정한 표준이 라이브 런에서 작동하나"까지. 우열·결정성 결론 아님.

## 0. 준비 상태 (내가 완료)
- ✅ **캐시 신선화**: Claude·Codex 캐시 둘 다 레포 HEAD(`246ccfc`)와 byte-identical(P2 백스톱 스크립트 포함). 직전 14커밋 stale였음.
- ✅ **fixture 2개**: Django 5.2.14 · Python 3.12 · ninja 미설치 · PROMPT.md 제거 · baseline 커밋 · check/migrate/seed 통과.
  - `~/Desktop/dddjango-smoke2-claudeA` — 태스크 A / Claude
  - `~/Desktop/dddjango-smoke2-codexB` — 태스크 B / Codex
- ⚠️ **반드시 새 세션에서 시작** — 캐시를 방금 갱신해서, 지금 열려 있는 세션은 메모리에 구 에이전트 텍스트를 들고 있다. (기존 세션을 쓰려면 `/reload-plugins` 후.)

## 1. 고정 게이트 답 (양 런 공통 — 변수 제거)
| 게이트 | 답 | 이유 |
|---|---|---|
| G0 BC 배치 | **미강제** — "표준 판정-소유 원칙대로 결정" | ③ 이주·⑥ 협력을 실제 테스트(강제하면 축 죽음) |
| G0 렌즈 | **ddd + db + api** | HTTP 계약(409) 있음 |
| G0 스코프 | **제안대로** | 확장 금지 |
| API 스택/프레임워크 | **"표준 기본대로"** — ⚠️ plain 강제 **금지** | ④/P1a의 본질 = 표준이 스스로 Ninja로 수렴하는지 |
| 테스트 러너 | **제안대로** | — |
| G1 설계 / G2 구현 | **명백한 결함 없으면 무수정 승인** | 게이트 발화 자체가 관찰 대상 |
| thinking | **OFF** (coder) | 비용 레버, 품질 무손실(DR-08) |

> 인터랙티브(Codex)에서 "venv 패키지 확인하라" 같은 힌트 **주지 말 것** — 표준이 스스로 Ninja+핀으로 가는지가 진짜 테스트.

## 2. 태스크 A — 재고예약 (Claude, fixture `dddjango-smoke2-claudeA`)
```
재고를 예약(reserve)하는 API. 재고가 부족하면 409, 충분하면 그만큼 차감(예약)한다. 대상은 기존 catalog의 Product.
```
실행:
```bash
cd ~/Desktop/dddjango-smoke2-claudeA
claude                       # 새 세션
# 세션 안에서:  /dddjango  → 위 프롬프트 붙여넣기 → §1 게이트 답
# 끝나면 테스트:
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations && .venv/bin/python manage.py migrate
.venv/bin/python manage.py test
```

## 3. 태스크 B — 주문생성 (Codex 인터랙티브, fixture `dddjango-smoke2-codexB`)
```
주문 생성 API. 별도 주문(order) 개념으로, 요청 상품·수량의 주문을 만든다. 재고는 기존 catalog가 소유하며, 주문 생성 시 catalog의 재고를 차감한다(재고 부족 시 409).
```
실행:
```bash
cd ~/Desktop/dddjango-smoke2-codexB
codex                        # 새 세션 — dddjango 스킬(코디네이터)이 트리거되게 위 프롬프트
# 게이트는 §1 표대로. 끝나면 위와 동일한 manage.py check/migrate/test
```

## 4. 끝나면 나에게
- "A 끝났어" / "B 끝났어"만 알려주면, 내가 직접 fixture의 `.dddjango/<기능>/design-spec.md`·`application/`·테스트·`requirements.txt`를 읽어 채점한다(파일은 내가 읽으니 따로 붙여넣을 필요 없음).
- 런 중 막히거나 게이트가 헷갈리면 그대로 물어봐.

## 5. 내가 채점할 핵심 (P→축)
| P | 축 | PASS 신호 (유기적 준수) |
|---|---|---|
| **P1a** | 축4 | operation은 `raise`만, problem+json 변환은 **중앙 `@api.exception_handler`/헬퍼 한 곳**. operation 본문에 수제 `JsonResponse`/튜플 반환 = 0. openapi.json에 404·409 노출. RFC 9457 본문. |
| **P1b** | 축3 | `requirements.txt`에 `django-ninja==<설치된 최신>` 핀(stale 옛 버전 ✗). **grep만으로 판정**(test-green 금지). |
| **P2** | 축5 | 커스텀 `BEGIN IMMEDIATE`/자작 DB 백엔드 = 0. 연결 튜닝은 stock `OPTIONS`(`transaction_mode` 등)만. version CAS + `stock>=0` CHECK 백스톱. |
| **P3** | 축13 | design-spec에 §9.6 8행 블록(번호 인용만 ✗). 동시성 기준이 **실제 테스트로 실현**(CAS-충돌 스파이/동시요청/동등 결정적 테스트). 가드만·oversell 테스트 0 = MISS. |
| 그 외 | 1·2·6·7·8·10·11·12 | 구조·명명·동작 회귀 확인 (FINAL-SMOKE-PLAN §4). |

> **유기적 한계(정직)**: catch 층(리뷰어 blocker·백스톱)은 위반이 없으면 발화 안 한다. 런타임이 준수하면 "미발화 = 정상". catch의 실효는 이미 저장 산출물 동적검증으로 확인(codexB recall 3/3). 이 런은 **준수(생산자) 측면** 확인이다.
