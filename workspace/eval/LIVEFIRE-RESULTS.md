# P1a 백스톱 라이브-파이어 스모크 결과 (2026-05-31)

> **목적**: DR-20 P1a 집행 백스톱(`discipline-reviewer` "API 오류 응답 중앙화 규율")이 *실제 `/dddjango` 라이브 파이프라인*에서 발화하는지 확인사살 + P1b·P2·P3 라이브 재확인.
> **방식**: dual-runtime 통제 비교 — 같은 태스크·게이트, 런타임만 다름. 캐시 양쪽 byte-identical 신선화(백스톱 포함). 각 N=1.
> **fixtures**: `~/Desktop/dddjango-p1a-livefire-{codex,claude}` — Django 5.2.14·py3.12·ninja 미설치(유기적)·PROMPT 제거·git baseline.
> **태스크(verbatim, smoke2 원본)**: "주문 생성 API. 별도 주문(order) 개념으로, 요청 상품·수량의 주문을 만든다. 재고는 기존 catalog가 소유하며, 주문 생성 시 catalog의 재고를 차감한다(재고 부족 시 409)."
> **정직 경계**: 각 N=1·런타임별 동일 태스크. "각 런타임에서 집행이 작동/준수했나"까지지 "런타임 우열" 아님.

---

## 한눈에 보기

| P | 의미 | **Codex** | **Claude** |
|---|---|---|---|
| **P1a** | ninja 오류→HTTP 중앙화 | 🔴 **위반 + 백스톱 다운그레이드**(권고로 분류, 미차단) | ✅ **유기적 준수**(operation raise·중앙 핸들러 4종) |
| **P1b** | 의존성 버전 신선 핀 | ✅ `django-ninja==1.6.2` | ✅ `django-ninja==1.6.2` |
| **P2** | 메커니즘-소유권(커스텀 백엔드 금지) | ✅ CAS·백엔드0·`check-mechanism-ownership.py` exit0 | ✅ stock `transaction_mode: IMMEDIATE`(커스텀 백엔드0) |
| **P3** | §9.6 Risky Write 테스트 실현 | ✅ **blocker 라이브 발화**→교정 | ✅ 유기적 준수(oversell·CAS-스파이 테스트) |

**핵심**: P1b·P2·P3는 양 런타임 모두 합격(P3는 Codex에서 라이브 발화로 catch 재확인). **P1a만 갈림 — Claude 준수 / Codex 위반인데 백스톱이 *blocker로 못 막고 권고로 다운그레이드*.** → 신규 문제 NEW-1.

---

## P1a — ninja 오류 응답 중앙화 (백스톱 라이브-파이어)

### Codex 🔴 위반 + 백스톱 다운그레이드 (핵심 발견)
- **코드(textbook 위반)**: operation `create_order`가 `-> JsonResponse` 반환(스키마 아님), 본문에서 직접 오류 응답 수제 생성 — idempotency-missing 400(`api_orders.py:49-59`), content-negotiation 415/406(`:75-105`), `_response_from_result`가 `JsonResponse(result.body, status=result.status_code)` 조립(`:108-117`). 도메인 예외→status+Problem Details 매핑은 **application service**(`create_order_app.py:92-166`). 중앙 `@api.exception_handler`는 **ValidationError 하나뿐**(`orders_api_router.py:19`).
- **백스톱 거동**: discipline-reviewer가 캐시에서 백스톱 텍스트를 정상 로드(시스템프롬프트에 "blocker): @router.* operation 본문이..." 확인)하고 위반을 **인지**했으나 — G2 리포트에서 **"API 오류 응답/Problem Details 생성이 application layer에 섞여 있어 책임 배치가 약합니다"를 *권고*로 분류**(blocker 아님). G2 요약의 blocker 2건은 멱등성 트랜잭션 + Risky Write(P3)였고, **P1a는 미차단으로 G2 통과**. (출처: codex 세션 `rollout-2026-05-31T01-43-07-*.jsonl` discipline-reviewer 리포트.)
- **판정**: 🔴 **백스톱 라이브 다운그레이드** — 명백한 위반을 blocker로 못 올림. → NEW-1.

### Claude ✅ 유기적 준수
- **operation**(`application/order/presentation_layer/api/create_order/api_order.py:83-87`): 본문이 command 변환→app 실행→`return 201, _to_response(order)`만. try/except·status선택·JsonResponse 전무. `-> tuple[int, CreateOrderOutSchema]`. docstring에 "모든 예외는 raise되어 중앙 핸들러로 간다 … operation 본문에서 try/except로 status를 고르거나 problem+json/JsonResponse를 만들지 않는다(P1a 규율)" 명시.
- **중앙화**(`presentation_layer/api/error_handlers.py`): `@api.exception_handler` 4종(OrderDomainError·CatalogDomainError·ValidationError·HttpError) + `api.create_response`(:84) 중앙 빌더. 오류→status 매핑은 **presentation layer**(`problem.py`)에 위치(Codex의 application service와 *레이어가 다름* — 올바른 곳).
- **판정**: ✅ **처방된 P1a 패턴 그대로**. 백스톱이 침묵(거짓양성 0).

---

## P1b — 의존성 버전 신선 핀
- **Codex**: `requirements.txt` → `django-ninja==1.6.2`. ✅
- **Claude**: `requirements.txt` → `Django==5.2.14` + `django-ninja==1.6.2`. ✅
- 양쪽 ninja 미설치 fixture에서 유기적으로 최신 안정(1.6.2) 핀. houserules §6.2 라이브 작동.

## P2 — 메커니즘-소유권 (커스텀 백엔드 금지)
- **Codex**: version CAS + `select_for_update`, 커스텀 백엔드 0. `check-mechanism-ownership.py` **exit 0**(coordinator G2 배선 실행). ✅
- **Claude**: stock `ENGINE='django.db.backends.sqlite3'` + `OPTIONS.transaction_mode: 'IMMEDIATE'`(`config/settings.py:89`) — **stock 5.2 OPTION으로 IMMEDIATE 획득, 커스텀 DatabaseWrapper 0.** 메커니즘 백스톱 통과. ✅ *이게 P2 픽스의 의도된 결말* — baseline을 5.2.14로 올려 stock transaction_mode 경로를 줬더니 (원래 커스텀 BEGIN IMMEDIATE 백엔드를 만들던) 그 자리에서 합법 경로로 착지.
- (참고: Claude가 TEST.NAME을 파일 DB로 설정 — 테스트 전용이라 백스톱 정상 통과.)

## P3 — §9.6 Risky Write 테스트 실현
- **Codex** ✅ **라이브 발화**: discipline-reviewer가 "명세가 Risky Write 테스트 기준(deterministic CAS conflict retry·concurrent oversell 방지)을 선언했으나 구현 테스트로 실현 안 됨"을 **blocker**로 잡음 → coder가 테스트 보강. (G2 blocker 2건 중 하나. smoke2와 일관된 catch 라이브 작동.)
- **Claude** ✅ **유기적 준수**: 동시성/CAS 테스트를 스스로 작성 — `test_create_order_concurrency.py`(`test_concurrent_single_unit_orders_do_not_oversell`·`test_concurrent_varying_quantity_orders_never_oversell`), `test_create_order_app.py`(`test_cas_conflict_once_then_converges_via_full_retry`·`test_cas_conflict_exhausts_retries_and_propagates`). blocker 불필요. (73 tests green.)

---

## 🆕 신규로 발생한 문제

### NEW-1 — P1a 백스톱이 라이브에서 blocker로 발화하지 않고 "권고"로 다운그레이드 (🔴 릴리스 차단급)
- **현상**: Codex가 낸 **명백한 P1a 위반**(operation 본문 수제 JsonResponse + application service 오류 매핑 + 중앙 핸들러 1개뿐)을, discipline-reviewer가 백스톱 텍스트를 *로드하고도* **blocker가 아닌 권고**로 분류해 G2를 통과시킴.
- **왜(가설)**: 위반 형태가 N=9 텍스트-판별의 known-bad(operation에 흩뿌려진 수제 응답)와 달리 **"단일 매퍼(app service) + `_response_from_result` 헬퍼"** = "한 곳에 모였지만 레이어가 틀림"으로 보임 → reviewer가 "책임 배치가 *약함*(권고)"으로 읽음. 거짓양성 carve-out **(a) "중앙 변환점이 하나라도 있으면 충족"**(ValidationError 핸들러 1개 존재)이 blocker를 약화시켰을 가능성.
- **N=9 텍스트-판별이 못 잡은 이유**: N=9는 *고립된 체크를 "적용하라"고 준* 조건 → 9/9 blocker. 라이브 reviewer는 *전체 에이전트 + carve-out + 홀리스틱 심각도 판단 + 경쟁 발견(멱등성·Risky Write blocker)* 맥락 → 같은 위반을 권고로 강등. **교훈: 텍스트-판별 통과 ≠ 라이브 발화.**
- **대조 증거(중요)**: 같은 런에서 **P3 백스톱은 blocker로 발화**, P1a만 강등 — 즉 catch 메커니즘 자체는 작동하는데 **P1a 백스톱 *문구가 약함*.** Claude는 준수해서 트리거 안 됨(거짓양성 0은 유지).
- **함의**: **현 P1a 백스톱을 머지하면 라이브에서 P1a를 실제로 못 막는다.** → **릴리스 보류**, 백스톱 강화 필요. 강화 방향(후속 설계): ① app-service/operation의 오류→status 생성을 blocker로 *확실히* 올리도록 문구 강화 ② carve-out (a)가 "틀린 레이어의 단일 소유자(app service)"·"부분 핸들러(ValidationError만)"를 봐주지 않게 조이기 ③ "도메인/application layer가 HTTP status·Problem Details를 만들면 blocker"를 명시. **단 게이트 추가가 아니라 기존 discipline-reviewer 문구 강화로**(NEW-2 회귀 우려와 충돌 회피). 구현 전 적대 리뷰 재실행.

### NEW-2 — 런타임 회귀 의심 (⚠️ 측정 필요)
- **현상**: Claude 라이브-파이어 런이 **1시간 12분+** 경과(관측 시점·진행 중), 확립된 기준 **~38~45m(smoke8 @`15ff62d`, 하드닝 이전)** 크게 초과.
- **가설**: 시간 단축 작업(thinking-off 등) *이후* 추가한 **하드닝(P2·P3·P1a 백스톱 + ③④, `15ff62d`→`bc75714` 17커밋)이 게이트를 늘려 coder 반송↑**. 왕복이 wall 지배 요인이라(비용 최적화 레버 #1 결론) 게이트 추가 = 직접 wall 증가. *같은 런 Codex가 G2에서 blocker 2건으로 반송*함이 실측 예.
- **교락(정직)**: ① smoke8과 다른 태스크 ② Claude가 catalog **풀 도메인 이주(A)** 선택=무거움 ③ N=1·최종시간 미확정 ④ 어느 게이트 탓인지 분리 안 됨.
- **측정 결과(런 종료 후 `session_telemetry.py`)**: Claude 세션 **WALL 92m**(그중 코디+게이트≈37.4m은 인터랙티브 게이트 대기 idle 다수), **machine(서브에이전트 겹침병합)=54.6m** vs 기준 ~38~41m → **~+33%**. **단 회귀 가설 깨끗이 미지지**: 증가분 대부분이 **coder n=4(29.8m)+architect n=2(16.3m)** = **무거운 태스크(catalog 풀 도메인 이주 A + order BC + 멱등성 + 동시성 = 다중 슬라이스)**와 정합. **discipline-reviewer(P1a/P2/P3 체크)는 1회·무반송** — 하드닝 게이트가 coder를 반복 튕긴 게 *아님*. **결론: 상승은 태스크 heaviness 주도, 하드닝 직접 기여는 미확인(교락).** 순수 하드닝 비용 격리엔 same-task A/B(pre `15ff62d` vs post `bc75714`) 필요 → 사용자 '회귀 의심'은 측정상 **부분 반증**(레버 #1 교훈 재확인). (메모리 `dddjango-cost-token-optimization` 기록됨.)

---

## 강화 v2 + 사전 시뮬 (2026-05-31, DR-22 — NEW-1 후속, 문구 강화 불충분 확인)
NEW-1 강화 방향대로 discipline-reviewer 백스톱 문구를 강화(v2)하고 사전 시뮬로 검증했으나 **또 0/3**.
- **강화 v2**(2미러 byte-identical·`validate` PASS, 구현 전 적대 리뷰 3렌즈): carve-out (a) ∃→∀(부분 핸들러=면제 아닌 blocker 명시) + 레드플래그를 operation→**operation·application·domain 어디든**으로 확장 + **단일 판별 게이트**("status 선택·problem body 생성이 presentation 변환점 밖에서 실행되나") + "operation 본문 밖"→"operation·application 계층 밖" 5곳 치환. 적대 리뷰가 carve-out (d)·옵션(비교-불변 잠금) 기각·분량 순증≈0 압축.
- **사전 시뮬(N=3, 강화 reviewer를 저장 Codex 산출물 `dddjango-p1a-livefire-codex`에 적용, 캐시 md5 확인)**: **P1a blocker 0/3.** sim-1·2 = P1a **점검 누락**(catalog 마이그레이션·테스트 구조에 주의 쏠림), sim-3 = **옛 ∃ 논리로 통과**("`@api.exception_handler(ValidationError)` 핸들러 존재→충족", ∀ 강화 미적용). 세 리뷰어 모두 app service의 오류→status 매핑을 *읽고도*(sim-1은 그 줄 직접 인용) P1a로 연결 못 함.
- **결론**: **bullet 문구 강화만으론 부족** — 적대 리뷰 **렌즈3 예언 실증**(silent downgrade/누락은 bullet이 아니라 주의 배분·산출 형식에서 발생). 이번엔 **Claude 리뷰어조차 강화 미적용** → 문구 약함이 런타임 무관. → **v3는 구조적 개입**: (가) 명시 판정 강제 (나) 생산자(design-architect) 예방 (다) 결정적 백스톱 (라) 산출 형식 보강. 직감 (가)+(나), 구현 전 적대 리뷰로 우선순위 확정. 정본=`workspace/DEVLOG.md` DR-22.

---

## v3 — 결정적 백스톱 + 생산자 예방 (2026-05-31, DR-23 — P1a actionable 해결)
v2 문구 강화가 사전 시뮬 0/3(LLM 집행 불안정)이라, **결정적 스크립트 + 생산자 예방 + 강화 v2 reviewer**의 3층으로 전환(사용자 두 제약 "반드시 적용 + 동작 시간 안 늘림"의 교집합 = 결정적 백스톱).
- **(다) `check-error-centralization.py`** 2미러: `/application_layer/` 파일이 HTTP status/응답을 직접 생성하면 exit2(AND: 경로·응답신호[`JsonResponse(`/`HttpResponse(`/`status[_code]=[45]\d\d`/`HttpError([45]\d\d`/`from ninja` import]·diff-only). P2 골격(SKIP_DIRS·diff-only·exit 0/2/1) 차용. 구현 전 적대 리뷰 3렌즈(거짓양성=하·HttpError/ninja-import 추가·§6.2 스킬명·단락정책·통과≠면제).
- **(나) design-architect 명세** 2미러: "오류→status 변환은 presentation 단일 소유(`@api.exception_handler`/`create_response`), application/domain은 HTTP status·problem body 안 만듦(`implementation-django-ninja §6.2`)".
- **coordinator 배선** 2미러(`dddjango.md`+codex `SKILL.md`): G2 직전 백스톱 2종, 하나라도 exit2→합쳐 반송, ②통과(0)≠reviewer 면제.
- **검증(결정적)**: `validate`✔·미러 md5·**위반본 exit2**(`create_order_app.py` 정확 지목)·**준수본 exit0**(거짓양성0)·거짓양성 가드(성공status·읽기·import-only→exit0/`JsonResponse status=404`→exit2)·시간 **0.21s**. **v2 LLM 0/3 → v3 스크립트 100% 결정적**(위반 항상 exit2·같은 코드→같은 결과). LLM 불안정 우회로 **P1a actionable 결정적 해결.**
- **정직 경계**: 스크립트는 application_layer HTTP 누수(라이브 위반 형태)만 고정밀. operation 본문 수제·status맵추출·변수우회는 (나)예방+강화 v2 reviewer 위임. **남은=라이브 배선 발화(B)**(coordinator가 G2서 실제 호출→반송).

## 종합 함의
- **P1b·P2·P3는 라이브에서 견고**(P3는 Codex 발화로 catch 재확인, P2는 Claude가 stock transaction_mode로 의도된 착지). 이 세 집행은 릴리스 가능 수준.
- **P1a actionable(백스톱 재현율) 해결**(NEW-1): v2 LLM 0/3 → **v3 결정적 백스톱(DR-23) 위반본 exit2/준수본 exit0·시간0.21s**. **남은=라이브 배선 발화(B)** → 통과 시 P1a 릴리스 보류 해소.
- v3는 **새 LLM 게이트 추가 없이**(NEW-2 회귀 우려) coordinator Bash 1회(시간 ~0)로 결정적 catch + 생산자 예방(반송↓로 단축) 달성.
- 정직 경계: 각 N=1·태스크 동일·우열 결론 아님. Codex 위반엔 멱등성·content-negotiation 복잡도 교락이 여전히 큼.

> 정본 상태표: `workspace/eval/REMAINING-ISSUES.md` · 결정 기록: `workspace/DEVLOG.md`(DR-20~22) · 메모리: `dddjango-final-smoke-findings`·`dddjango-cost-token-optimization`.
