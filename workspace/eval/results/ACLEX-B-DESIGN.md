# ACLEX-B-DESIGN — ACL-EX2 예방 처방(B 트랙) 적대 리뷰용 후보

> 상태: **적대 3렌즈 대기**. A 트랙(EVAL-METHOD §4.3.1 에러경로 관측)은 완료·커밋(`d9049da`) — *탐지*는 보장됨. B는 *예방*(코드/표준이 옳아지게). 이 문서는 표준-텍스트 변경 전 적대 검증을 받기 위한 후보다.

## 0. 고정(relitigate 금지)
- A 트랙(§4.3.1) = 완료·커밋. maj1 처방(salience+reviewer+백스톱 ⑭) = 완료·라이브 검증(`57e6141`).
- DR-44/45 ACL 전수성 처방(houserules:143·포트앵커 E·reviewer C1/C2) = 시행 중. *진짜 raw 인프라 예외* 경로는 이걸로 다룸.
- 질문은 **오직 B 트랙** = ACL-EX2 예방 + min1 승격. 33항목 RUBRIC = freeze(불변).

## 1. 문제 (A가 탐지, B가 수정)
**ACL-EX2** (maj1live-claude 라이브 재현·probe EP-3=500):
- Claude ACL `application/order/infra_layer/acl/product_stock_adapter.py:82` — CAS 소진(낙관락 재시도 `_MAX_CAS_RETRIES=3` 실패) 시 **합성 `OperationalError(f"재고 차감 CAS 경합이 ...회 재시도로 해소되지 않음...")`** raise (한국어 메시지·`from` 없음=`__cause__` 없음).
- presentation `error_handlers.py:59-71` `_is_retryable_db_error` — 메시지 "locked"/"deadlock detected"/"could not serialize access" **또는** `__cause__` SQLSTATE 40001/40P01만 인식.
- 합성 메시지가 어느 것도 매칭 안 됨 → 핸들러가 영구장애로 분류 → **HTTP 500** (의도는 503 retryable).
- **Codex 대안 B**(`orders/infra_layer/acl/product_stock_adapter.py:23` + `orders_api_router.py:119-130`) — CAS 소진을 **도메인 예외 *타입*** `ProductStockContention`→`ProductStockUnavailable`로 번역, 핸들러가 *타입*으로 503 매핑. **구조적 면역**(메시지/시그니처 의존 0).

## 2. 후보 처방 핵심 — 3-way 구분 명문화
현 표준(houserules:143·ninja §6.2)은 transient를 **2-way**로 본다: ① 실 raw 인프라 예외(경계로 흘려 시그니처 recognize) ② 도메인 예외(위장 번역 금지). ACL-EX2는 **세 번째 케이스가 사각**임을 드러낸다:

| 종류 | 정의 | 올바른 처리 | 근거 |
|---|---|---|---|
| **(1) 실 드라이버 raw transient** | DB 드라이버가 raise한 `OperationalError("database is locked")` 등 — 진짜 발생, 실 메시지/`__cause__` 보유 | 도메인 위장 금지, 경계까지 흘려 `_is_retryable_db_error` 시그니처 recognize → 503 | **불변**(houserules:143·ninja §6.2) |
| **(2) 애플리케이션-계산 transient** | ACL/앱의 낙관락·CAS 재시도 루프가 *스스로* 소진 판정 — 드라이버 예외 부재, 계산된 도메인/앱 결과 | **도메인 transient-마커 예외 *타입*** raise → 핸들러 *타입* 매핑 → 503 | **신규**(Codex 대안 B = 정답 모델) |
| **(3) 금지 안티패턴(ACL-EX2)** | 계산된 조건을 인프라 예외 타입(`OperationalError`/`DatabaseError`/`IntegrityError`)으로 **합성/위장** | **금지** — recognizer 사각(실 메시지/SQLSTATE 부재) → 500 오분류 | 신규 금지 |

**핵심 원리**: 시그니처 recognizer(메시지/SQLSTATE)는 **진짜 드라이버 예외 전용**(실 신호가 있을 때만). *계산된* transient는 **타입 매핑**(ACL이 도메인 마커 타입으로 번역, 핸들러가 isinstance로 503). 합성 인프라 예외 = 두 경로 어디에도 안 맞는 최악수.

**houserules:143과의 정합(모순 아님 주장)**: 기존 "ACL은 transient를 도메인 예외로 위장 번역 안 함"은 **종류(1)**(실 드라이버 예외)에 한정 — 실 인프라 예외를 도메인으로 둔갑시켜 포트에 인프라 누수시키지 말라는 뜻. **종류(2)**는 애초에 인프라 예외가 *아니라* 앱이 계산한 도메인 결과("재고 경합이 재시도로 안 풀림")이므로 도메인 예외로 raise하는 게 *맞다*. 구분축 = **provenance**(드라이버가 던졌나 vs 앱이 계산했나).

## 3. 결정 후보
- **D1 (표준 텍스트)**: houserules:143 + ninja §6.2 transient 절에 **종류(2)·(3)** 명문화. "낙관락/CAS 재시도 소진처럼 *앱이 계산한* transient/경합은 도메인 transient-마커 예외 타입으로 raise하고 핸들러가 타입 매핑한다. 인프라 예외 타입(`OperationalError`/`DatabaseError`)을 *합성*해 transient를 신호하지 않는다 — recognizer는 실 드라이버 예외 전용." 미러 claude↔codex byte-id.
- **D2 (종단 테스트 의무)**: CAS 소진 → HTTP 503 end-to-end(경계 우회 주입 금지·실 ACL→핸들러 경로). min3 경계-스파이·DR-44 B와 합류. acceptance-tester/test 표준.
- **D3 (min1 reviewer 승격)**: §5.1 외부 식별자 입력 상한(`product_id` 등) reviewer nit→important. (별개·작음·§5.1 텍스트 `final.md:186` 기존)
- **백스톱 = NO** (N≥2 라이브 후·memory 일관). ⑭ 등 11종 누구도 ACL↔핸들러 어휘 정합 원리상 못 봄.

## 4. 적대 렌즈가 깰 지점 (열린 긴장 — 반증 환영)
1. **houserules:143 모순 위험**: "transient를 도메인으로 위장 말라" ↔ "계산 transient는 도메인 타입으로". provenance 구분이 코더에게 *actionable*한가, 아니면 사후 합리화인가? 두 케이스를 혼동 없이 진술 가능한가?
2. **N=1 vs 테마 3×**: ACL-EX2 = Claude 단일 인스턴스, Codex 구조적 면역. 표준 변경이 N=1에 정당한가, 아니면 reviewer-only/defer(백스톱처럼 N≥2)? 테마(DR-44/45/EX2)는 같은가 *다른 메커니즘*인가?
3. **더 단순한 근본?**: 진짜 버그가 "가짜 메시지로 예외 합성 금지"(cleancode 규칙)일 뿐, ACL 규칙이 아닐 가능성? 또는 코더 미규율(N=1)이라 기존 텍스트로 이미 금지?
4. **D2 과처방**: min3 경계-스파이 통합 테스트가 이미 write-conflict→409 종단. CAS 소진→503이 *자기* 종단 테스트를 따로 의무화할 필요 있나, 포섭되나?
5. **대안 B 과강제**: 도메인-타입 매핑을 THE way로 못박으면 설계공간 과축소? `__cause__` 보존·공유 마커 등 방어가능 대안을 표준이 허용해야?

## 5. 렌즈 산출 요구
각 렌즈는 **GO / MODIFY / NO-GO** 판정 + 근거 + (MODIFY면) 구체 수정안. 특히 §4의 긴장 중 자기 렌즈 소관을 정면 반증 시도. 읽기 전용(편집 금지). 픽스처 코드 확인 가능: `~/Desktop/dddjango-maj1live-{claude,codex}`.

---

## 6. 적대 3렌즈 종합 + 조정자 검증 (2026-06-07)
세 렌즈 모두 **MODIFY**. 후보의 두 전제를 반증, 조정자가 load-bearing 사실 직접 검증.

### 반증 1 (렌즈 A·grep 확인) — provenance 축 폐기 + "Codex 면역" 거짓
- Codex catalog `decrement_product_stock_command.py`도 *같은* 메시지-매칭 recognizer(`is_retryable_operational_error`) 보유 — 위치만 상류(catalog)로 이동, "시그니처 의존 0·구조적 면역" 서사 **거짓**(grep 확인).
- 진짜 차이: Codex recognizer가 raw 락을 **도메인 타입**(`ProductStockContention`)으로 즉시 번역, CAS 소진도 같은 도메인 타입으로 raise → 핸들러 *타입* 매핑 503. Claude는 CAS 소진을 **인프라 예외(`OperationalError`) 합성** → recognizer 사각 → 500.
- **교정 근본축 = "받아서 recognize(외부 신호) / 만들어서 raise(도메인 타입)"** (provenance="누가 던졌나" 아님). 우리 코드가 transient를 *raise*할 땐 도메인 마커 타입; 인프라 예외는 *받는* 외부 신호일 뿐 표현 매체로 합성 금지. houserules:143("받은 인프라 예외를 도메인으로 둔갑 말라"=입력측)과 신규("transient *만들* 땐 도메인 타입=출력측")는 **한 원리의 양면** — 모순 없이 화해(provenance 불필요).

### 반증 2 (렌즈 C 주장 → 조정자 *정정*) — "이미 다 있다"는 과장이나 일부 옳음
- 렌즈 C "reviewer line 41 완전성 렌즈가 이미 ACL-EX2를 important로 잡음" → **조정자 직접 확인 결과 틀림**: line 41·42 두 transient 불릿은 *핸들러*만 봄(존재/분기 유무). ACL-EX2는 핸들러 *존재·분기 有*인데 ACL 합성 신호를 recognizer가 못 읽어 500 → **두 불릿 다 사각**(ACL 출력=생산자 쪽 미커버). **reviewer 갭 실재.**
- 렌즈 C가 *맞은* 것: ① §6.2(:355-357)·houserules:143이 transient 90% 다룸 → 순 신규=**"합성 금지" 1문장**. ② min1 §5.1 = **`architecture-api:186`**(ninja 아님·확인)·"구체 경계값(매직넘버) 박지 마라(값 불문)" 이미 처리. ③ D2 종단 테스트 *의무화*는 acceptance-tester "명세 없는 행위 테스트 안 함" 스코프 충돌. ④ freeze는 §4.3.1:185가 이미 소급차단. ⑤ 미러 누락 0(houserules·ninja·architecture-api §5.1 이미 byte-id).

### 반증 3 (렌즈 B) — "백스톱 원리상 불가"가 틀림
- ⑮ `check-synthetic-infra-exc`: AST로 `infra_layer/acl`(또는 infra_layer)이 raw 인프라 예외(`OperationalError`/`DatabaseError`/`IntegrityError`)를 **`from` 없이**(`raise.cause is None`=`__cause__` 미보존=합성) raise → exit2. **`from` 조건이 방어가능 대안(실 드라이버 예외 보존 재던지기)을 자동 면제.** 전 픽스처+코퍼스 거짓양성 후보 0(프로덕션 합성=ACL-EX2 maj1live:82 단 1곳·나머지 test double은 디렉터리 필터·class 정의는 raise 아님). ⑭(핸들러 입력)이 못 보는 정확한 사각(ACL 출력=같은 결함 반대 끝).
- 렌즈 B 부가: D2 종단 테스트는 ACL 합성 메시지 미핀 시 ACL-EX2 *못 잡음*(Claude 테스트가 `OperationalError("database is locked")` 직접 주입→green인데도 결함 존재) → 탐지 신뢰불가. D3 대안 B 단일정답 금지(불변=합성금지 하나, `__cause__` 보존·공유 마커·Result 허용).

### 수렴 (그대로 진행)
- **ninja §6.2 한 문장**(교정 축): ACL/앱이 낙관락·CAS 재시도를 *스스로 소진 판정*하면 인프라 예외 *합성* 금지(recognizer는 받은 드라이버 예외 전용) → 도메인 transient-마커 예외 타입으로 raise·핸들러 타입 매핑. houserules:143 무변경. 미러 byte-id.
- **min1**: architecture-api §5.1(:186) reviewer nit→important(값 불문·*선언 유무*만·매직넘버 함정 회피).
- **폐기**: provenance 축·"Codex 면역" 서사. **defer**: D2 종단 테스트 의무화(reviewer:36 Risky Write + §4.3.1 EP-3가 명세-선언 케이스 이미 커버).

### 분기 (사용자 결정) — ACL-EX2 집행 레버 강도
reviewer 갭이 *실재*(검증)하므로 생산자 쪽 집행 필요 여부·강도가 결정점:
- **A(조정자 권장)**: 텍스트 + **백스톱 ⑮**(정밀도 시제품 검증 통과 후 배선) + reviewer 마이크로 불릿. maj1 ⑭(반대축)과 대칭·픽스처가 기존 텍스트 *문자대로 따라* 발생(DR-35/DR-22 텍스트-only 재발 함정)·Lens B 정밀도 강함.
- **B**: 텍스트 + reviewer 마이크로 불릿(백스톱 N≥2 보류). 기존 보류 규율 유지·단 reviewer 비-게이트라 재발 위험(maj1이 ⑭ 만든 그 약점).
- **C**: 텍스트만(Lens C 최소). 생산자 집행 0·reviewer 갭 실재라 DR-35/DR-22 재발 위험 최대.

---

## 7. 구현 완료 (2026-06-07·옵션 A·미커밋)
사용자 결정 = **옵션 A**(텍스트 + 백스톱 ⑮ + reviewer 마이크로 불릿; min1 공통). 적대 3렌즈 MODIFY 전부 반영.

**구현 7편집(claude↔codex 미러)**:
1. **백스톱 ⑮ `check-synthetic-infra-exc.py`**(신규·게이트 14→15종): AST로 `infra_layer`가 raw 인프라 예외(`OperationalError`/`DatabaseError`/`IntegrityError`)를 **`from` 없이**(`raise.cause is None`=합성) 생성(Call)해 raise→exit2. `from` 보존·도메인 타입·변수 재던지기(Name)·test 필터·비-infra(저-recall)·git-touched는 면제. plugin.json **1.7.0**. 배선=commands/dddjango.md·codex SKILL.md(양 판·codex는 `scripts/` 경로).
2. **houserules:143 disambiguator**(Lens B: coder가 *이 규칙*을 문자대로 따라 합성 — fixture 주석 "도메인 예외로 위장 번역 금지" 인용=coin-flip 뿌리): "이 '위장 번역 금지'는 드라이버가 *실제로 던진* transient에 한정 — *계산된* 소진(드라이버 예외 부재)은 인프라 예외 합성 말고 도메인 transient-마커 타입으로 raise". 미러 byte-id.
3. **ninja §6.2 새 불릿**("계산된 transient는 합성이 아니라 도메인 타입으로"): recognizer는 실 드라이버 예외 전용·합성 사각→500 과소매핑·`from` 보존 허용·백스톱+reviewer 포인터. 미러 byte-id.
4. **reviewer 43(d) 합성절**: ACL 계산 소진 인프라 예외 합성(`from` 없이)=important·⑮ 저-recall(헬퍼·변수 우회) 보조·(i)완전성/(ii)과잉/(iii)합성 **배타 3진단**(이중계상 금지). 미러 byte-id.
5. **reviewer min1**: 외부 식별자 수치 입력 상한 미선언=important·"값 불문·선언 유무만"(매직넘버 함정 §5.1 복제·백스톱 비대상). 미러 byte-id.

**적대 반영(MODIFY 전부)**:
- **provenance 축 폐기**(렌즈 A·grep 확인) → "받아서 recognize(외부 신호)/만들어서 raise(도메인 타입)". **"Codex 구조적 면역" 서사 폐기**(Codex도 catalog `decrement_product_stock_command.py`에 메시지 recognizer — 위치만 상류; 차이는 도메인 *타입* raise). 정당화 서사 = "P4③ 빈칸 비결정 봉인"(≠Codex 증거).
- **백스톱 NO→GO**(렌즈 B 반증): "원리상 불가"는 틀림. ⑮ 정밀도 시제품 통과(known-bad 3종[Op/Db/Integrity 합성] 차단·known-good 8종[도메인타입·`from`보존·도메인+from·변수재던지기·bare·비-infra·테스트더블·presentation] FP0·실 픽스처 Claude:82 exit2/Codex exit0). memory "백스톱 N≥2"는 *발화율 불확실 의미변종* 한정·여기선 코드형태 결정적·국소적(P1a-v3·C4 N=1 라이브 백스톱 선례 일관).
- **houserules도 편집**(렌즈 B): 렌즈 C "§6.2만·houserules 무변경"은 coder가 houserules:143을 읽고 합성한 사실 미반영 → 뿌리 편집 필수. reviewer line 41은 ACL-EX2 미커버(조정자 검증: 핸들러만 봄·producer-side 사각) → 신규 (d) 합성절 정당(증식 아님).
- **D2 종단테스트 의무 = defer**(렌즈 B: 합성 메시지 미핀 시 green인데도 결함·못 잡음 / 렌즈 C: reviewer:36 Risky Write + §4.3.1 EP-3 이미 커버·acceptance-tester "명세 없는 행위 테스트 안 함" 스코프 충돌).
- **D3 대안B 단일정답 금지**: 불변=합성금지 하나·`from` 보존·공유 마커·Result 허용(⑮ `from`/Name 면제로 구현).

**검증(빌드타임)**: ⑮ 정밀도 11케이스 FP0·실 픽스처 dual(Claude exit2·Codex exit0)·`claude plugin validate` ✔·15 게이트 양 판 syntax OK·미러 byte-id 전수(houserules·ninja·reviewer×2·script·게이트 카운트)·빈/자기레포 FP0.

**🔴 미검증·정직**: 라이브 배선(DR-30식 dual `/dddjango`서 ⑮ *발화* + 텍스트 효과로 Claude *합성→도메인타입* 전환) 미검증 — maj1 ⑭의 DR-30 전 상태와 동형. **N=1**(ACL-EX2=Claude 단일 인스턴스·테마는 DR-44/45/EX2 3회). 커밋 미실행(사용자 "B가자"=구현 요청, 커밋 미요청). 캐시 1.7.0 신선화는 라이브 테스트 시.
