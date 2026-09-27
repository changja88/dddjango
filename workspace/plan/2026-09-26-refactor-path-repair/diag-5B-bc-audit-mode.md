# 진단 5B — «BC 전체 점검 모드»의 규모·분담·산출 형식 (2026-09-27 · 읽기 전용)

## 결론 (5줄)

1. **규범 수**: 그래프 규범 3,508개 중 검사기 없이 에이전트 판정만 있는 규범은 2,698개다. 그중 코드를 읽어 판정할 수 있는 코드 대상 규범은 **약 1,100개**다(휴리스틱 분류 · 표본 정밀도 34/40). 담당은 discipline-reviewer 822 · design-review-api 146 · design-review-db 83 · design-review-ddd 72다. 다만 discipline-reviewer 몫 822개 중 **약 370개는 그 에이전트의 «경계» 절(기술 구현 정확성은 보지 않음)과 미적재 스킬 때문에 실제로 판정할 주체가 없다.**
2. **BC 규모**: spring_dream `main` 의 BC 23개는 제품 코드 749~23,073행, 테스트 890~43,269행이다. 가장 큰 파일은 5,860행 1개다. 실측 밀도는 행당 약 20토큰으로, 주어진 가정(10토큰)의 두 배다.
3. **1회 점검 가능 여부**: 200k 창 기준으로, 한 리뷰어가 BC 제품 코드 전량을 한 번에 읽을 수 있는 BC는 14/23이고, 제품+테스트를 한 번에 읽을 수 있는 BC는 7/23뿐이다. 그래서 기본형은 **렌즈 4개 병렬 + 규율 리뷰어를 제품/테스트로 나눈 5회**다. 제품 5,000행을 넘는 BC 9개는 층·폴더 단위로 나눠 7~21회가 된다. 전 BC 합계는 약 163회다(api 층이 없는 BC 9개를 생략하면 약 154회 · 1M 창이면 약 116회).
4. **표본(service_policy)**: 원시 항목 19건 → 채택 예상 13건(병합 후 12) · 규칙 문구로 제외 5건 · 규칙 문구가 없어 탈락 1건. 채택분 중 **동작 불변 정리 10건(77%)**, 별도 요청 3건(마이그레이션 1 · 동작 변경 1 · 타 BC 1)이다. 원시 항목 기준 오탐률은 약 30%이고, 검사기 결과와 겹치는 항목은 2건이다.
5. **권고 분담**: ddd = 도메인·판정 소유·컨텍스트 경계 · api = HTTP 계약 · db = 모델·인덱스·트랜잭션 · discipline = 클린코드·테스트·트리·타입으로 나눈다. 모드를 더하기 전에 기존 한정 조항을 풀어야 한다. 리뷰어 3명의 «구현 코드 열람 금지»(R-3368·R-3323·R-2614), 규율 리뷰어의 diff 한정(R-1058·R-0982·R-1059·R-3420), 함수형 Router 보존 허용(R-0674), 그리고 무소유 규범 약 370개의 이관 여부다. architect 에게는 cleancode 스킬이 없으므로 판정 입력에 규칙 원문을 붙여 준다.

**표기**: SP = `application/service_policy/` (spring_dream `main` = `495128e26` · 2026-09-27 02:31). 모든 현장 수치는 `git ls-tree`/`git show main:` 으로 셌다(작업 트리·검사기 실행 0). 그래프는 `ontology/**/*.ttl` 전체(golden 제외)를 rdflib 로 적재했다(트리플 48,730). Serena·Graphify 는 쓰지 않았다.

---

## 1. 의미 위반 규범 목록

### 1-1. 배선별 규범 수 (실측)

| 배선 | 규범 수 | 비고 |
|---|---:|---|
| 전체 규범(Obligation·Prohibition·Permission·Exception·Override) | 3,508 | deprecated 0 |
| 검사기만(`enforcedBy`만) | 299 | |
| 둘 다(에이전트+검사기) | 511 | 이 중 코드 대상 약 237(검사기가 형태를 잡고 에이전트가 의미 변종을 본다 — 예: R-0523) |
| **에이전트만(`delegatedTo`만)** | **2,698** | 위임 대상 1개 2,422 · 2개 261 · 3개 이상 15 |

### 1-2. 에이전트만 2,698 — 에이전트별 (실측 · 복수 위임은 에이전트마다 셈)

| 위임 대상 | 에이전트만 규범 | 그중 코드 대상(추정) |
|---|---:|---:|
| agent-discipline-reviewer | 1,510 | **822** |
| command-dddjango (Coordinator) | 778 | 5 |
| agent-design-review-api | 352 | **146** |
| agent-design-review-db | 155 | **83** |
| agent-design-review-ddd | 140 | **72** |
| agent-design-architect | 29 | 1 |
| agent-coder | 20 | 5 |
| agent-acceptance-tester | 8 | 0 |
| (중복 제거한 고유 규범) | 2,698 | **1,104** |

### 1-3. 문서 키별 (실측 · 코드 대상은 추정)

| 문서 키(SKILL.md + references/final.md 합) | 에이전트만 | 코드 대상 |
|---|---:|---:|
| implementation-django | 218 | 167 |
| discipline-cleancode | 205 | 156 |
| implementation-django-ninja | 191 | 120 |
| architecture-api | 170 | 112 |
| implementation-django-web | 153 | 110 |
| implementation-test | 213 | 109 |
| architecture-ddd | 127 | 76 |
| implementation-python | 96 | 75 |
| architecture-db | 101 | 61 |
| discipline-tdd | 174 | 32 |
| discipline-houserules | 84 | 27 |
| 에이전트 md 7개 | 647 | 59(대부분 discipline-reviewer §Phase 2 점검 항목) |
| 커맨드 md | 319 | 0 |

### 1-4. 코드 대상 분류 (추정)

**분류 방법(재현용)**: 규범이 등장하는 절(블록 `statesNorm` → 절 → 문서)마다 기본 분류를 두었다(예: `architecture-db §11 rollout` = 운영, `discipline-tdd §5.5 입장 심사` = 절차). 그다음 라벨에 절차 표지(입장·승인·명세·반송·diff·G0/G1/G2·게이트·후보·evidence·slot·검사기·스킬·정본 등)가 있으면 «파이프라인 절차»로 내렸다. 에이전트 md 중 점검 항목 절(discipline-reviewer s007, 리뷰어 3명의 «점검 항목» 절)은 코드 표지가 있고 절차 표지가 없을 때만 코드 대상으로 올렸다.
**정밀도**: 코드 대상 무작위 40건 중 34건이 실제로 기존 코드에서 판정 가능했다(85%). 누락은 «절차»로 내린 235건 표본의 약 17%, «설계 지식·메타» 279건 표본의 약 20%다. 이를 반영한 **실제 코드 대상은 약 950~1,150개**로 추정한다.

| 분류 | 코드 대상 수 | 대표 규범 (R-ID · 라벨) |
|---|---:|---|
| API 계약·컨트롤러 | 247 | R-0696 신규 표준 표면 = @api_controller 클래스 컨트롤러 · R-2850 URL 의 동사 행위 포함 금지 · R-1968 201 Created 의 Location 헤더 |
| 네이밍·클린코드 | 172 | R-1513 지식의 중복 금지 · R-1394 2곳 이상 파일이 공유하는 철자의 명명 상수 승격 · R-1375 불용어로 이름만 달리한 구분 금지 |
| 테스트 규율 | 169 | R-1826 외부 서비스·시간·난수 의존 금지 · R-1836 구현 세부 결합 없는 테스트 · R-2209 mock 도구는 `mocker` |
| DB·ORM·트랜잭션 | 146 | R-2386 복합 인덱스 컬럼 순서는 가장 많은 쿼리를 서비스하도록 · R-1221 루프 개별 save 대신 bulk · R-1286 update_fields |
| 서버렌더 web | 102 | R-2269 form_valid() 에 durable invariant 몰기 금지 · R-2973 템플릿은 presentation 분기 한정 |
| 도메인 모델 | 90 | R-0960 C형 빈혈(규칙 메서드 0·판정이 인프라에만)의 blocker · R-0962 판정·불변식 메서드의 평면 ORM 모델 부착 금지 · R-0959 판정의 인프라 복제 금지 |
| 파이썬·타입 | 79 | R-2775 밑줄 접두·접미 관례 · R-2715 레코드는 TypedDict · R-2998 제너레이터 send·throw 금지 |
| 레이어 책임·의존 | 50 | R-1460 framework entrypoint 박막 — 정책은 application·도메인에 위임 · R-1459 책임 분리 기준은 변경 이유 · R-1316 서비스 레이어 도입 기준 |
| 파일트리·분할 | 25 | R-3415 분할 공리 — 크기가 아니라 소관·응집 · R-3416 캐스케이드 ① 이동 · R-1196 한 문장 목적 서술 불가 시 앱 분리 |
| 보안·설정 | 24 | R-1298 raw() 의 파라미터화 · R-2325 `@csrf_exempt` 는 작은 경계 한정 |
| (비코드) 파이프라인 절차 | 1,247 | 입장 표·게이트·반송·보고 |
| (비코드) 설계 지식·메타 | 279 | «언제 쓰나»·선택 가이드·위임 |
| (비코드) 운영·도구·배포 | 68 | rollout·deprecation·버전 핀 |

- 코드 대상 1,104개의 규범 종류: 의무 774 · 금지 186 · **허용 73 · 예외 58 · 우선 13**. 허용·예외·우선 144개는 architect 가 «빼는 근거가 되는 규칙 문구»로 쓸 수 있다(§3 제외 5건이 모두 여기서 나왔다).

### 1-5. 사용자 예시 3개의 해당 규범

| 예시 | 해당 규범(실측) | 집행 | 현장 |
|---|---|---|---|
| 큰 파일 분할 | houserules §1 «동명 폴더 승격 캐스케이드»: R-3415 분할 공리(크기가 아니라 소관·응집 — 행 수는 감사 신호) · R-3416 ① 이동 · R-3417 ② 승격 · R-3418 ③ 유지(본업 비대는 한 파일) · R-3419 감사 주도 배정. 관련: cleancode §3.1 | 검사기 없음(에이전트만). 신호는 check-layer-skeleton 의 ⓓ(행위 칸 200행 초과 · R-3420). R-3420 은 **판정 의무를 diff 가 만들었거나 키운 파일로 한정**한다 → 점검 모드에서 풀어야 한다 | 200행 이상 제품 파일 107개 · 400행 이상 28개 · 최대 `fortune_house/…/run_visit_turn_use_case.py` 5,860행 |
| 함수형 API → 클래스 컨트롤러 | R-0696 신규 표준 표면 = 클래스 컨트롤러 · R-0698 touched 표면의 클래스 컨트롤러화 · R-0697 «함수형 Router operation 의 레거시 취급·기존 형태 보존» · **R-0674(허용) «기존 함수형 Router 의 확립 표면 보존»** | 에이전트만(discipline-reviewer) | `application/*/driving_layer/api` 에 `Router(` 0건, `@api_controller` 17파일(12 BC) → **현장은 이미 해소됨** |
| 흩어진 업무 규칙 | R-0523 «응용 서비스는 비즈니스 로직을 직접 구현하지 않고 도메인에 위임»(에이전트+검사기 ⓓ#194) · R-0959/R-0960/R-0961/R-0962 판정 소유·빈혈 · R-2879 domain_layer 애그리거트 판정 소유 · R-1513/R-1514 지식 중복 · R-1455 로직과 데이터의 동거 | 대부분 에이전트만. 검사기는 usecase-dto ⓓ#194 후보(«조건이 도메인 속성 깊이를 들여다본다»)만 낸다 | §3 표본 1~4번 |

- 두 번째 예시는 규범상 «위반»이 아니다. 기존 함수형은 «레거시»(R-0697)이고 보존이 허용돼 있다(R-0674). 리팩토링 커맨드에서 정리 대상으로 삼으려면, R-0674 가 기능 요청에만 적용된다는 문면이 필요하다.
- 첫 번째 예시도 크기만으로는 위반이 아니다(R-3415). ①/② 판정(소관·응집)이 나와야 위반이다.

### 1-6. 점검 모드를 넣으려면 풀어야 할 현행 한정 조항 (실측)

| 조항 | 현재 문면(라벨) | 점검 모드와의 충돌 |
|---|---|---|
| R-1058 | 대조 대상의 이번 diff(승인 스코프 산출물) 한정 | BC 전체를 읽을 수 없다 |
| R-0982 | 이번 diff 신규 변경 한정 관찰(기존 코드 존중) | 같음 |
| R-1059 | 범위 밖 legacy 잔존의 발견 불산입(빚 보고 채널) | 기존 코드 발견을 셀 수 없다 |
| R-3420 | 승격 감사 신호 — 판정 의무만 diff 한정 | 큰 파일 판정이 막힌다 |
| R-3121 · R-3119 · R-3137 | 기존 줄 전파 금지 · 스코프 밖 이동·수정 금지 | «발견»은 해당 없음. «정리»는 G0 ⓐ 경로로 연결해야 한다 |
| R-3368 · R-3323 · R-2614 | 리뷰어 3명(ddd·db·api)의 «명세 한정 열람 — 구현 코드 열람 금지(편향 방지)» | 코드를 읽을 수 없다 |
| 리뷰어 3명 «산출» 절 | 근거 = «명세의 해당 절 제목이나 인용 문구» | 점검 모드는 `파일:행` 이 필요하다(discipline-reviewer 는 이미 `파일:라인`) |
| discipline-reviewer «경계» 절(R-1137 · R-1140) | 기술 특화 구현 정확성(Django/Python/ORM 관용구)은 비관찰 | 아래 무소유 문제 |
| R-0674 | 기존 함수형 Router 보존 허용 | 예시 2 |

**무소유 규범 (추정)**: discipline-reviewer 에 위임된 코드 대상 822개 중 458개는 그 에이전트가 적재하지 않는 스킬에서 온다. 적재 스킬은 cleancode·tdd·implementation-test·houserules 뿐이다. 출처별로는 implementation-django 167 · django-web 109 · ninja 85 · python 74 · architecture-ddd 22 · architecture-db 1이다. 이 가운데 «경계» 절이 명시적으로 제외하는 기술 정확성 규범은 **약 370개**다(Django ORM·보안 약 117 · ninja 80 · web 102 · python 73). 기능 요청에서는 diff 가 작아 드러나지 않았지만, BC 전체 점검에서는 이 규범들을 아무도 보지 않게 된다.

---

## 2. 현장 규모 (spring_dream `main`)

### 2-1. BC별 크기 (실측 · 제품 = test/·migrations/ 제외 · 테스트 = `test/` 폴더 전부 + `test_*.py`·`conftest.py`)

| BC | 제품 .py | 제품 LOC | 마이그 LOC | 테스트 파일(`test_*`) | 테스트 LOC | ≥200행 | 최대 파일 | 제품 토큰(×10) | 제품 토큰(×20 실측) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fortune_house | 670 | 23,073 | 507 | 99 | 43,269 | 10 | 5,860 | 231k | 461k |
| fortune_library | 522 | 16,556 | 699 | 44 | 12,393 | 14 | 1,937 | 166k | 331k |
| fortune_teller | 482 | 12,828 | 336 | 75 | 14,153 | 10 | 583 | 128k | 257k |
| chat_relay | 381 | 10,792 | 256 | 54 | 12,519 | 14 | 683 | 108k | 216k |
| accounts | 370 | 10,176 | 294 | 47 | 10,475 | 9 | 806 | 102k | 204k |
| fortune_content | 278 | 8,921 | 327 | 11 | 3,908 | 8 | 831 | 89k | 178k |
| fortune_calculation | 233 | 7,014 | 0 | 36 | 6,900 | 5 | 546 | 70k | 140k |
| fortune_reading | 180 | 5,540 | 0 | 27 | 8,867 | 8 | 656 | 55k | 111k |
| llm_access | 113 | 5,388 | 85 | 13 | 5,169 | 6 | 1,067 | 54k | 108k |
| decisive_fortune | 221 | 4,912 | 144 | 14 | 3,189 | 3 | 262 | 49k | 98k |
| fortune_catalog | 173 | 4,744 | 312 | 17 | 5,834 | 5 | 441 | 47k | 95k |
| **service_policy** | 240 | **4,639** | 131 | 24 | **4,374** | 1 | 245 | 46k | 93k |
| fortune_record | 216 | 4,439 | 152 | 33 | 4,903 | 3 | 336 | 44k | 89k |
| wallet | 170 | 3,810 | 192 | 9 | 2,078 | 3 | 357 | 38k | 76k |
| promotion | 160 | 3,491 | 146 | 26 | 4,186 | 2 | 309 | 35k | 70k |
| fortune_intent | 148 | 2,828 | 161 | 10 | 1,666 | 4 | 245 | 28k | 57k |
| rag_service_library | 147 | 2,720 | 0 | 10 | 1,083 | 2 | 370 | 27k | 54k |
| fortune_employee | 120 | 2,128 | 145 | 17 | 2,002 | 0 | 144 | 21k | 43k |
| media_library | 122 | 2,065 | 103 | 21 | 3,217 | 0 | 192 | 21k | 41k |
| product | 97 | 1,422 | 77 | 10 | 941 | 0 | 126 | 14k | 28k |
| text_library | 115 | 1,325 | 137 | 13 | 1,249 | 0 | 86 | 13k | 27k |
| query_translation | 103 | 1,315 | 128 | 7 | 1,478 | 0 | 169 | 13k | 26k |
| notification | 96 | 749 | 46 | 8 | 890 | 0 | 94 | 7k | 15k |
| **합계** | 5,357 | 140,875 | 4,378 | 625 | 154,743 | 107 | — | 1.4M | 2.8M |

- 제품 .py 에는 빈 골격 파일이 많다(BC당 36~248개 — houserules «골격은 내용과 무관»). 이 파일들은 읽을 분량에 거의 더하지 않는다.
- **토큰 밀도 실측**: SP application_layer 를 행 번호를 붙여 읽은 결과가 1,470행 = 29,856토큰, 곧 **행당 약 20토큰**이었다. 한국어 docstring 과 긴 절대 import 경로 때문이다. 아래 계산은 20을 쓴다.
- **리뷰어 고정 비용(추정)**: discipline-reviewer md 55.8KB 와 적재 SKILL 4개 48.7KB 로 약 30~40k토큰이다. references(cleancode 106KB · test 108KB · tdd 57KB)는 필요할 때 읽고, 절 몇 개만 읽어도 10~30k토큰이다. 200k 창에서 코드에 쓸 수 있는 몫은 **약 100k토큰 = 약 5,000행**이다.

### 2-2. 리뷰어 1회로 BC 하나를 전량 읽을 수 있나 (추정)

| 조건(200k 창 · 코드 5,000행) | BC 수 |
|---|---:|
| 제품 전량 ≤ 5,000행(규율 리뷰어 1회로 제품 전량) | 14 / 23 |
| 제품+테스트 ≤ 5,000행(한 번에 전부) | 7 / 23 |
| 1M 창(약 40,000행) — 제품 전량 1회 | 23 / 23 |
| 1M 창 — 테스트 전량 1회 | 22 / 23(fortune_house 테스트 43,269행만 2회) |

### 2-3. 나누는 방법

렌즈별로 읽는 범위가 다르다. 렌즈 리뷰어는 자기 층만 읽는다.

| 렌즈 | 읽는 층 | SP 행수 | 최대 BC 행수 |
|---|---|---:|---:|
| ddd | domain_layer + application_layer + open_host_service + published_event | 2,821 | fortune_house 17,313 |
| api | driving_layer/api + composition_root(registrar) | 373 | chat_relay 2,661(driving_layer/api 가 0인 BC 9개는 생략) |
| db | driven models + migrations + driven adapter(repository·uow) | 845 | fortune_house 5,829 |
| 규율(제품) | 제품 전량(층 단위로 분할: domain+application / driven+driving+composition) | 4,639 | fortune_house 23,073 |
| 규율(테스트) | test/ (unit / integration / e2e 로 분할) | 4,374 | fortune_house 43,269 |

- **분할 규칙 제안**: 5,000행을 넘는 렌즈 범위는 먼저 층으로, 다음 애그리거트·기능 폴더(`application_layer/<기능>/`)로 나눈다. 5,000행을 넘는 단일 파일은 그 파일만 따로 한 번 읽는다(현재 1개 — `run_visit_turn_use_case.py` 5,860행 ≈ 117k토큰으로 200k 창에서 단독으로도 빠듯하다).
- **호출 수(200k · 5,000행 기준 · api 렌즈 항상 1회로 셈)**: 5회 13개 BC · 6회 1개 · 7회 3개 · 8회 1개 · 10회 3개 · 12회 1개(fortune_library) · 21회 1개(fortune_house)다. **합계 약 163회**이고, api 층이 없는 BC 9개를 생략하면 약 154회다. 1M 창이면 약 116회(fortune_house 만 6회)다.

---

## 3. 현장 표본 판정 — service_policy (모의 «BC 전체 점검 모드» 산출)

- 선택 이유: 중간 크기(제품 4,639 · 테스트 4,374)이고, 최근 플러그인으로 빌드됐다(레인 0830-1615 · 0918-2050).
- **이미 알려진 검사기 결과**(레인 0918-2050 `refactor-scope.md` · 2.18.3 · 27종): 결정적 빚은 #490 1건(`driven_layer/adapter/clock/system_clock_adapter.py`)과 #645/#647 `Any` 12건(admin `form/*.py`)이다. ⓓ 후보는 domain-model #259/#268/#301 14건 · usecase-dto #191/#194 2건 · port-adapter #485 1건 · public-surface 2건이다.
- 제품 전 파일과 테스트 일부(grep + 2개 파일 발췌)를 직접 읽었다. 경로는 SP 기준 상대 경로다.

### 3-1. 항목 표 (19건)

| # | 렌즈(리뷰어) | 분류 | 규칙 R-ID · 문구 | 파일:행 | 발견 요지 | 검사기 겹침 | architect 판정(예상) | 정리 성격 |
|---|---|---|---|---|---|---|---|---|
| 1 | 규율 | 흩어진 규칙·DRY | R-1513 «지식의 중복 금지» · R-1514 «중복 판정의 지식 기준» | `application_layer/usage_policy/check_action_admission/check_action_admission_use_case.py:82-95` · `…/get_remaining_uses/get_remaining_uses_use_case.py:76-89` · `…/consume_action/consume_action_use_case.py:94-97` · `…/get_my_usage_status/get_my_usage_status_use_case.py:109-112` | «선택된 규칙의 주기 키로 사용 기록을 찾는다»는 같은 지식이 4곳에 있다(`_find_usage` 2개는 본문이 같다) | 없음 | 채택 | 동작 불변 |
| 2 | 규율 | 흩어진 규칙·DRY | R-1513 | `check_action_admission_use_case.py:68-73` · `consume_action_use_case.py:84-89` · `get_remaining_uses_use_case.py:61-65` | 입장 판정 재료(행위 종류·정지·규칙 조회 → `select_limit_rule` → `GuestTimezone.resolve`)를 모으는 전문이 3곳에 있다 | 없음 | 채택 · **1번과 병합** | 동작 불변 |
| 3 | ddd + 규율 | 판정 소유 | R-0523 «응용 서비스는 비즈니스 로직을 직접 구현하지 않고 도메인에 위임» | `consume_action_use_case.py:90-93` | «규칙(또는 행위 종류)이 없으면 판정만 하고 기록하지 않는다»는 업무 규칙이 응용 층의 분기에 있다 | ⓓ#194 후보(usecase-dto 2건 중 하나일 수 있음 — 위치 미확인) | 채택(판정·조율 경계 해석 필요) | 동작 불변 |
| 4 | 규율 | DRY | R-1513 | `…/save_limit_rule/save_limit_rule_use_case.py:59-85` ↔ `…/check_limit_rule_override/check_limit_rule_override_use_case.py:38-45` | 원시값을 LimitRule 후보로 조립하는 같은 지식이 2곳에 있다(한쪽은 «거울») | 없음 | 채택 | 동작 불변 |
| 5 | 규율 | 매직 값 | R-1394 «2곳 이상 파일이 공유하는 철자의 명명 상수 승격» · R-1511 «지식의 단일·모호하지 않은 권위 표현» | `driven_layer/django_service_policy/admin/limit_rule/form/limit_rule_form.py:36` · `…/admin/suspension/form/suspension_form.py:27` (권위 = `driven_layer/adapter/clock/system_clock_adapter.py:18` `settings.TIME_ZONE`) | help 문구에 «Asia/Seoul»을 박아 두어, 운영자 시간대의 권위(settings)와 따로 논다 | 없음 | **판정 갈림**(R-1398 «사람 대상 서술 리터럴 허용»으로 뺄 수도 있다) | 동작 불변(표시 문자열 같음) |
| 6 | 규율 | DRY | R-1513 | `admin/limit_rule/panel.py:46-62,79-85` ↔ `admin/suspension/panel.py:50-64,80-86` | `_AccountColumn` 클래스와 `get_changelist_instance` 가 거의 복제돼 있다 | 없음 | 채택(공유 자리는 houserules §1 결정 순서로 정해야 한다) | 동작 불변 |
| 7 | ddd | 컨텍스트 경계 | R-0490 «BC 간 연결은 OHS 계약 타입 또는 wire value» · R-1063 «형태 밖 의미 변종 … 직독» | `admin/limit_rule/feature/account_existence.py:13-14` · `…/account_labels.py:18-26` · `admin/suspension/form/suspension_form.py:13` | accounts 가 소유한 사용자 테이블을 `get_user_model()` 로 직접 조회한다(주석상 의도적 — import 만 피함) | context-isolation 은 import 만 본다 → 사각 | 채택(판정 갈림 — auth 모델을 공유 커널로 볼 여지: R-0477/R-0478) | **별도 요청 — 타 BC**(accounts OHS 신설 필요) |
| 8 | db | 인덱스 | R-2386 «복합 인덱스 컬럼 순서는 가장 많은 쿼리를 서비스하도록» · R-3335 «인덱스의 쿼리 패턴 커버 … 누락 부재» | `driven_layer/adapter/persistence/repository/limit_rule_repository.py:32-35` vs `driven_layer/django_service_policy/models/limit_rule_model.py:35-37` | `list_for_account` 는 `account_id` 조건만 쓰는데 인덱스 선두 열은 `action_kind` 다 | 없음 | 채택(행 수가 작은 정책 표면이라 영향은 작다 — R-2391 벤치마크 전제) | **별도 요청 — 마이그레이션**(결정 8 «마이그레이션 무변 확인»에 걸림) |
| 9 | 규율(+ddd) | 값 객체 | R-3454 «도메인 개념 → dataclass·값 객체 · 딕셔너리 금지» · R-1479 «변치 않는 값의 값 객체 표현» | `domain_layer/action_kind/action_kind_repository.py:12` · `domain_layer/limit_rule/limit_rule_repository.py:13,21` · `domain_layer/suspension_reason/suspension_reason_repository.py:14` (호출 `check_action_admission_use_case.py:69,71`) | 도메인 저장소 계약이 VO `ActionKindCode` 가 있는데도 원시 `str` 코드를 받는다 | 없음 | 채택 | **별도 요청 — 동작 변경**(형식이 틀린 코드의 조회가 «action_kind_unavailable» 거부에서 `InvalidActionKindCode` 예외로 바뀐다) |
| 10 | 규율(파이썬) | 명명 | R-2775 «밑줄 접두·접미 관례 표 준수» | `…/get_my_usage_status/get_my_usage_status_result.py:10,19` ← `get_my_usage_status_use_case.py:11-12` | 비공개 표지(`_LimitStatus`·`_SuspensionStatus`)를 붙인 클래스를 다른 모듈에서 import 한다 | 확인 안 됨 | 채택 — **다만 implementation-python 규범이라 현행 discipline-reviewer 는 판정 주체가 아니다(§1-6)** | 동작 불변(결정 9 이름 치환) |
| 11 | 규율 | 명명 | (규칙 문구 특정 불가) | `driven_layer/adapter/clock/system_clock_adapter.py:11` | `SystemClockClockAdapter` 는 낱말이 겹친다 — 명명 규약(`<기술><Port>Adapter`)이 강제한 형태일 수 있다 | **결정적 빚 #490 과 같은 파일** | **탈락**(규칙 문구 없음) · 빚 채널로 | — |
| 12 | 규율(테스트) | 테스트 | R-1826 «R — 외부 서비스·시간·난수 의존 금지» | `test/integration/test_admin_changelist.py:111` | 시계를 고정하지 않고 `datetime.now(UTC)` 를 쓴다(상대 시각이라 불안정 위험은 낮다 — nit) | 없음 | 채택 | 동작 불변(테스트 정리 슬라이스) |
| 13 | 규율(테스트) | 테스트 | R-1836 «구현 세부 결합 없는 테스트 작성» · R-1839 «public 프로토콜만으로» | `test/integration/test_admin_changelist.py:142` | 필터를 `type(spec).__name__ == "ScopeListFilter"` 라는 클래스 이름 문자열로 찾는다 | 없음 | 채택 | 동작 불변(테스트 정리 슬라이스) |
| 14 | 규율 | DRY | R-1513 | `domain_layer/domain_service/rank_effective_suspension.py:12` ↔ `…/select_limit_rule.py:13` | `_EARLIEST_INSTANT`(None 시각의 정렬 하한)가 2곳에 정의돼 있다 | 없음 | 채택(nit) | 동작 불변 |
| 15 | 규율 | DRY | R-1513 ↔ **R-1395 «우연히 값이 같은 다른 지식의 통합 금지»** | `domain_layer/shared_value_object/action_kind_code.py:11` ↔ `…/suspension_reason_code.py:11` | 두 카탈로그 코드의 정규식이 같다 | 없음 | **제외**(R-1395 — 카탈로그 두 개의 형식은 우연히 같을 수 있다) | — |
| 16 | 규율 | 매직 값 | R-1394 ↔ **R-1391 «과승격 방지 — pass-through 면제와 열린 집합 멤버 한정»** | `…/seed_action_kind_catalog/seed_action_kind_catalog_use_case.py:23-26` ↔ `…/seed_common_limit_rule/seed_common_limit_rule_use_case.py:29-32` | 씨앗 코드 `small_talk`·`split_call` 이 2개 파일에 되풀이된다 | 없음 | **제외**(R-1391 — 행위 종류는 DB 카탈로그, 곧 열린 집합이다. 타 BC 는 wire value 로 소비한다 — R-0490) | — |
| 17 | api/규율 | DRY | R-1513 ↔ **R-0992 «controller 의 짧은 failure→prepared error→Status mapping 반복의 DRY 면책»** | `driving_layer/open_host_service/usage_policy/usage_policy_service.py:103-104,121-122,145-146,173-174` | `NaiveNowNotAllowed` 번역 `try/except` 가 4번 반복된다 | 없음 | **제외**(R-0992·R-0074 준용 — 단 OHS 가 «controller» 문면에 드는지는 판정 필요) | — |
| 18 | 규율 | DRY | R-1513 ↔ **R-1512 «DRY 의 범위 — 단순 코드 중복 금지가 아님»** | `application_layer/port/unit_of_work/*.py`(5 × 27행) · `driven_layer/adapter/persistence/unit_of_work/*.py`(5 × 42행) | UoW 포트와 어댑터 5쌍의 모양이 같다 | 없음 | **제외**(R-1512 + D50·#546 «한 트랜잭션 = 애그리거트 하나»가 분리를 요구한다) | — |
| 19 | ddd/규율 | 도메인 모델 | **R-0960 «C형 빈혈(도메인 규칙 메서드 0개·판정이 인프라에만 존재)»** | `domain_layer/suspension/suspension.py:18-48` · `domain_layer/suspension_reason/suspension_reason.py:10-16` | 루트에 규칙 메서드가 없다. 그러나 판정은 도메인 서비스(`rank_effective_suspension.py:15` · `judge_action_admission.py:44-46`)와 VO(`suspension_window.py:25`)에 있다 | ⓓ#301/#268(domain-model 후보 14건)과 인접 | **제외**(C형 요건 «판정이 인프라에만» 불충족) | — |

### 3-2. 표본에서 읽히는 것 (추정)

- **사용자 예시 해당 여부**: 이 BC 에서 예시 1(200행 초과 행위 칸 0 · 최대 245행은 composition_root 로 배선 제외)과 예시 2(이미 클래스 컨트롤러)는 0건이다. 예시 3(흩어진 규칙)이 1~4번, 5건 중 4건이다.
- **산출량**: 원시 19건(제품 1,000행당 4.1건) → 채택 13건(1,000행당 2.8건). 이 BC 는 최근에 플러그인으로 빌드돼 정돈된 편이다. 오래된 큰 BC(fortune_house 23k행)는 같은 밀도로 셈해도 채택 약 65건 이상이 된다(근거가 약한 외삽).
- **오탐 위험**: 원시 항목의 약 32%(제외 5 + 탈락 1 = 6/19)를 architect 가 걸러야 했다. 제외 5건은 모두 코퍼스에 있는 **허용·예외 규범 문구**(R-1395 · R-1391 · R-0992 · R-1512 · R-0960 의 요건)로 근거를 댈 수 있었다. 곧 «규칙 문구로만 뺀다» 원칙은 실행 가능하다.
- **중복 위험**:
  - 렌즈 사이 중복: 3번은 ddd(판정 소유)와 규율(R-0523) 양쪽이 낸다. 7번은 ddd(R-0490)와 규율(R-1063) 양쪽이 낸다.
  - 같은 렌즈 안 중복: 1·2번.
  - 검사기와의 중복: 3번(ⓓ#194)과 11번(#490)이다.
  - 따라서 architect 에게 «병합→ID»와 «검사기 겹침» 열이 꼭 있어야 한다.
- **판정 갈림**: 5·7번은 규칙 두 개가 반대 방향을 가리킨다. architect 가 한쪽 문구를 골라 적고, G0 에서 사용자가 볼 수 있게 해야 한다.

---

## 4. 리뷰어 분담안

### 4-1. 렌즈 → 리뷰어 (각 md «경계» 절 준수)

| 렌즈 | 리뷰어 | 맡는 분류 | 코드 대상 위임 규범(에이전트만) | «경계» 절 근거 | 모드를 더할 때 바뀌는 것 |
|---|---|---|---:|---|---|
| 도메인 | design-review-ddd | 도메인 모델 · 판정 소유(흩어진 규칙) · 컨텍스트 경계·ACL · 레이어(헥사고날·CQRS) | 72 | 계약은 api, 데이터는 db 몫 | 코드 열람 허용(R-3368) · 근거를 `파일:행` 으로 · «판정-소유 대조 표»를 명세가 아닌 코드 대상으로 |
| HTTP 계약 | design-review-api | API 계약·컨트롤러(상태 코드·URL·스키마·오류 프로필·멱등성) | 146 | 도메인은 ddd, 저장은 db 몫 | 코드 열람 허용(R-2614) · 12-slot 은 명세 전제라 «현행 코드 관찰»로 대체 · driving_layer/api 가 없는 BC 9개는 호출 생략 |
| 데이터 | design-review-db | DB·ORM·인덱스·제약·트랜잭션·마이그레이션 | 83 | 도메인은 ddd, 계약은 api 몫 | 코드 열람 허용(R-3323) · Risky Write 8행 블록은 명세 대상 → 코드의 실제 트랜잭션·락으로 판정 |
| 규율 | discipline-reviewer | 네이밍·클린코드 · 테스트 · 파일트리·분할(캐스케이드) · 파이썬·타입 · 보안 · SRP | 822(그중 약 370 무소유) | 기술 정확성 비관찰 · 스코프 확대 권고 금지 | diff 한정 해제(R-1058 · R-0982 · R-1059 · R-3420) · 발견 채널을 «빚 보고»에서 «점검 항목»으로 |

**무소유 약 370개 처리안** (사용자 결정 사항):
- (가) ninja 기술 규범 80개는 api 리뷰어, Django ORM·보안 약 117개는 db 리뷰어로 옮긴다. 점검 모드에서는 이들에게 implementation-django-ninja·implementation-django 를 적재한다. python 73개는 규율 리뷰어가 implementation-python 을 적재해 맡는다. web 102개는 application/<bc> 에 서버렌더 뷰가 거의 없고(admin 은 Django admin), 표현계층은 web/ 쪽이라 dddjango-web 몫으로 둔다.
- (나) 이 370개는 점검 범위 밖이라고 문면에 박는다.

표본 10번(R-2775)은 (가)가 아니면 판정 주체가 없다.

### 4-2. 병렬 호출 수 (추정 · 200k 창)

| BC 크기 | 해당 BC | 호출 | 구성 |
|---|---:|---:|---|
| 제품 ≤ 5,000행 | 14 | 5~6 (api 없는 BC 는 1 적음 · fortune_catalog 는 테스트 5,834행이라 6) | ddd 1 · api 1 · db 1 · 규율-제품 1 · 규율-테스트 1~2 |
| 5,000~13,000행 | 7 | 7~10 | ddd·규율을 층·기능 폴더로 2~3분할, 테스트는 unit/integration/e2e 로 분할 |
| fortune_library | 1 | 12 | ddd 3 · 규율-제품 4 · 규율-테스트 3 |
| fortune_house | 1 | 21 | ddd 4 · db 2 · 규율-제품 5(5,860행 파일 단독 1) · 규율-테스트 9 |

+ architect 판정 1회. 렌즈 리뷰어끼리는 서로의 노트를 보지 않는다(현행 독립성 유지).

### 4-3. 리뷰어 산출 (항목 표 열)

`ID | 렌즈 | 분류 | 규칙 R-ID | 규칙 문구(라벨 원문) | 파일:행(복수 허용) | 발견 요지(1~2문장) | 근거 코드 1줄 | 심각도(blocker/important/nit) | 검사기 겹침(없음 / ⓓ#N / 빚 #N) | 정리 성격 예상(불변-코드 / 불변-테스트 / 동작 변경 / 마이그레이션 / 타 BC) | 확신(상/중/하)`

- 규칙 문구가 없는 항목은 내지 않는다(표본 11번).
- 규칙 두 개가 반대 방향이면 두 문구를 모두 적는다(표본 5·7번).

### 4-4. architect 판정

- **입력**:
  - 렌즈별 항목 표(파일)
  - 27종 검사기 결과 — 결정적 빚 목록 + ⓓ 후보 목록(겹침 표시용)
  - 인용된 R-ID 의 규칙 원문 발췌(rulepack). architect 는 cleancode·implementation-* 스킬을 적재하지 않는다(현재 ddd·api·db·houserules·tdd 만).
- **출력 — 판정 표**: `ID | 판정(채택 / 병합→ID / 제외 / 탈락 / 사용자 판단) | 근거 R-ID·문구(제외·탈락이면 필수) | 정리 성격 확정 | 정리 묶음(슬라이스 후보 — 코드 정리와 테스트 정리 분리: 결정 8 한쪽 고정) | 비고`
- **추가 출력**: G0 배너 초안(아래).
- 판정만 하고 코드는 쓰지 않는다. 현행 «리뷰 반영·충돌 중재» 절과 같은 권한 범위다.

### 4-5. G0 배너 요약 (표본으로 만든 모의)

```
BC 점검 — service_policy (제품 4,639행 · 테스트 4,374행 · 리뷰어 5회 + architect 1회)
발견 19 → 채택 13 (병합 후 12 묶음) · 제외 5 · 탈락 1
정리 성격: 동작 불변 10 (코드 8 · 테스트 2) · 별도 요청 3 (마이그레이션 1 · 동작 변경 1 · 타 BC 1)
규칙별: R-1513 지식 중복 5 · R-0523 · R-1394 · R-0490 · R-2386 · R-3454 · R-2775 · R-1826 · R-1836 각 1
파일별(상위): check_action_admission_use_case.py 3 · consume_action_use_case.py 3 · get_remaining_uses_use_case.py 2 · get_my_usage_status_use_case.py 2 · test_admin_changelist.py 2
제외 사유: R-1395 · R-1391 · R-0992 · R-1512 · R-0960(요건 불충족) 각 1 — 목록은 판정 표 §제외
사용자 판단 필요(규칙 충돌): 5번(R-1394 ↔ R-1398) · 7번(R-0490 ↔ R-0477/0478)
검사기 겹침: 결정적 빚 1(#490 — 빚 질문으로) · ⓓ 후보 1(#194)
```

---

## 5. 동작 불변으로 정리할 수 있는 비율 (표본 · 추정)

| 구분 | 건수 | 표본 # |
|---|---:|---|
| 채택 예상 | 13 | 1~10, 12~14 |
| └ 동작 불변 — 제품 코드 정리 슬라이스 | 8 | 1·2(병합) · 3 · 4 · 5 · 6 · 10 · 14 |
| └ 동작 불변 — 테스트 정리 슬라이스(제품 코드 고정) | 2 | 12 · 13 |
| └ 별도 요청 — 마이그레이션 필요 | 1 | 8 |
| └ 별도 요청 — 외부 관찰 동작 변경 | 1 | 9 |
| └ 별도 요청 — 타 BC 변경 필요(동작은 불변) | 1 | 7 |
| **동작 불변 비율** | **10 / 13 ≈ 77%** | |

- 불변 10건은 모두 추출·이동·이름 치환·상수 승격이라 결정 9(이름 치환 허용)와 결정 8(테스트 고정 확인) 안에 든다. 단 3번(판정을 도메인으로 옮김)은 테스트가 «기록하지 않음»을 외부 관찰로 덮는지 확인해야 한다(결정 8의 전제 2).
- 별도 요청 3건의 유형: 스키마 변경(8), 실패 경로 변경(9), 경계 밖 쓰기(7). 이 셋은 «동작 불변 창 밖»의 대표 유형이다. G0 에서 «정리(ⓐ)»와 «별도 요청 안내»를 처음부터 나눠 보여야 한다.
- 표본 하나(정돈된 BC)에서 나온 비율이다. 오래된 BC 에서는 스키마·계약에 걸친 항목 비중이 더 클 수 있다(검증 안 됨).

---

## 6. 실측 대 추정

- **실측**:
  - 그래프 집계 전부(§1-1·1-2·1-3의 «에이전트만» 열 · 규범 종류 분포 · 조항 라벨)
  - 현장 파일 수·LOC·최대 파일·`Router(`/`@api_controller` 개수
  - SP 전 제품 파일의 `파일:행`
  - 0918-2050 RS 의 검사기 결과
  - 토큰 밀도 1회(1,470행 = 29,856토큰)
- **추정**:
  - 코드 대상 분류(휴리스틱 + 표본 40건 정밀도)
  - 무소유 약 370(경계 절 해석)
  - 리뷰어 고정 비용·창 예산(5,000행)·호출 수
  - 표본 19건의 architect 판정(내가 architect 역할을 가정해 판정)
  - 오래된 BC 로의 외삽
- **확인하지 않은 것**:
  - ⓓ#194 후보 2건의 정확한 위치(RS 에 행 번호 없음)
  - 10번 항목에 대한 check-naming 의 커버 여부
  - 테스트 전량 판정(grep + 2개 파일 발췌만)
  - 서브에이전트의 실제 창 크기(200k/1M 둘 다 계산)
- **스크래치**(재현용): `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/diag5b/` — `census.py`·`classify.py`(분류 규칙) · `norms.json`·`classified.json` · `bcsize.py`·`layers.json` · `sp_*.txt`(SP 발췌).
