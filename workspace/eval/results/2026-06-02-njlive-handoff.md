# NJ-경계 가이드+백스톱 라이브 검증 — 실행 핸드오프 (2026-06-02)

> 너가 `/dddjango`를 직접 돌리고(드라이브), 끝나면 내가 G2 백스톱 발화·생성 코드를 채점한다.
> **목적**: 1.0.4(ninja 경계 가이드 §6.3 + 백스톱 2종)가 라이브에서 ① **예방**(코덱스가 406/415 협상 *미들웨어* 대신 ninja 경계로, 클로드가 problem 헬퍼를 `application/common/` 대신 BC presentation_layer에) ② **백스톱 발화**(위반 시 G2 차단)를 하는지. **N=1 sanity** — 우열·결정성 결론 아님.
> 처방 정본: `~/.claude/plans/shiny-petting-lovelace.md` (이번 세션 plan). 진단=DEVLOG(예정).

## 0. 준비 상태
- ✅ 백스톱 2종 신설(`check-ninja-boundary-middleware`·`check-common-container`) + 가이드 3미러(ninja §6.1/§6.2/§6.3·houserules §1·architecture-api §7.2) byte-identical + 게이트 **9종** 배선 + plugin **1.0.4** 범프. **미커밋(작업트리 상태)** — 두 marketplace가 *directory 소스*(`/Users/hyun/Desktop/dddjango` 작업트리 직결)라 **커밋 불요**.
- ✅ fixture 2개 clean baseline(Django 5.2.14·**py3.12**·**ninja 미설치**·seed Widget10/Gadget3·`catalog` 0001만·`application/` 없음·백스톱 2종 exit0·git clean):
  - `~/Desktop/dddjango-njlive-claude` — Claude
  - `~/Desktop/dddjango-njlive-codex` — Codex
  - (이전 `dddjango-smoke6-*` 원본은 **보존**됨 — 이건 clone 신규본)
- 🔲 **캐시 신선화(네가 실행)** — 1.0.4를 캐시에 반영:
  - **Claude 새 세션**: `/plugin marketplace update changja88` → `/reload-plugins`
  - **Codex 새 세션**: `/plugin marketplace update dddjango-local`
  - ⚠️ **반드시 새 세션**에서 `/dddjango`. 캐시 폴더가 `1.0.4/`로 새로 생기는지 확인하면 갱신 성공.

## 1. 고정 게이트 답 (양 런 공통 — 변수 제거)
| 게이트 | 답 |
|---|---|
| G0 BC 배치 | **미강제** — "표준 판정-소유 원칙대로 결정" |
| G0 렌즈 | **ddd + db + api** (HTTP 409 계약 있음) |
| G0 스코프 | **제안대로** (확장 금지) |
| API 스택 | **"표준 기본대로"** — ⚠️ plain 강제 **금지**(표준이 스스로 Ninja로 수렴하는지가 본질) |
| 테스트 러너 | 제안대로 |
| G1 설계 / G2 구현 | **명백한 결함 없으면 무수정 승인** (게이트·백스톱 발화 자체가 관찰 대상) |
| thinking | **OFF** (coder) |

> 인터랙티브(Codex)에서 "venv 패키지 확인하라"·"406/415 어떻게 처리하라" 힌트 **금지** — 표준이 스스로 ninja 경계로 가는지가 테스트다.

## 2. 태스크 (양 fixture 동일 — smoke6와 같은 프롬프트로 P-α·P-β 둘 다 자극)
```
주문 생성 API. 별도 주문(order) 개념으로, 요청 상품·수량의 주문을 만든다. 재고는 기존 catalog가 소유하며, 주문 생성 시 catalog의 재고를 차감한다(재고 부족 시 409).
```
실행:
```bash
# Claude
cd ~/Desktop/dddjango-njlive-claude && claude          # 새 세션
#  → /plugin marketplace update changja88 → /reload-plugins → /dddjango → 위 프롬프트 → §1 답
# Codex
cd ~/Desktop/dddjango-njlive-codex && codex            # 새 세션
#  → /plugin marketplace update dddjango-local → /dddjango 트리거
# 끝나면(양쪽):
.venv/bin/python manage.py check && .venv/bin/python manage.py makemigrations && .venv/bin/python manage.py migrate && .venv/bin/python manage.py test
```

## 3. 사전등록 신호 (PoC 프로토콜 — 발화=강한 확정 / clean=약한 positive)
| 백스톱 / 축 | 발화(blocker exit2) = 위반 | 미발화(exit0) = 준수(예방 작동) |
|---|---|---|
| **check-ninja-boundary-middleware** (P-α) | `presentation_layer` 미들웨어를 전역 `settings.MIDDLEWARE`에 자가등록(협상 자작) | 406/415를 ninja 경계(`Parser`/`HttpError`)로 내거나 미구현·기본 위임 — 미들웨어 0 |
| **check-common-container** (P-β) | `application/common/` 횡단 버킷(problem 헬퍼 조기 승격) | problem 헬퍼가 그 BC `application/<bc>/presentation_layer/`에(단일 BC) |

> **정직(PoC 프로토콜)**: 예방이 작동하면 백스톱은 **미발화(정상)**. *발화를 보면 catch 실효 확정*(1건이면 충분). *clean이면 약한 positive*(이번 런이 운 좋게 준수했을 수 있음 → N>1 필요). 둘 다 의미 있다.
> **이전 자연 재현**: 코덱스 **3런**(smoke3·smoke6·final-codexB) 협상 미들웨어, 클로드 smoke6 `application/common/ninja`. **같은 주문생성 태스크라 재현 가능성 있음** — 재현되면 백스톱이 G2에서 잡아야 한다(이전엔 백스톱·가이드 부재라 통과했음).

## 4. 끝나면 나에게
- **"claude 끝났어" / "codex 끝났어"** — 내가 fixture의 `.dddjango/<기능>/design-spec.md`·`application/`·`config/settings.py`·`requirements.txt`·**G2 백스톱 출력**을 직접 읽어 채점(파일은 내가 읽음).
- **G2 배너에 백스톱 blocker가 떴으면 그 원문**도 알려줘(라이브 발화 = 최강 증거).
- 런 중 막히거나 게이트가 헷갈리면 그대로 물어봐.

## 5. 내가 채점할 핵심
| 항목 | PASS 신호 |
|---|---|
| **P-α (협상 미들웨어)** | `settings.MIDDLEWARE`에 `application.*.presentation_layer.*` 항목 0. 406/415는 ninja 경계(`Parser`/`HttpError`) 또는 미구현. 백스톱 exit0(준수) 또는 발화→교정. |
| **P-β (common 레벨)** | `application/common/` 0. problem 헬퍼가 BC `presentation_layer/`(단일 BC). 백스톱 exit0 또는 발화→교정. |
| 회귀 | 기능 정확성(409·재고 차감)·중앙 오류 핸들러(P1a)·구조 골격 유지. |
