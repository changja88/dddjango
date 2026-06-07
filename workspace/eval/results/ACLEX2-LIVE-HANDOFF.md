# ACL-EX2 예방(B 트랙) 라이브 배선 검증 핸드오프 (2026-06-07)

> 너가 `/dddjango`를 직접 돌리고(드라이브), 끝나면 내가 산출물을 읽어 채점·⑮ 배선 검증한다.
> **목표**: B 트랙 ACL-EX2 예방(커밋 `8f6922c`·plugin 1.7.0)이 라이브서 **① 예방(텍스트 효과)** = ACL이 CAS 소진을 *도메인 transient-마커 타입*으로 raise(합성 `OperationalError` 아님)·EP-3=503 / **② 백스톱 ⑮ 배선** = G2 게이트서 실행·합성 시 차단(exit2)하나.
> **정직 경계**: **N=1·P4③** — ACL-EX2는 Claude 단일 인스턴스 흠(Codex는 대안 B로 부재). 1회 런은 *증명*이 아니라 *예방 작동/배선 관찰*. 우열 결론 아님. ⑮ 자연 발화는 텍스트가 예방하면 안 일어나는 게 정상 — 배선은 내가 proxy 주입(DR-30식)으로 확인.

## 0. 준비 상태 (내가 완료)
- ✅ **커밋 `8f6922c`**(B 트랙 7편집·14파일·미푸시·브랜치 `eval/codex-determinism-n2`). 직전 `d9049da`(A트랙)·`57e6141`(maj1).
- ✅ **캐시 신선화 1.7.0**: Claude(`~/.claude/plugins/cache/changja88/dddjango/1.0.0`)·Codex(`~/.codex/plugins/cache/dddjango-local/dddjango/1.0.0`) 둘 다 plugin 1.7.0·게이트 **15종**·⑮ `check-synthetic-infra-exc.py` 안착·repo와 byte-id.
- ✅ **fixture greenfield**: `~/Desktop/dddjango-aclex2live-{claude,codex}` — baseline clone(claude `6e48b68`/codex `32d1cf5`)·`.venv` **Django 4.2.30만**(ninja/pytest 미설치)·catalog.Product **Widget(10)·Gadget(3)** 시드·`application/order` 없음·`manage.py check` 0 issues·git clean.
- ⚠️ **반드시 새 세션** — 캐시를 방금 갱신했다(기존 세션은 구 에이전트 텍스트 메모리 보유; 기존 세션 쓰려면 `/reload-plugins` 후).

## 1. 태스크 (maj1live와 **동일 입력**·변수 통제)
```
주문 생성 API. 별도 주문(order) 개념으로, 요청 상품·수량의 주문을 만든다. 재고는 기존 catalog가 소유하며, 주문 생성 시 catalog의 재고를 차감한다(재고 부족 시 409).
```
> ⚠️ 동시성·CAS·예외 형식·입력 상한을 **프롬프트에 명시하지 않는다** — 표준이 스스로 하는지가 관찰면. 이 태스크가 낙관적 CAS 동시성을 끌어내 catalog 재고차감 ACL을 자연 발생시킨다(ACL-EX2 관찰점 = ACL이 CAS *소진*을 어떻게 신호하나).

## 2. 고정 게이트 답 (maj1live와 동일)
| 게이트 | 답 |
|---|---|
| G0 BC 배치 | **미강제** — "표준 판정-소유 원칙대로 결정해줘" |
| G0 렌즈 | **ddd + db + api** |
| G0 스코프 | **제안대로** |
| API 스택 | **"표준 기본대로"** — ⚠️ plain 강제 **금지**(DR-31) |
| 테스트 러너 | **"표준 기본대로"** |
| G1 멱등성/버전 | **미도입**(`/api/orders`) |
| G1 409 본문 | available/requested 노출(기본) |
| G1 설계 / G2 구현 | **명백한 결함만 반송**(ACL transient 신호 형식·상한은 *관찰 대상*이라 유도 금지) |
| thinking | **OFF** (coder) |

## 3. 실행
**Claude**: `cd ~/Desktop/dddjango-aclex2live-claude` → `claude`(새 세션) → `/dddjango` → §1 → §2
**Codex**: `cd ~/Desktop/dddjango-aclex2live-codex` → `codex`(새 세션) → §1 → §2
**끝나면 스모크**: `.venv/bin/python manage.py check && .venv/bin/python manage.py migrate && .venv/bin/pytest`
**끝나면 나에게 "claude 끝났어" / "codex 끝났어"** — 내가 fixture에서 직접 읽어 채점·⑮ 배선 검증.

## 4. ACL-EX2 확인 포인트 (B 트랙 초점 — 내가 채점)
### ⓐ 예방(텍스트 효과) — *주된 관찰면*
- **ACL이 CAS 재시도 *소진*을 어떻게 신호하나** — `application/<order>/infra_layer/acl/*adapter*.py`:
  - ✅ **도메인 transient-마커 예외 *타입*** raise(`StockContention`류·retryable 의미) → houserules:143/§6.2 신규 처방 준수.
  - ❌ **합성 `OperationalError`/`DatabaseError`**(`from` 없이·메시지만) raise → **ACL-EX2 재발**(직전 Claude maj1live:82 흠).
- **EP-3 종단(§4.3.1 매트릭스)**: 내가 probe(CAS 소진 강제 주입)로 HTTP status 확인 — **503/409(retryable)=통과** / **500=ACL-EX2**. type i(raw 종단)/type ii(도메인 경로) N/A 규칙 적용.
- **houserules 효과**: ACL 주석/코드가 "위장 번역 금지"를 *드라이버 실제 throw*에만 적용하고 *계산된 소진*은 도메인 타입으로 가르나(coin-flip 해소).

### ⓑ 백스톱 ⑮ 배선 — DR-30식(내가 검증)
- **G2 게이트 시퀀스에 ⑮ 실행됐나** — 런 중 "결정적 백스톱(15종)" 배너·15개 스크립트 실행 보이면 알려줘(또는 내가 run 로그/산출물로 확인).
- **proxy 차단 검증**: 클린 산출물(도메인 타입)이면 ⑮ exit0이 정상(예방 성공이라 발화 안 함). 내가 *합성 주입*(ACL에 `raise OperationalError(...)` from 없이) 후 캐시 ⑮ 재실행 → **exit2 차단 확인**(maj1 ⑭ DR-30 동형). 자연 발화는 기대 안 함.

### ⓒ min1 (부수)
- 입력 schema의 `product_id` 등 외부 식별자에 **상한**(`le=`/`lt=`) 선언했나 — reviewer important 승격 효과(없으면 거대 입력→500, 단 underdetermined).

## 4.5 채점 진행 상황 (2026-06-07·compact 경계)
- ✅ **Codex 완료 = PASS**(채점지 `20260607-2022-aclex2live-codex.md`): ACL-EX2 부재(대조군·대안 B)·EP-3=503 실측·⑮ 배선 양방향(exit0+proxy exit2)·min1·maj1·FC 동시성 강함. **🟠 2 후속 후보**: ① catalog 중앙화 *형식* 완전성 갭(`handle_operational_error` permanent시 `raise exc`+catch-all 부재→problem+json 우회·§6.2:467 위반·reviewer 형식-완전성 사각) ② DR-42 집행 갭(⑬이 pytest *부재* 면제→Codex 계속 미채택). nit=영어 docstring(reviewer line45).
- 🔄 **Claude 진행 중**: 통제 게이트 부여=멱등성 미적용·**transient status 503**(Codex와 변수 통제)·승인. "claude 끝났어" 대기 → **migrate 적용 후** 동일 EP probe+⑮+ACL-EX2 채점. **진짜 검증**=직전 maj1live ACL-EX2 보유자가 B 트랙으로 합성→도메인타입 전환하나.
- **EP probe 패턴**(재사용·Claude는 구조 달라 신규 작성): Django `Client`+`settings.ALLOWED_HOSTS=['*']`·EP-3=CAS 메서드 monkeypatch→False로 소진 강제·라이브 산출은 migrate 미적용이라 **먼저 `manage.py migrate`** 필요.

## 5. 정직 경계 (채점 시 내가 지킴)
- **N=1·P4③** 우열·완료 결론 금지. ACL-EX2는 Claude 특정 인스턴스(Codex 대안 B로 부재) — Codex 런은 *대조군*(여전히 도메인 타입이면 정상).
- **라이브 배선 첫 관측**: ⑮ 발화는 DR-30식 proxy로만(자연 발화는 예방이 막으면 정상 부재). 텍스트 효과(예방)가 주 신호.
- **소급 금지**: §4.3.1 EP-3은 관측 트랙(치명 게이트 아님)·이 fixture는 1.7.0 산출이라 정상 적용.
