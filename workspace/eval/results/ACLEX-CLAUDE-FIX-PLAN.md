# aclex Claude 결함 해결 계획 v2 (적대 5렌즈 반영 — 구현 전)

> **범위**: aclex 채점지 + 적대검증으로 실재 확정된 7개 결함의 *표준(플러그인)* 처방 설계. fixture는 증거, 수정 대상은 표준, 라이브로 닫는다.
> **상태**: v3 — 적대 5렌즈(v1)+3렌즈×3+2렌즈+3렌즈(6단계) 반영. **✅ 1~4·6단계 완료 = 테마 A 전부 + 테마 B**(maj1·maj2·maj3·maj4·min1·min2 처방; min3 무처방): 미러 byte-id·`claude plugin validate`·**1·2·3 fixture 라이브 ALL PASS**(transient→503·영구장애/미식별→500·깨진본문→400 problem+json·비표준status 가드). 6단계 적대 3렌즈(fixture mutation 실측)가 **min3 무처방**(이미 경계-스파이 종단)·**B2 백스톱 NO-GO**(catalog 스파이 존재→무발화·동형 부적합)로 과처방 차단. **남음: 5단계(테마A+B 라이브 dual·사용자 /dddjango), 2026-06-07.**
> **방법론**: 예방(producer) + 백스톱(결정적) + reviewer(의미) → 적대 리뷰 → 라이브. 교훈: 텍스트만이면 회귀(DR-22)·백스톱 박혀야 산다(DR-23)·신호가 정당코드와 동형이면 백스톱 구조적 불가(DR-39).
> **정직 경계**: N=1. 무력 테스트 완전 탐지=mutation testing이라 플러그인 *보장* 불가.

## v1→v2 핵심 교정 (적대 리뷰 결과)
1. **catch-all은 maj2를 못 닫는다**(ninja MRO 실측). "1규칙 4결함 동시"는 *형식*만 참 — 올바른 status(503)는 여전히 분류 의존. A0 "의미 면역" 철회.
2. **테마 A 백스톱 보류**: ninja 기본 `Exception` 핸들러 존재 + `create_response` override 정당 대안 → "핸들러 존재" 체크는 빈껍데기 Goodhart or 정당코드 오탐(실측). 라이브+reviewer 1차(DR-39 선례).
3. **근본 = 텍스트 부재 아닌 발화 부재**: reviewer:40 완전성·architect:34 retryable·api:168 누락금지가 *이미 존재*하나 미발화. 진짜 빈틈 = **transient 인프라(락)를 "서버버그"로 오분류**해 스코프 밖으로 빼는 분류 경계.
4. **막다른 길 제거**: maj4 `stock>=0`은 필드 암묵 가드와 동치라 구별 테스트 불가 → 탈출구 필요. min3 skip은 표준적으로 옳음(flaky 회피) → 실DB 종단 강제 금지.
5. **ninja 기술 실측 확정**(안전): catch-all은 구체 핸들러 비-가로채기(MRO most-specific-first)·`@api.exception_handler(Exception)` 1.6.2 실존(`set_default_exception_handler`는 부재)·DEBUG 스택누출 실제 차단.

---

## 테마 A — 오류가 problem+json을 빠져나간다 (전수성)

### A0. 구조 (v1 "catch-all 만능" 철회)
결함은 **두 개의 다른 빈틈**이다 — 섞으면 안 된다:
- **형식 빈틈**(응답이 problem+json 아님) — maj1 500·maj2 400json·min1 500html·min2 latent.
- **의미 빈틈**(status가 틀림) — maj1의 락은 503 retryable이어야 하는데 500.

그리고 형식 안전망도 **두 부분**이다(서로 안 잡음 — ninja MRO 실측):
- **net-1**: presentation `@api.exception_handler(Exception)` → 500 problem+json **+ `logger.exception` 필수**. 미지 예외·DEBUG 스택누출 차단(실측). *구체 핸들러는 MRO상 먼저 매칭되어 안 가로채짐*.
- **net-2 (=maj2)**: ninja 내장 4xx(파싱실패 `HttpError`·`ValidationError`)의 CT를 problem+json으로. **스코프드** `create_response`/`get_content_type` override(≥400에서만 CT 설정 + 실제 RFC9457 body) **또는** 구체 `@api.exception_handler(HttpError)`. **전역 무조건 override 금지**(2xx까지 problem+json 오표기·body가 `{"detail"}`만 — 실측). net-1은 이걸 못 잡는다.

### A1. 근본 처방 = 분류 경계 한 줄 (텍스트 추가 최소화)
대부분 표준에 이미 있고 안 발화했으므로, **새 텍스트가 아니라 분류 규칙 1개**가 핵심:
> **transient 인프라 예외(`OperationalError` 락/deadlock·serialization failure)는 retryable(503 또는 409)이지 "서버버그 500"이 아니다.**
- **위치**: `discipline-reviewer.md:40`의 "서버버그성 예외(AssertionError/KeyError류)는 500 정당" carve-out을 개정 — transient 인프라를 그 carve-out에서 *제외*. + `design-architect.md:34`(이미 retryable 강제)에 transient 인프라를 실패모드 표 대상으로 명시. + houserules 포트앵커(DR-44 E)에 한 문장.
- **maj1 status 매핑 위치 결정 = presentation**(ACL 아님): 구체 `@api.exception_handler(OperationalError/DatabaseError)` → 503 retryable problem. *ACL은 §143대로 도메인 예외만 번역(인프라는 안 건드림) — SD-7 경계·§143 "구체 예외만·except Exception 금지" 유지*. (대안: ACL이 인프라를 *명명 구체 예외*로 포트선언해 번역 — §143 안엔 들지만 포트에 인프라 누수. presentation이 더 깨끗 → presentation 채택.)

### A2. 형식 안전망 레시피 (예방)
- `implementation-django-ninja §6.2`: net-1(catch-all+log) + net-2(스코프드 override **또는** HttpError 핸들러)를 **§6.2 대안 B의 자연 귀결**로 명시(신규 대비개념 발명 금지). SD-6 충돌 아님 한 줄(operation 본문 *삼킴* 금지 ≠ API 경계 최후방 변환; cleancode는 `except Exception: logger` 이미 "좋은 예").
- **✅ 2단계 반영 완료(2026-06-07·§6.2 적용·fixture 라이브 ALL PASS)**: (a) net-1 `@api.exception_handler(Exception)`(미식별→500 problem·`logger.exception`만) — DEBUG=True 라이브서 traceback 누수 0. (b) `OperationalError` 시그니처 분기(`locked`[table-lock 변종 포함]·`deadlock detected`·`could not serialize access` + `sqlstate`||`pgcode` 드라이버 폴백→retryable; disk I/O·malformed→500) — 클래스 통째 금지. (c) `IntegrityError` 명시 핸들러(형식 500; 동시성 경합의 retryable·409 *의미*는 도메인·ACL 1차 책임). + §6.1 503·`Retry-After`·`type=` 명시(렌즈1 M1 TypeError 차단). status 503/409는 명세 §5/G1 선택(임의확정 금지·렌즈3 MF-1). 라이브: lock/table-lock/serialization→503·disk/미식별/integrity→500·전부 problem+json.
  - **✅ 3단계 완료(maj2·2026-06-07)**: §6.2 `@api.exception_handler(HttpError)`(깨진본문·임의 HttpError→RFC9457 body·`HTTPStatus` ValueError 가드) + 대안 B body한계 명시 + §6.3 "대안B면 핸들러 불요" **거짓이분법 교정**(대안 B는 CT만, body는 핸들러) + `problem_response`→`problem` 정렬 + MRO에 HttpError. 라이브: 깨진본문→400 problem+json(type/title/status)·406·비표준499 가드 ALL PASS. 적대 3렌즈 표준교정: 처방의 §6.9 **dead-ref**→§6.2·`architecture-api` §6.3 앵커.
- (min2) 중앙 핸들러 **커버리지 완전성**: 도메인이 raise하는 예외 전수 ↔ 등록 핸들러 대조(InvalidOrderQuantity 흡수). net-1이 latent 안전망.
- (min1) **api §5.1 한 줄 권고**(외부 식별자 입력 도메인 상한; 필드 `PositiveIntegerField`면 2^31-1·DB bigint면 2^63-1 — 매직넘버 주의) + reviewer nit. **백스톱 비대상**(catch-all이 500-problem으로 덮음).

### A3. 백스톱 — **보류** (정직)
"catch-all/override 존재"는 정당 형식이 복수(`exception_handler(Exception)` OR `create_response` OR renderer override)이고, ninja 기본 `Exception` 핸들러로 거의 항진이며, 빈 껍데기 Goodhart에 취약(실측). **신호가 정당코드와 동형 → 백스톱 구조적 부적합(DR-38/39 선례)** → 라이브+reviewer 1차. **이게 테마 A의 약점(DR-22 회귀 위험)** — 그래서 A4 라이브를 강하게. N≥2 재발 시 백스톱 재검토.

### A4. reviewer + 라이브 검증 (집행 무게중심)
- reviewer: 기존 reviewer:40 완전성 렌즈 + 분류규칙(transient=retryable) + 핸들러 커버리지. design-review-api가 transient→503 점검.
- 라이브(강): 인프라 예외 주입 → **503 problem+json·스택 0** / 깨진 본문 → **400 problem+json + RFC9457 body(type·title·status)** / 거대정수 → 500 problem+json / **2xx는 problem+json 아님**(net-2 전역 오표기 회귀 가드).

### A5. 리스크 (개정)
- ✅ ninja 해상도 역효과 = 실측 반증(MRO, 안전). ✅ `exception_handler(Exception)` 실존.
- ⚠️ 전역 override 2xx 오표기 → **스코프드 강제**(라이브 가드).
- ⚠️ 테마 A 백스톱 보류 → DR-22 회귀 위험 잔존(라이브 보강).
- ⚠️ 분류규칙이 reviewer:40 "서버버그 carve-out"과 충돌 안 하게 정합(transient ≠ 서버버그).

---

## 테마 B — 테스트가 산출물을 증명 못 한다 (건전성)

### B0. 정직 (유지)
완전 탐지 = mutation testing, 플러그인 *보장* 불가(그레이더 FC-2가 최종 캐치). 단 *일부 구조적 변종*은 결정적으로 잡힌다.

### B1. 예방 (producer)
- **(maj3, PARTIAL)** CAS 안전성은 이미 대조군(`test_product_repository.py:59`)이 커버 — 결함 실체는 *§6.7 인수의 순차 no-op + 죽은 단언*. 처방: §6.7 인수가 동시성 기준을 *그 레벨서* 결정적 CAS 스파이로 실현(§9.6/§20.5 기존 텍스트 발화 강화) + **죽은(항진) 단언 금지**.
- **(maj4) 탈출구 명시**: 명명 제약이 필드 암묵 가드(`PositiveIntegerField`)와 **동치**면 그 *중복 자체가 발견*(제거 또는 "필드 백스톱 병행" 문서화) — 구별 테스트 강제 아님. **strictly stronger일 때만**(예 `quantity>=1` vs 필드 `>=0`) 구별 테스트 요구.
- **(min3)** write-conflict **경계-스파이 통합 테스트**(presentation 경계서 포트/`deduct_stock` mock→ 실 ninja 스택 → 409 problem+json+retryable) 필수. **실DB 종단 강제 금지**(sqlite 단일라이터 flaky·정당 skip 존중).

### B2. 백스톱 (제한적·후보)
- **`check-concurrency-test-realized.py` (후보)**: 명세가 동시성/risky-write 기준 선언 **AND** touched 코드에 동시성 행사 테스트(stale `version` 주입+재시도 호출 or 동시 디스패치)의 AST 골격 0개 → exit2. `check-anemic-sql-guard` 동형(양성 트리거=명세 선언). **scope 정직**: "어디에도 동시성 테스트 0"만 잡고, "인수 테스트가 vacuous"·죽은 단언은 못 잡음(reviewer+FC-2).
- **skip 백스톱**: 단독 추가 **신중**(Goodhart 역효과 — skip만 처벌하면 덜 정직한 vacuous non-skip으로 도망). 두더라도 "계약 테스트 skip인데 같은 모듈에 보상 결정적 테스트 0"일 때만 저강도 발화 + 역효과 docstring 명시. (recall은 함수명+reason+docstring 3중신호라 plan 우려보다 높음 — 실측.)
- maj4 오귀속·죽은 단언 결정적 탐지 **보류**(near-mutation).

### B3. reviewer + 라이브
- discipline-reviewer "테스트 비-vacuous·산출물 귀속"(산출물 제거 시 red 추론·죽은 단언·중요 skip 보상 여부). design-review-db §6.7/§9.6 실현. **한계: 의미적·DR-22 강등 위험 → 라이브+그레이더 FC-2 동반**.
- 라이브: §6.7 인수 결정적 스파이 존재·순차 no-op 아님 / 제약 테스트 산출물 제거 시 red / write-conflict 경계-스파이 통합 실행(skip 아님). **+ 그레이더 FC-2(mutation) 최종 캐치**.

---

## 미러 체크리스트 (신규 스크립트마다 4 동기화 지점)
① `dddjango/scripts/X.py` ② `codex-dddjango/skills/dddjango/scripts/X.py` ③ `dddjango/commands/dddjango.md` 열거블록(`N종`·항목번호) ④ `codex-dddjango/skills/dddjango/SKILL.md` 열거블록. 텍스트(스킬/에이전트) 편집은 plugin+codex 2미러 byte-identical. `claude plugin validate`.

## 순서·우선순위
1. ✅ **분류규칙**(reviewer:40 carve-out 개정 — transient=retryable) — **완료**(v3·plugin6+codex6·미러검증·validate, 2026-06-07). 적대 3렌즈 반영: 트리거 술어 OR확장+닫는괄호+carve-out 술어 정합교정, 정의를 'OperationalError 중 락/경합 시그니처만'으로 정밀화, reviewer 판별=매핑 존재여부, 토큰통일, architect 속격분리.
2. ✅ **net-1 + transient + IntegrityError 핸들러**(maj1 의미·형식) — **완료**(§6.2·§6.1, plugin5+codex5·미러·라이브 ALL PASS, 2026-06-07). 적대 3렌즈 실측 반영: `type=` 명시·시그니처 확장·명세 status선택·Retry-After·net-1 가드.
3. ✅ **net-2**(maj2 HttpError 핸들러→problem+json body) — **완료**(§6.2·§6.3, 라이브 깨진본문→400 problem+json·비표준status 가드, 2026-06-07). 적대 3렌즈: §6.9 dead-ref 교정·대안B body한계·HTTPStatus ValueError 가드·problem_response→problem 정렬.
4. ✅ **min2(베이스매핑 누락점검)·min1(§5.1 상한)** — 완료(텍스트 2미러·백스톱 없음·reviewer 무변경, 2026-06-07). 적대 2렌즈: 개별핸들러→베이스매핑 프레이밍·매직넘버 계약계층 금지·over-wiring 회피. 🔴 라이브 미검증(텍스트 처방→5단계서).
5. **라이브 검증**(테마 A — 백스톱 보류분을 라이브로 보강).
6. ✅ **테마 B**(maj3·maj4) — 완료(reviewer:36 봉합 + §16.1 The Liar 변종 producer + 산출물귀속 reviewer, plugin+codex 4곳, 2026-06-07). 적대 3렌즈(fixture mutation 실측): **min3 무처방**(이미 경계-스파이 종단·채점지 오독)·**B2 백스톱 NO-GO**(catalog 스파이→무발화·"행사 골격" 신호가 정당코드와 동형·테마A 보류 논리)·maj4 §9.5 충돌회피(CHECK 제거 아닌 테스트 귀속). 🔴 라이브 미검증(텍스트→5단계).
- 각 단계 구현 전 적대 리뷰 → 라이브 재검증.

## ✅ 설계 결정 확정 (2026-06-06 사용자 승인)
- **결정 1 — 테마 A 백스톱 = 보류.** 신호(catch-all/override 존재)가 정당코드(대안B)와 동형이라 백스톱 구조적 부적합(DR-38/39) → 라이브(A4)+reviewer로 집행, DR-22 회귀 위험은 A4 라이브 가드로 보강. *주의: 테마 B의 동시성-행사 백스톱(B2 후보)은 이것과 별개 — 진행 대상.*
- **결정 2 — maj1 status 매핑 = presentation.** `@api.exception_handler(OperationalError/DatabaseError)`→503 retryable problem. ACL은 §143대로 도메인 예외만 번역(SD-7 경계 유지·포트 인프라 누수 금지).
