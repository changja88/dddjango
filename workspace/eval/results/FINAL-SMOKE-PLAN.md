# 최종 수동 스모크 — 태스크 + 축별 체크리스트 (rev2, 서브에이전트 2렌즈 리뷰 반영)

> 목적: **정적으로 커밋된 표준 전부가 라이브 `/dddjango` 런에서 실제로 발화하는지** 확인.
> 정직 경계: **N=1 sanity** — "표준이 이번 런에 작동한다"까지. ③ 결정성·codex vs claude 우열은 **N≥5 블라인드** 별도(이 스모크 범위 밖).
> rev2 변경: ① 단일 리치 태스크 → **2-태스크 분할(기본)** (BC 배치가 ③·⑥을 동시에 흔드는 간섭 제거) · ② **clean fixture**(ninja 사전설치 금지 — 교란·거짓PASS 차단) · ③ 축 2개 추가(§0 종류폴더·테스트 의미군) · ④ 인용 오기 수정(`§9.5/§9.6`) · ⑤ 축1·6 조건부 판정.
> **rev3(2026-05-30 재테스트)**: P1a·P1b·P2·P3 수정 후 라이브 재검증. ① **캐시 신선화 필수**(§3.1) ② fixture **Django 5.2.14·Python 3.12**(P2 발생조건=stock `transaction_mode` 경로 부여) ③ **축13 신설**(§9.6 Risky Write 블록 + 동시성 테스트 실현 = P3) ④ 깊이=**유기적 준수**(catch 층은 위반 없으면 미발화 — 저장 산출물 동적검증으로 갈음). **P→축: P1a=축4·P1b=축3·P2=축5·P3=축13.**

---

## 1. 태스크 — 2개로 분할 (기본안)

**왜 분할**: BC 배치 결정 하나가 축1(③ 이주)·축6(cross-context)을 *동시에* 흔든다 — architect가 주문을 catalog에 흡수(단일 BC)하면 ⑥이 아예 안 생기고 ③ 판정도 달라져 신호가 엉킨다(직전 codex-7 reserve-stock가 단일 컨텍스트로 끝나 ⑥ 미발화). 두 태스크로 나눠 간섭 제거.

### 태스크 A — 단일 컨텍스트 (BC 모호성 없음)
baseline: 평면 `catalog.Product(name, price, stock)` (clean sample 클론).
> **재고를 예약(reserve)하는 API. 재고가 부족하면 409, 충분하면 그만큼 차감(예약)한다. 대상은 기존 catalog의 Product.**

catalog가 예약 판정을 명백히 소유 → ③ 이주가 *불명확 없이* 기대됨. **커버: 축 1·2·3·4·5·7(리포 명명)·8·10·11·12·13.**

### 태스크 B — 명시적 cross-context
baseline: 동일 clean sample (catalog 평면).
> **주문 생성 API. 별도 주문(order) 개념으로, 요청 상품·수량의 주문을 만든다. 재고는 기존 catalog가 소유하며, 주문 생성 시 catalog의 재고를 차감한다(재고 부족 시 409).**

"주문은 catalog와 다른 책임 + catalog가 재고 소유"를 명시해 **2 컨텍스트 협력을 유도**. **커버(집중): 축 6(ACL 분리+통합 스타일)·축 7(ACL 포트 명명)·축 13(§9.6 블록+동시성 테스트). 부수 재확인: 1·2·8·10.**

> **단일 리치 태스크(B 한 개로 전부)** 는 대안으로만: 런 실패 시 축 분리 곤란 + ⑥/③ 간섭. 시간/비용이 빠듯하면 B 하나로 갈 수 있으나 그땐 축6 조건부 판정(§4) 필수.

## 2. 게이트 답 (★ 미강제 = 축을 실제로 테스트)
- **BC 배치**: 미강제("표준 판정-소유 원칙대로 결정"). ⚠️ A는 단일이라 무관, **B에서 architect가 단일 BC로 합치면 축6 N/A 처리 + design-spec에서 *왜*를 읽어 판정**(§4 축6 참조).
- **lens**: ddd + db + api.
- **API 스택/framework**: "표준 기본대로" — **plain 강제 금지**(④의 본질).
- **테스트 러너**: 제안대로. **G1·G2**: 리뷰 깨끗하면 승인.

## 3. 런타임 & fixture (교란 차단 — 최우선)
- **fixture는 CLEAN**: `~/Desktop/dddjango-smoke-sample` 클론, **requirements = `Django==5.2.*`만, venv에 ninja 미설치**. ⚠️ 기존 `~/Desktop/dddjango-codex-interactive`(ninja 사전설치됨)는 **그대로 재사용 금지** — 새로 clean 클론.
  - 이유: ninja 사전설치는 (a) Tier3 교란 재현(architect가 requirements만 보고 "설치 불가→plain") (b) **축3 거짓 PASS**(핀 누락이어도 venv에 있어 test green)를 만든다. → 설치는 **런 중에** 일어나게(coder가 requirements 추가 후 설치 / 인터랙티브는 사용자가 승인). **축3은 requirements.txt grep만으로 판정**(test-green을 핀 증거로 쓰지 말 것).
- **런타임**: Claude(릴리스 제품 — 축 전부) + **Codex 인터랙티브**(축9 인터랙티브 ④ + 교차). 인터랙티브 런 첫머리에 "venv에 깔린 패키지 확인하라" 힌트 **주지 말 것**(보강 표준이 스스로 Ninja로 가는지가 진짜 테스트).

### 3.1 재테스트 준비 상태 (2026-05-30 — 준비 완료)
- **캐시 신선화 ✔ (최우선·완료)**: Claude(`~/.claude/plugins/cache/changja88/dddjango/1.0.0/`)·Codex(`~/.codex/plugins/cache/dddjango-local/dddjango/1.0.0/`) 둘 다 레포 HEAD(`246ccfc`)와 **byte-identical**로 rsync(P2 백스톱 `scripts/check-mechanism-ownership.py` 포함). 직전엔 14커밋 stale였음. ⚠️ **라이브 런은 반드시 새 세션에서 시작** — 기존 세션은 메모리에 구 에이전트 텍스트를 들고 있음(또는 새로고침 후 `/reload-plugins`).
- **fixture 2개 ✔**: `~/Desktop/dddjango-smoke2-claudeA`(태스크A·Claude)·`~/Desktop/dddjango-smoke2-codexB`(태스크B·Codex). 각각 **Django 5.2.14·Python 3.12·ninja 미설치·PROMPT.md 제거**(옛 plain-Django 게이트답 누설 차단)·baseline git 커밋. `manage.py check`/migrate/seed 통과.
- **유기적 깊이 한계**: catch 층(design-review-db blocker·discipline-reviewer blocker·`check-mechanism-ownership.py`)은 *위반이 있어야* 발화한다. 런타임이 준수하면 미발화가 정상 — 이 스모크는 **준수(생산자) 측면**을 본다. catch 발화는 이미 저장 산출물 동적검증으로 확인.

---

## 4. 축별 체크리스트 (PASS / 위치 / 확인법 / 근거)

### 축 1 — ③ 판정-소유 구조 이주 [조건부 판정]
- **먼저 design-spec에서 "재고 차감/예약 판정의 소유자"를 읽는다.** 그에 따라:
  - 소유자=catalog → **catalog가 표준 트리로 이주**(판정이 `application/catalog/domain_layer/...` bare 애그리거트, `catalog/models.py`엔 판정 0)면 PASS. (태스크 A는 이 경로가 기대됨.)
  - 소유자=ordering, catalog는 단순 데이터 소스 → **catalog 평면 유지 + ACL/포트 통합**도 §3.2 (2)항상 **합법 PASS**(태스크 B에서 가능). 평면이라고 무조건 MISS 아님.
- **MISS**: 판정이 평면 ORM 모델에 직접 붙음(소유자인데 이주 안 함). t3 사례.
- **근거**: `architecture-ddd` §3.2 (final.md:630/632).

### 축 2 — ④ API 스택 수렴 + headless 보강
- **PASS**: design-spec "API 스택=Django Ninja" 1급 결정+왜. presentation이 `from ninja import NinjaAPI/Router`. plain 아님.
- **확인**: `grep -niE "API stack|스택|Ninja" .dddjango/*/design-spec.md`; `grep -rl "from ninja" application/`.
- **근거**: `design-architect` "API 스택" 불릿(+ DR-17 보강).

### 축 3 — ④f 설치 규칙 (requirements 핀) [test-green로 판정 금지]
- **PASS**: `requirements.txt`에 `django-ninja==<버전>` 정확 핀 추가(기존 Django 핀 스타일).
- **확인**: `cat requirements.txt` (django-ninja 핀 유무) — **오직 이것만**. clean fixture라 핀 없으면 import 에러로 드러남.
- **근거**: `implementation-django-ninja` §2.1.

### 축 4 — ninja operation 품질 [openapi 확인 필수]
- **PASS**: ① 모든 status를 `response=`에 선언(200/201·404·409·422) ② **오류는 operation에서 `raise`하고 problem+json 변환은 중앙 `@api.exception_handler`·헬퍼 한 곳** — operation 본문에서 `(status, schema)` 튜플·수제 `JsonResponse`/`HttpResponse` 반환 **✗**(⚠️ codex-7이 operation 본문 우회=FAIL; 중앙 핸들러의 problem+json 응답은 허용) ③ `summary`/`description`/`tags` ④ 명시 반환 타입(`Status[...]`/성공 schema) ⑤ 에러 본문 **RFC 9457 problem+json**(`type`/`title`/`status`/`detail`).
- **확인(필수)**: 서버 띄워 `/api/.../openapi.json`에 **404·409가 노출되는지**; **operation 함수 본문**에 수제 응답·튜플 반환 grep=0(중앙 `@api.exception_handler`·헬퍼는 제외). 생성 OpenAPI의 error media-type이 `application/json`인 건 §6.2 수용된 한계(`get_openapi_schema` 사후변형 grep=0).
- **근거**: `implementation-django-ninja` §2.2·§6.2(RFC 9457).

### 축 5 — 코더 메커니즘-대체 가드레일 [grep 1차]
- **PASS(1차, 자동)**: `select_for_update`(운영용) + `CheckConstraint(stock>=0)` 백스톱 + version/CAS 조건부 UPDATE 존재. **커스텀 `BEGIN IMMEDIATE`/자작 DB 백엔드 grep=0**. SQL `WHERE`에 `stock>=qty` 비즈니스 판정 복제 없음.
- **보조(정성)**: 세션 로그상 코더가 메커니즘 자작 토끼굴에 빠졌다 되돌렸는지(있으면 가드레일이 *사후*만 작동 신호) — 보조 관찰일 뿐.
- **근거**: `coder.md` + `implementation-django §16.4` + **`architecture-db §9.5`(재시도 §9.6)**.

### 축 6 — ACL 분리 + 통합 스타일 [태스크 B / 조건부]
- **PASS(B에서 cross-context 생성 시)**: `ordering`이 `catalog`를 직접 import 안 함(`from application.catalog.domain_layer/infra_layer ...` grep=0). 통합이 `domain_layer/<agg>/port/` + `infra_layer/acl/`로 분리(`repository/`에 안 섞임). design-spec에 **통합 스타일 결정 기록**(재고 차감=즉시 일관성→동기 OHS/ACL, 비동기 이벤트 아님). **음성**: 통합 없는 앱엔 `port/`·`acl/` 미생성.
- **조건부 N/A**: architect가 단일 BC로 합치면 cross-context 미발생 → **MISS 아닌 N/A**로 기록하되, design-spec에서 *단일 BC 사유*를 읽어 **§3.2 (2) 데이터소스 논리(정상) vs 규칙4 오용(→ 진짜 표준 결함 신호)** 구분.
- **확인**: `grep -rn "from application.catalog" application/ordering/`; `ls application/*/domain_layer/*/port application/*/infra_layer/acl`.
- **근거**: `architecture-ddd` 규칙4·§2.5·§6.8 / `discipline-houserules` final.md §2 / `design-architect`(통합 스타일 기록).

### 축 7 — §4 명명 [리포=모든 태스크, ACL포트=B]
- **PASS**: 추상=개념 bare+역할 접미사(`OrderRepository`·`...Port`), 구현=기술 한정자 접두+동일 base(`DjangoOrderRepository`), `Interface`/`Impl` 없음, 파일명 풀네임(약어 ✗). ACL 포트 명명은 태스크 B에서.
- **근거**: `discipline-houserules` §4 / `design-architect`.

### 축 8 — B1 도메인 소유 (회귀 확인)
- **PASS**: 차감/예약 판정이 도메인 메서드에 있고 프로덕션 호출(테스트 전용 죽은코드 ✗). repo/infra는 version CAS 경합 가드만(SQL `WHERE`에 비즈니스 판정 복제 ✗).
- **근거**: `architecture-ddd` §3.2(final.md:630). (Tier 1·2·3 검증됨 — 회귀 확인.)

### 축 9 — 인터랙티브 ④ 확인사살 [Codex 인터랙티브 한정, 선택]
- **PASS**: 인터랙티브 Codex 런에서도 ④가 Ninja+requirements 핀으로 수렴. clean fixture(ninja 미설치)에서 사용자가 설치 자유 행사.
- **근거**: DR-17(헤드리스 통과, 인터랙티브 N+1). [[dddjango-stdgap-3-4]]. (필수 아님 — headless가 더 어려운 관문.)

### 축 10 — 동작 (모든 런타임)
- **PASS**: `manage.py check` clean → `makemigrations`/`migrate` OK → `test` green. **oversell 0**(동시 차감이 음수 재고/lost update 없음), 부족 409·없는 상품 404·잘못된 요청 422.

### 축 11 — §0 구조 불변식 (종류 2차 폴더 전체 생성) [신규 — 필수]
- **PASS**: `application/<app>/` + 4계층 `_layer`. `domain_layer/<agg>/` 아래 `entity/`·`value_object/`·`repository/`·`port/`(통합 시)·`domain_service/`·`event/`·`specification/`이 **비어도 폴더(빈 패키지)로 존재** — `repository.py`처럼 평면 파일로 접히지 않음. Django 앱은 `infra_layer/django_<app>/`(앱 루트 `models.py` 없음).
- **확인**: `find application/<app>/domain_layer -type d`; `find application -name 'models.py' -not -path '*/django_*'`=0.
- **근거**: `discipline-houserules` final.md §0 불변식·라인 115 / `discipline-reviewer.md`.

### 축 12 — 테스트 의미군 분리 [신규 — 필수]
- **PASS**: 테스트가 `application/<app>/test/{unit,integration,e2e}/` 의미군 배치(도메인·응용 단위=unit, DB·repo·HTTP=integration). `test_*.py` 평면 나열·엔드포인트별 평면 배치 ✗.
- **확인**: `find application/*/test -type d`; HTTP 계약 테스트가 `integration/`인지.
- **근거**: `discipline-houserules` §2 / `implementation-test` §4.2 / `discipline-reviewer.md`.

### 축 13 — §9.6 Risky Write 블록 + 동시성 테스트 실현 [P3 / 재고·주문 모든 태스크]
- **PASS(설계·생산자측)**: design-spec에 **§9.6 Risky Write Consistency Block 8행**(Transaction owner·Locking strategy·Rule ownership·Idempotency storage·API handoff·Side-effect timing·Isolation/retry·**Test criteria**)이 표 또는 행 단위로 존재하고, 각 행에 결정 내용 또는 근거 있는 '미적용'이 적혔는가. §9.6을 *번호로 인용만* 하고 8행 미기재면 MISS(= codexB 원래 실패 형태).
- **PASS(테스트 실현)**: Test criteria(동시 요청·oversell)가 **실제 테스트로 실현**됐는가 — 결정적 CAS-충돌 스파이(`implementation-test §20.5`: stale-`version` 1회 주입→재시도 수렴, 실 스레드·커스텀 백엔드 없이) 또는 동시요청 행위 테스트(§20.4), 또는 동등하게 경합을 행사하는 결정적/통합 테스트 중 하나의 형태. 구조 가드(version CAS·`stock>=0` CHECK·`select_for_update`)만 있고 oversell·경합 테스트 0이면 MISS(= codexB 원래 실패 형태).
- **확인**: design-spec에서 8행 블록 육안/grep; `application/*/test/`에 동시성·재시도·oversell 테스트 파일 존재 + 그 테스트가 경합을 *실제로* 주입·행사하는지 본문 확인; `manage.py test`에서 해당 테스트 green.
- **유기적 한계**: 생산자/실현 측면(architect가 블록 emit·coder가 테스트 실현)을 본다. catch 층(design-review-db가 블록 누락 차단·discipline-reviewer가 선언-미실현 차단)은 *위반이 있어야* 발화 → 준수 시 미발화가 정상(catch는 저장 산출물 동적검증으로 이미 확인 — codexB recall 3/3).
- **근거**: `architecture-db §9.6` / `implementation-test §20.5·§20.4` / `design-architect`·`design-review-db`·`discipline-reviewer`(P3 4스테이지). [[dddjango-final-smoke-findings]].

### (흡수) 타입 어노테이션
- 프로덕션 함수·메서드 시그니처에 인자·반환 타입(`houserules §4`, mypy strict; 테스트 면제) — 축11 확인 시 함께 grep.

### (트리거 미충족 — 발화 안 함이 정상)
- Idempotency-Key(ninja §7)·도메인 이벤트: 이 태스크 게이트가 멱등성/결과적 일관성을 요구 안 함(즉시 일관성 경로) → **미발화가 정상**. 산출물에 없다고 결함 아님.

---

## 5. 커버리지 (태스크 × 축)
- **태스크 A**: 1·2·3·4·5·7(리포)·8·10·11·12·**13**
- **태스크 B**: 6·7(ACL포트)·**13** + 1·2·8·10 재확인
- **인터랙티브(Codex)**: 9 + A 또는 B 재현

## 6. 한계 (한 런이 못 보는 것 — 정직)
- **③ 결정성·codex vs claude 우열**: N≥5 별도(스모크 범위 밖).
- **축6은 architect BC 결정에 종속** — 단일 BC면 N/A(설계 사유로 정상/결함 구분).
- **축1은 판정 소유자에 따라 평면유지도 합법** — design-spec 먼저 읽고 판정.
- 일부 축(§4 명명 등)은 약하게만 칠 수 있음 — 산출물 직접 확인.

## 7. 릴리스 (별개)
스모크 통과 ≠ 릴리스. **재테스트 결과(2026-05-30 smoke2): P1b·P2·P3 라이브 집행 확정 · P1a Codex 재발 — 상세 채점·해석은 `REMAINING-ISSUES.md` "🧪 라이브 재테스트 결과".** eval 브랜치 `eval/codex-determinism-n2`의 main 머지/푸시(v1.0.1?)는 별도 결정.
