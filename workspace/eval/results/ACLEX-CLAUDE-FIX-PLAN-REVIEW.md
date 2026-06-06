# aclex Claude 결함 해결 계획 — 적대 5렌즈 리뷰 원문 (2026-06-06)

> 대상: `ACLEX-CLAUDE-FIX-PLAN.md` **v1 초안**(catch-all 중심)에 대한 5 독립 서브에이전트 적대 리뷰.
> **전원 판정 `FIX-THEN-GO`**. 이 리뷰 결론이 같은 파일 **v2**에 반영됨. 이 문서는 *구현 시 참고할 원본 근거*(file:line·실측) 보존용.
> 검증 환경: 표준 `dddjango/`(cwd) · fixture `~/Desktop/dddjango-aclex-claude`·사본 `/tmp/aclex-verify/*` · ninja 1.6.2 (fixture venv).

## 수렴 결론 (복수 렌즈 합의 = 고신뢰)
1. **catch-all은 maj2를 못 닫는다** (L5 실측, L3 보강): ninja `_lookup_exception_handler`(`main.py:641-646`)는 `type(exc).__mro__` most-specific-first → `exception_handler(Exception)`이 `HttpError(400)`을 못 가로챔. 깨진 본문은 `_default_http_error`(`errors.py:113`)→`{"detail":...}` `application/json`. A0 "1규칙 4결함 동시"는 *형식*만, 그것도 maj2 제외.
2. **catch-all=형식 면역, 의미(503 retryable)는 여전히 enumerate 의존** (L3): `OperationalError`(락)=retryable인데 catch-all이 잡으면 500. `architecture-api/references/final.md:168` "미매핑 500 누수 금지"를 catch-all이 형식만 problem+json으로 *영구화*. → 진짜 레버는 분류규칙+의미매핑이지 catch-all 아님.
3. **테마 A 백스톱은 Goodhart/거짓양성** (L1·L3·L5 합의): ninja가 이미 기본 `Exception` 핸들러 등록 + `create_response`/`get_content_type`/renderer override가 정당 대안(구체 핸들러 0개로 problem+json CT 달성, L5 실측 Strategy 1-3) → "핸들러 존재" 체크는 (a) 빈껍데기 통과 (b) 대안B 정당코드 오탐. DR-38/39 "신호가 정당코드와 동형이면 백스톱 구조적 불가" 선례. → 보류, 라이브+reviewer.
4. **근본 = 텍스트 부재 아닌 발화 부재** (L1·L4 합의): `discipline-reviewer.md:40`(완전성 important)·`design-architect.md:34`(retryable 503/409)·`architecture-api:168`(누락금지)·`architecture-db §9.6:408`(결정적 CAS 스파이)가 *이미 존재*. 진짜 빈틈 = reviewer:40 "서버버그성 예외(AssertionError/KeyError) 500 정당" carve-out이 **transient 인프라 락을 서버버그로 오분류**해 스코프 밖으로 뺌. → 핵심 변경 = 분류 경계 한 줄.
5. **maj1 위치가 ACL §143과 충돌** (L3·L4): `houserules:143` "ACL은 포트 선언 구체 예외만 명시번역, `except Exception` 아님". `ddd:359` ACL=타 BC 도메인 모델 번역기. `OperationalError`는 인프라 transient지 타 BC 도메인 예외 아님 → ACL에 넣으면 §143 모순·SD-7 흐림. 명시 결정 필요(presentation vs ACL 명명-구체).
6. **막다른 길 2개** (L2): maj4 `stock>=0`은 `PositiveIntegerField` 암묵 가드와 동치 → 구별 테스트 논리적 불가. min3 skip은 표준적으로 옳음(flaky 회피)·보상테스트 실재.
7. **ninja 실측 안전 확정** (L5·L2): catch-all 구체핸들러 비-가로채기·`@api.exception_handler(Exception)`(`main.py:601`) 실존(`set_default_exception_handler` 부재)·DEBUG 스택누출 실제 차단. → v1 리스크 #3은 기우.
8. **미러 부담 과소산정** (L4): 신규 스크립트는 codex 미러 + 배선블록 양쪽 = **4 동기화 지점**.

---

## 렌즈 1 — 회귀 저항·집행력 (FIX-THEN-GO)
**must-fix 1**: A2 백스톱에 발화 트리거 없음. 기존 presence-required 백스톱 3개 모두 조건부 트리거 — `check-layer-skeleton.py:19-30`(application/ 채택 AND 4계층 마커 AND touched), `check-test-config.py:22-34`(pytest 설정 도입 AND 바인딩 부재), `check-openapi-error-declaration.py:18-22`(`missing=extra-declared`). A2는 트리거 미명시 → 액면 구현 시 plain-Django/server-render/brownfield서 거짓양성 폭발(거짓양성≈0 불변식 파괴) 또는 빈껍데기 Goodhart. 재설계: 4중 AND(application/ 채택 AND presentation_layer에 ninja import+NinjaAPI/router AND git-touched AND catch-all 신호[`exception_handler(Exception)` OR `create_response` override] 0개). 배선=`dddjango.md:86` "13종→14종" 동형.
**must-fix 2**: A1/A3가 DR-44 회귀 반복. 표준 전체에 `OperationalError`/`IntegrityError`/`DatabaseError` 문자열 0회. DR-44 prevention=`discipline-reviewer.md:41` "포트-선언 구체 예외 집합 누락만, `except Exception` 강요 아님" → 인프라 예외 구조적 스코프밖. `aclex-claude.md:22,82` "표준 자체 빈틈·C1/C2 라이브 미발화"(DR-22 패턴). 집행 무게중심을 catch-all 백스톱에 두되, 빈껍데기 Goodhart 차단 위해 "problem 헬퍼/`create_response`로 problem+json 반환 형태"까지 봐야.
**should-fix 3**: 테마 B에 *이미 있는* 더 강한 레버 안 씀. `discipline-reviewer.md:36` "Risky Write 동시성 기준 실현(TDD)" 이미 blocker인데 `aclex:47` D2 STRONG(동시성 기준 열거)에도 sequential — 명세선언+reviewer로도 못 막음(텍스트/reviewer 레버 한계 재확인). 더 강한 결정적 레버: **명세 Test-criteria ↔ 실제 테스트 AST 대조**(check-anemic-sql-guard 동형, 양성트리거=명세선언, 부재=행사테스트 0). maj3 순차 no-op 결정적 캐치.
**should-fix 4**: min3 skip-백스톱을 이름위장 아닌 "명세 선언 대조"로 트리거하면 위장 면역. maj3+min3을 하나의 "명세 선언↔행사 테스트(skip 아님)" 백스톱으로 통합.
**should-fix 5**: A5#2 SD-6 충돌 과장. `discipline-cleancode/final.md:1549-1572`(§12.2/12.3) `except Exception as e: logger.error` "좋은 예". SD-6은 operation 본문 얇게(`ninja:440,447`)이지 API 경계 핸들러 금지 아님.
**강점**: 백스톱 배선 정확(`dddjango.md:86` 13종 Bash·exit2 일괄반송, ⑭ 텍스트편집만). enumerate→default-deny 정확. 테마 B 능력경계 정직.

## 렌즈 2 — 거짓양성·막다른 길 (FIX-THEN-GO)
**must-fix 1**: maj4 규칙이 `stock>=0`서 논리적 불가능 테스트 요구(막다른 길). fixture 두 부류 실측 — `order_quantity_at_least_one`(`quantity>=1` on PositiveIntegerField, `quantity=0`이 구별점 → `CHECK constraint failed: val_ge_1`, 구별 테스트 가능) vs `catalog_product_stock_non_negative`(`stock>=0`, 필드 암묵 `>=0`과 완전동일 → 구별 불가). PositiveIntegerField가 sqlite서도 컬럼 CHECK emit(실측 `stock=-1`→CHECK). 탈출구: 명명제약이 필드와 **동치**면 중복 자체가 발견(제거/문서화), **strictly stronger일 때만** 구별 테스트 요구. 증거 `order_model.py:21`·`0004_..._non_negative.py:15`.
**must-fix 2**: min3 "종단 강제" + skip-백스톱이 정당 skip 오탐. `test_create_order_api.py:257` skip 사유("sqlite 단일라이터 flaky 불가→결정적 위임") 표준적 옳음. 보상 `test_deduct_stock_command.py:98 test_execute_raises_write_conflict_when_retries_exhausted(mocker)`(`spy.call_count==MAX_RETRIES`·DB 불변) 실재·결정적. 고침: (a) min3을 "**경계-스파이 통합**"(presentation 경계서 포트 mock→실 ninja→409+retryable)으로 한정, *실DB 종단* 아님. (b) skip-백스톱은 reason에 보상테스트 참조 없을 때만.
**should-fix 3**: `le=2^63-1` 구조적 임계값은 옳음(실측: PositiveIntegerField validator max=2^31-1, pk조회 2^63-1까지 무오류·>=2^63 OverflowError; Postgres bigint 동일). 단 필드 범위(2^31-1)와 어긋남·catch-all이 500-problem으로 흡수하므로 **비필수·백스톱 비대상**("선택적 polish, reviewer nit").
**should-fix 4**: SD-6 충돌 과장. `cleancode:1624` 대상은 *삼킴(swallow)*이지 재던짐/변환 아님. `ddd:1877,1891,1919` Saga/트랜잭션 스크립트 `except Exception` 합법 보유. catch-all=`§6.2:390-395` 대안B(`status>=400` 일괄 problem) 자연귀결. → 구별 문구 단순화.
**should-fix 5**: A5#1(버그 가림) — ninja 기본(`errors.py:125-133`)도 이미 500화(DEBUG=True서 text/plain traceback). override는 problem+json 500+로깅이라 순이득. **catch-all에 `logger.exception` 필수**(빠지면 silent-swallow).
**강점**: A5#3 ninja 해상도 실증 반증 — `_lookup_exception_handler`(`main.py:641-644`) MRO most-specific→least 첫매치. 라이브: `DomainErr`→409(구체 승)·`InfraErr`→500 problem+json(catch-all 승). default-deny 거짓양성 저항(구체 핸들러 공존). A2 자기한계·테마B 능력경계 정직.

## 렌즈 3 — 새 빈틈·Goodhart·범위 (FIX-THEN-GO)
**must-fix 1**: "전수성=형식만, 의미(올바른 status)는 enumerate 의존". `catalog_product_stock_adapter.py:44-51` OperationalError("database is locked")=retryable transient인데 catch-all→500(503 아님). `architecture-api:168` "미매핑 500 누수 금지"를 catch-all이 형식만 problem+json으로 영구화. A0 "면역"→"형식 면역, 의미는 인프라 매핑 완전성 의존"으로 격하. 우선순위 재고(catch-all 1순위 의심).
**must-fix 2**: A2 백스톱 Goodhart. ninja 기본 `Exception` 핸들러 이미 등록(context7). (a)빈껍데기 통과 (b)대안B(create_response)면 Exception 핸들러 0개여도 정상(`reviewer.md:40`)→거짓양성 딜레마. SD-6 백스톱이 `status:int` 놓친 것과 동형. → A2 취소 or 좁게 재정의 or 백스톱 부적합 선언(DR-39 "신호가 정당코드와 동형").
**must-fix 3**: 테마 A가 DR-44 §143과 새 텍스트 모순. `houserules:143` "`except Exception` 포괄 catch 아님, 구체예외 명시번역". `reviewer.md:40` 동일. A1(b) 인프라 transient *패밀리*=베이스 catch → §143 정면충돌. 미러 byte-id로 양립 시 coder 모순지시. §143 개정: 구체 도메인 + 명시 열거 인프라 transient 화이트리스트, 그외 catch-all 안전망 위임(3자 분담).
**should-fix 4**: 우선순위 — 진짜 레버는 ACL/핸들러 커버리지지 catch-all 아님. catch-all은 스택노출·text/html만 닫음(부수효과).
**should-fix 5**: skip-백스톱 저-recall(이름위장) + Goodhart 역효과(skip만 처벌→덜 정직한 vacuous non-skip으로 도망, FC-2가 잡을 걸 숨김). **추가 말 것** 진지 고려. 두면 "보상테스트 없을 때 경고" 저강도 + 역효과 docstring.
**should-fix 6**: maj3 과잉 가능. 대조군(`test_product_repository.py:59`·`test_deduct_stock_command.py:98`) CAS 안전성 이미 커버 → 실체는 인수 순차 no-op+죽은 단언. 죽은 단언 제거만으로 90%. B2 결정적 보류는 옳음.
**should-fix 7**: min1(catch-all이 500까지만, schema 가이드 과함→reviewer nit)·min2(#3에서 §143/핸들러 커버리지 정합하면 자동 흡수→독립 항목 삭제).
**should-fix 8**: A5#3 ninja 해상도 우려 불필요(이미 검증). risk에서 내리고 #2 Goodhart 근거로 전환.
**강점**: enumerate→default-deny 방향(`acl...:44-51` 3-예외 누수 실재). B0/B2 정직(mutation 보장불가, RUBRIC FC-2:72 그레이더 주입). 자기 리스크 열거. maj3 PARTIAL·min1 강등 정직.
**증거**: `acl catalog_product_stock_adapter.py:44-51`·`ninja final.md:336-409`(대안B 존재)·`houserules:143`·`reviewer.md:40`·`api:168`·`dddjango.md:86`·`test_product_repository.py:59`·`test_create_order_api.py:257`.

## 렌즈 4 — 표준 정합·미러 (FIX-THEN-GO)
**must-fix 1**: A1/A3 상당부분 이미 존재(중복). `discipline-reviewer.md:40` "API 오류 응답 중앙화 규율 + 완전성(미매핑 누수) important"(=maj1/min2). `design-architect.md:34` "재시도/CAS 실패 outcome retryable(503/409)"(=A1.b). `api:168` 누락금지. 진짜 결함=발화 부재. `aclex:8,19` 단일패스가 "비재시도 OperationalError 서버버그 carve-out" 합리화 + `reviewer.md:40` "프로그래밍 오류·서버버그성(AssertionError/KeyError) 500 정당"이 인프라 예외 스코프밖. **핵심 텍스트 변경 = 이 분류 경계 하나**(catch-all 신설 아니라).
**must-fix 2**: maj1 위치가 houserules §2 ACL 전수성과 충돌. `houserules:143` "포트 선언 우리쪽 예외 전수, `except Exception` 아님·구체 명시번역". `ddd:359` ACL=타 BC 도메인 모델/용어 번역기. OperationalError는 인프라 transient지 타 BC 도메인 예외 아님→ACL에 넣으면 SD-7 흐림. 명시 결정: (a) ACL 명명-구체(§143 안 들지만 포트에 인프라 누수) or (b) presentation(§6.2+reviewer carve-out서 transient 분리). 어느쪽이든 **제네릭 catch-all로 transient 일괄 금지**(retryable 신호가 500과 뭉개짐, `api:168` 충돌).
**must-fix 3**: 신규 백스톱 미러 4지점 — ①`dddjango/scripts/X.py` ②`codex-dddjango/skills/dddjango/scripts/X.py` ③`dddjango/commands/dddjango.md` 열거블록 ④`codex-dddjango/skills/dddjango/SKILL.md` 열거블록. (스크립트 자체 byte-id는 현실적 — 기존 13종 양쪽 동일.)
**should-fix 4**: catch-all=`§6.2:336,390-395` 대안B 앵커(신규 대비개념 발명 금지). *단 핵심차이*: 대안B는 ninja가 만든 4xx/5xx CT만 바꿈, app/도메인 raise된 미처리 `OperationalError`(ninja 4xx 안만듦)는 Django 500(text/html)로 전파 → `exception_handler(Exception)` *예외타입* catch-all은 진짜 신규(중복 아님, 이 점 plan 옳음). 중심레버는 분류규칙, catch-all은 "정체불명 500 problem화+로깅" 안전망.
**should-fix 5**: min1 위치=`architecture-api §5.1` 요청계약(`:182`), 422 의미 `§4.2:158`. ninja는 구현만(`architect:35`). `aclex:17` underdetermined·sqlite 강등 → §5.1 한 줄 권고로 충분, 백스톱·blocker는 YAGNI.
**should-fix 6**: 테마 B도 발화 부재 — `architecture-db §9.6:408`(결정적 CAS-스파이 의무)·`reviewer.md:38`(빈혈 C형)·`:50`(Risky Write 실현). 신규 텍스트보다 reviewer 발화 강화.
**강점**: maj1 표준-수준 빈틈 정확(`aclex:21`). check-error-boundary-completeness 상보(check-error-centralization은 application HTTP 누수만) 정확·비중복. 백스톱 한계 정직. reviewer 4종(architect·discipline-reviewer·review-api·review-db) plugin+codex 실재·미러됨.

## 렌즈 5 — ninja 기술타당성·테마 B 실현성 (FIX-THEN-GO)
**must-fix 1**: catch-all 단독으로 maj2 못 닫음. `main.py:641-646` MRO most-specific-first. HttpError(400)→`_default_http_error`(`errors.py:113`)→`{"detail":"broken body"}` status=400 ct=`application/json`. 공식문서: 기본 HttpError 핸들러는 `@api.exception_handler`로 따로 override. A0 "maj2 동시" 제거.
**must-fix 2**: A2 "둘 다 등록" 백스톱이 `create_response`/`get_content_type`/renderer override로 우회(실측 — 구체 HttpError 핸들러 0개로 problem+json CT 달성, Strategy 1-3). 근거 `_default_*`가 전부 `api.create_response`(`errors.py:110/116/122`)→`get_content_type`(`main.py:562·570`)→`renderer.media_type`. **단 전역 무조건 override는 자체 결함**(실측: 201 success→problem+json 오표기·body `['detail']`만 RFC9457 아님). 스코프드(≥400만+실제 problem body)가 정답이나 그것도 구체 핸들러 미등록→텍스트체크 우회. → A2를 핸들러 등록 형태로 두지 말것; maj2는 **라이브로**(깨진본문→CT problem+json AND body type/title/status). 생산자 예방에 두 합법경로(구체 HttpError 핸들러 OR 스코프드 create_response/renderer) 적시 + 전역 무조건 override 금지 reviewer 레드플래그.
**should-fix 3**: min3 백스톱 recall 과소평가 — 함수명+reason+docstring 3중신호(실측 `test_write_conflict_exhaustion_returns_409_retryable` + reason §6.8). 일반 위장 어려움.
**should-fix 4**: min3 본질=skip 아닌 shallow-mock 위임(`test_exception_handlers.py:91` command mock→StockReservationConflict 직접 raise, 핸들러→problem+json만 검증, CAS 재시도 루프 0행 적중 미구동). skip-백스톱은 위임처 계약 실구동 못봄.
**should-fix 5**: min1·maj4 A0 과대귀속 정밀화. min1 catch-all은 500까지만(422 깔끔은 schema 상한 의존). maj4 `product_model.py:15` PositiveIntegerField + 0004 중복 CheckConstraint → 제약 삭제해도 필드 가드가 IntegrityError → green 유지(정확히 maj4). 정적으로 "테스트 의도 vs 필드 암묵가드" 결정적 분리 불가(모델 docstring이 CHECK를 백스톱으로 정당화) → B0 결정적 보류 옳음.
**강점**: catch-all 구체핸들러 비-가로채기 실측(ValidationError/HttpError/DomainExc→CONCRETE, ValueError/OperationalError→CATCHALL). `@api.exception_handler(Exception)`(`main.py:601`)·`add_exception_handler`(`:595`) 실존, `set_default_exception_handler` 부재(1차선택만). catch-all DEBUG 스택누출 실제 차단(기본 `_default_exception` `errors.py:125` DEBUG=True traceback override). min3 skip AST 탐지 가능. 테마B mutation 비보장 정당.

---

## 구현 시 미해결 결정 2개 (v2 계획 말미와 동일)
1. **테마 A 백스톱 보류가 맞나** — 약하더라도 좁은 결정적 신호(L1: 명세선언↔행사테스트 / L1#1: 4중 AND 트리거)를 짤 가치 vs Goodhart 빌미(L3·L5).
2. **maj1 status 매핑 위치** — presentation(v2 채택) vs ACL 명명-구체(L4 must-fix 2 양자택일).
