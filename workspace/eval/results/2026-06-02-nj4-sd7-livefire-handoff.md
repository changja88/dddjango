# NJ-4·SD-7 백스톱 라이브 검증 — 실행 핸드오프 (2026-06-02)

> 너가 `/dddjango`를 직접 돌리고(드라이브), 끝나면 내가 G2 백스톱 발화·생성 코드를 채점한다.
> **목적**: 신규 결정적 백스톱 2종(`check-openapi-error-declaration`·`check-context-isolation`)이 **라이브에서 작동**하는지 + 생산자 예방(표준 보강)이 준수를 유도하는지. **N=1 sanity** — 우열·결정성 결론 아님.
> 처방 정본: `workspace/design/2026-06-02-nj4-sd7-enforcement.md`.

## 0. 준비 상태
- ✅ 백스톱 2종 + 표준/배선/리뷰어/architect 보강 + 3미러 byte-identical 동기화 — 커밋 `bde2865`.
- ✅ 플러그인 버전 1.0.2 범프 — 커밋 `655079d`(캐시 갱신 트리거; marketplace는 git HEAD 기반).
- ✅ fixture 2개: baseline clean(Django 5.2.14·**py3.12**·ninja 미설치·PROMPT 제거·seed Widget10/Gadget3·check 통과).
  - `~/Desktop/dddjango-smoke6-claude` — Claude
  - `~/Desktop/dddjango-smoke6-codex` — Codex
- 🔲 **캐시 신선화(네가 실행)** — 커밋했으니 marketplace update 필요:
  - **Claude 세션**: `/plugin marketplace update changja88` → `/reload-plugins`
  - **Codex 세션**: `/plugin marketplace update dddjango-local`
  - ⚠️ **반드시 새 세션**에서 `/dddjango`(캐시 갱신 반영). 캐시 폴더가 `1.0.2/`로 새로 생기는지 확인하면 갱신 성공.

## 1. 고정 게이트 답 (양 런 공통 — 변수 제거, RETEST §1 재사용)
| 게이트 | 답 |
|---|---|
| G0 BC 배치 | **미강제** — "표준 판정-소유 원칙대로 결정" |
| G0 렌즈 | **ddd + db + api** (HTTP 409 계약 있음) |
| G0 스코프 | **제안대로** (확장 금지) |
| API 스택 | **"표준 기본대로"** — ⚠️ plain 강제 **금지**(표준이 스스로 Ninja로 수렴하는지가 본질) |
| 테스트 러너 | 제안대로 |
| G1 설계 / G2 구현 | **명백한 결함 없으면 무수정 승인** (게이트·백스톱 발화 자체가 관찰 대상) |
| thinking | **OFF** (coder) |

> 인터랙티브(Codex)에서 "venv 패키지 확인하라" 힌트 **금지** — 표준이 스스로 Ninja+핀으로 가는지가 테스트.

## 2. 태스크 (양 fixture 동일 — 주문생성, SD-7·NJ-4 둘 다 자극)
```
주문 생성 API. 별도 주문(order) 개념으로, 요청 상품·수량의 주문을 만든다. 재고는 기존 catalog가 소유하며, 주문 생성 시 catalog의 재고를 차감한다(재고 부족 시 409).
```
실행:
```bash
# Claude
cd ~/Desktop/dddjango-smoke6-claude && claude          # 새 세션
#  → /plugin marketplace update changja88 → /reload-plugins → /dddjango → 위 프롬프트 → §1 답
# Codex
cd ~/Desktop/dddjango-smoke6-codex && codex            # 새 세션
#  → /plugin marketplace update dddjango-local → /dddjango 트리거
# 끝나면(양쪽):
.venv/bin/python manage.py check && .venv/bin/python manage.py makemigrations && .venv/bin/python manage.py migrate && .venv/bin/python manage.py test
```

## 3. 기대 — 백스톱 발화 (G2 배너 직전)
| 백스톱 | 발화(blocker) 조건 = 위반 | 미발화 = 준수(정상) |
|---|---|---|
| **check-openapi-error-declaration** (NJ-4) | operation이 오류 status를 `openapi_extra`로만 선언·`response={...}` 누락 | 오류 status를 `response={...}`에 선언 |
| **check-context-isolation** (SD-7) | ACL 밖(presentation·application)이 catalog `domain_layer`/`infra_layer`(예외 포함) 직접 import | catalog 결합이 ACL에 격리(예외 번역 ACL 내·`infra_layer/acl/`만 import) |

> **정직(RETEST §65)**: catch(백스톱)는 위반이 없으면 미발화. 런타임이 준수하면 "미발화=정상"(생산자 예방 작동). **발화를 보면 catch 실효 확정**. 둘 다 의미 있는 결과다.
> 이전 자연 재현: `poc-codex`가 NJ-4 위반(openapi_extra), `p1a-v3-claude`가 SD-7 위반(ACL 밖 예외 누수) — **같은 주문생성 태스크라 재현 가능성 있음**. 재현되면 백스톱이 G2에서 잡아야 한다(이전엔 백스톱 부재라 통과했음).

## 4. 끝나면 나에게
- **"claude 끝났어" / "codex 끝났어"** — 내가 fixture의 `.dddjango/<기능>/design-spec.md`·`application/`·테스트·`requirements.txt`·**G2 백스톱 출력**을 직접 읽어 채점(파일은 내가 읽음).
- **G2 배너에 백스톱 blocker가 떴으면 그 원문**도 알려줘(라이브 발화 = 최강 증거).
- 런 중 막히거나 게이트가 헷갈리면 그대로 물어봐.

## 5. 내가 채점할 핵심
| 항목 | PASS 신호 |
|---|---|
| **NJ-4** | 오류 status가 `response={...}`에 선언(openapi_extra-only ✗). 백스톱 exit0(준수) 또는 발화→교정. |
| **SD-7** | ACL 밖에서 catalog domain/infra 직접 import 0. 예외 번역이 ACL 격리. 백스톱 exit0 또는 발화→교정. |
| 회귀 | P1a(중앙 핸들러)·구조·기능 정확성(409·재고 차감) 유지. |
