# dddjango 플러그인 개정 판정 기록 (소유자 확정본)

> 2026-08-25 saju (b) 7건 판정 세션. 각 항목: 무엇을 / 왜 / 어떻게. 이 문서가 플러그인 수정 작업의 정본이다.
> 관련 조사 자료: plugin-revision-worklist.md (동일 디렉터리 — 런들의 원 보고·증거 경로).

## 판정 ① — #247 UnitOfWork 명명 규칙 완화 [검사기 수정]

**무엇을**: check-naming.py #247의 UnitOfWork 명명 규칙을 확장한다.
- 현행: 계약은 정확히 `<Bc>UnitOfWork`, 구현은 정확히 `Django<Bc>UnitOfWork`만 인정.
- 개정: `<Bc>[<역할>]UnitOfWork` / `Django<Bc>[<역할>]UnitOfWork` — **역할 수식어(CamelCase 1어절 이상)를 선택적으로 허용**한다. BC명 접두·UnitOfWork 접미는 계속 필수. 축약형(`Uow` 등)은 불허(소유자 결정 — 확립된 패턴명 가독성·기존 전 BC 표기 일관).

**왜**:
1. 구조적 필연 — 한 BC에 트랜잭션 소유자가 2개 이상 생기면(예: billing 결제 원장 vs event stream) BC당 고정 단일 이름은 충돌한다.
2. 정보 보존 — saju의 `SajuImportUnitOfWork`는 "legacy 이관 흐름 전용 트랜잭션 소유자"라는 승인 설계 의도(§5.2 exact)를 이름에 담는다. `SajuUnitOfWork`로 강제 rename하면 BC 전체 경계처럼 읽혀 오히려 부정확해진다.
3. #63 판정(에러는 최대한 자세한 하위 타입 선언)과 같은 원칙 축 — 더 구체적인 이름이 정보를 더 담으면 인정한다.

**어떻게**:
- check-naming.py L273-283 부근: `expected = _camel(bc.name) + "UnitOfWork"` 동등 비교를 → 정규식 `^{Bc}([A-Z][A-Za-z0-9]*)?UnitOfWork$`(구현은 `^Django` 접두 동일 패턴) 매칭으로 교체.
- 양성 fixture: `SajuUnitOfWork`(무수식) · `SajuImportUnitOfWork`(수식) 모두 통과.
- 음성 fixture: `ImportSajuUnitOfWork`(BC명 비접두) · `SajuImportUow`(축약) · `SajuUnitOfWorkImport`(접미 아님) 위반 유지.
- 판정 결과: saju 현행 이름 2건은 **적합** — 제품 수정 없음.

## 판정 ② — #245 UoW 메서드 집합: dunder 프로토콜로 통일 [검사기 수정 + saju 제품 수정]

**무엇을**: UoW 계약 메서드 집합의 canon을 `{__enter__, __exit__, after_commit}`(+`__init__`)로 확정하고, check-port-adapter-pairing.py의 3자 불일치를 정합한다. saju는 open/close 방식을 dunder/with 방식으로 재작업한다.

**왜**:
1. 언어 강제 안전성 — `with` 문은 정상·예외·조기 return 모든 경로에서 `__exit__`(커밋/롤백)를 보장한다. 수동 open/close+try/except/else는 경로 하나만 빠뜨려도 트랜잭션이 새는 구조적 위험이 있다.
2. 전 BC 일관 — daily·billing 등 기존 BC가 이미 `with uow:` 형태. 두 스타일 공존을 canon으로 인정하면 이원화가 영구화된다.
3. Python 표준 관례(context manager protocol).

**어떻게** (플러그인):
- check-port-adapter-pairing.py 3자 정합: L84 선언 집합(현행 유지 — 이미 dunder) = L371 실제 판정(open/close 위반 유지 — 단, 진단 사유를 명확히) = 진단 문구(«열기·닫기·after_commit» → «__enter__/__exit__/after_commit» 로 교정).
- fixture: exact-three 양성(`__enter__/__exit__/after_commit`) · missing-each/extra(open·close 등 임의 public 메서드) 음성.

**어떻게** (saju 제품 — 재작업 지시 예정):
- 포트 `SajuImportUnitOfWork`: `open()`→`__enter__()`, `close(exception)`→`__exit__(exc_type, exc, tb)`(False 반환=예외 재전파), after_commit 유지.
- 어댑터 `DjangoSajuImportUnitOfWork`: 기존 open/close 구현 로직을 dunder로 이사(커밋/롤백 판단은 exc_type 기준).
- use case 2곳: try/except/else 수동 부기 → `with unit_of_work:` 3줄 형태. dry_run 분기는 `contextlib.nullcontext()`.
- 검증: 기존 UoW 관련 테스트 의미 보존(rename 추종) + 전체 green + registry #245 소멸.

## 판정 ③ — 프로젝트 원칙: 일회성 legacy 이관은 BC 밖 scripts/ 소유 [설계 원칙 — saju (b) 잔여 전건·daily #197 소멸]

**무엇을**: "일회성 legacy 데이터 이관(및 그 검증·재대사 도구)은 BC 내부 유스케이스가 아니라 저장소 최상위 `scripts/` 아래 독립 로더로 작성하고, 컷오버 후 폐기 가능한 코드로 취급한다"를 프로젝트 표준으로 확정한다. 선례: review BC의 `scripts/import_legacy_reviews/`(mapping·audit_tags·validation.sql·전용 테스트).

**왜**:
1. 한 번 쓰고 버릴 코드가 영구 코드 기준의 dddjango 검사기(명명·포트/어댑터·DTO·재던짐 규율)와 계속 부딪히는 것이 마찰의 근원이었다. saju (b) 5건(#247·#245·#555·#355·#67)과 daily #197이 전부 BC 내 이관 기계장치에서 발생.
2. BC는 서비스의 영구 도메인만 소유해야 하며, 이관 도구는 수명이 다르다.

**어떻게**:
- **saju**: application/saju에서 이관·재대사 서브시스템(import/reconcile 유스케이스·command/result·SajuImportUnitOfWork·리포트 포트/어댑터) 제거 → `scripts/import_legacy_saju/`로 재구성. 재대사는 BC 상시 기능으로 두지 않고 스크립트의 이관 검증 절차로 흡수(출력 동등성 합격 기준은 유지). 차트 엔진·도메인·API 불변. G1′ 정본 개정 절차.
- **daily**: load_legacy_daily_data 이관 유스케이스·raw-SQL target·operator 배선을 동일 원칙으로 scripts/ 재배치. → **#197 판정 자체가 불요**(분쟁 코드가 BC 밖으로).
- **billing**: 현행 R2~R4 플로우 완주 후 동일 원칙 적용(별도 정리 런).
- **tarot**(전역 적용 확정): legacy_tarot_import_persistence + canonical_tarot_deck_persistence(덱 78장 최초 적재 — 적재 행위는 일회성, 덱 모델·테이블은 BC 잔존)를 scripts/로 재배치 → 이관 계열 10행(#328×2·#630×5·#490×2·#188×1) 소멸. 잔여 39행은 축별 판정.
- **플러그인 영향**: #555 carve-out·#355 완화·#67 applicability 분리는 **불요**(사례 소멸). 판정 ①(#247 역할 수식어 허용)·②(#245 dunder canon+검사기 3자 정합)는 영구 BC UoW에 여전히 유효 — 플러그인 수정 유지. scripts/는 dddjango 검사기 대상 밖(현행 유지).

## 판정 ④ — #256·#351: 0바이트 골격 파일은 aggregate/구현 의무에서 제외 [검사기 수정]

**무엇을**: check-domain-model #256(루트 클래스 요구)과 check-port-adapter-pairing #351(선언당 구현 정확히 하나 요구)에 공통 조건을 추가한다 — **대상 파일이 exact-empty(0바이트)면 해당 요구를 건너뛴다.**

**왜**: bypass 조회 전용 개념(예: tarot 카드·카테고리·스프레드·토픽·프롬프트 6종 — 쓰기·비즈니스 규칙 없음)은 aggregate 없이 port Record(dataclass 계약)로 포맷 경계를 이미 보장한다(available_catalog_out.py). 폴더 골격 표준이 개념별 domain 파일 자리를 요구해 0바이트 파일이 존재하는데, #256/#351이 이를 미완성 aggregate로 오인 — 골격 표준과 두 검사기가 상호 모순(빈 파일 삭제 시 골격 검사 위반 — review 실증). 억지 aggregate/repository 실체화는 무호출 코드 18파일+(원칙 05 위반).

**어떻게**:
- 두 검사기의 대상 수집 단계에서 `path.stat().st_size == 0`(또는 내용 strip 후 빈 문자열)이면 skip.
- 양성 fixture: 0바이트 domain 파일+repository 선언 → 진단 0. 음성 fixture: 주석/pass만 있는 비어 보이는 파일(0바이트 아님) → 기존 진단 유지(우회 방지), 내용 있는 클래스 불완전 → 기존 진단 유지.
- 해소: tarot #256×6·#351×6 = 12행.

## 판정 ⑤ — #630: tarot 모델 클래스명 정렬 [제품 수정 — 검사기 무변경]

**무엇을**: tarot의 영구 모델 클래스 10개에서 `Tarot` 접두를 제거한다(`TarotCardModel`→`CardModel` 등). **실제 DB 테이블 이름은 전부 현행 유지**(`tarot_card` 등 — 데이터·DDL 영향 0).

**왜**: #630 규약 `<app_label>_<entity_snake>`은 공식으로 유지한다(검사기 예외 없음). tarot만 클래스명에 BC명을 중복시켜 공식 결과가 `tarot_tarot_card`(말더듬)가 됐던 것 — 예외자는 tarot이며, review(`ReviewModel`→review_review)·notification(`MarketingConsentModel`→notification_marketing_consent) 등 병합 4개 BC의 명명 규약(클래스에 BC 접두 없음)에 정렬한다. DataGrip 등에서의 `<bc>_*` 테이블 그룹핑은 공식이 보장하므로 유지된다.

**어떻게**: tarot 재작업 사이클에 포함 — 클래스 rename(참조 전수 추종)·명시 db_table 값은 현행 유지(공식과 일치하게 됨)·greenfield 0001 재생성에 반영·전체 green+registry로 #630 영구 10행 소멸 확인. 이관 계열 #630×5는 원칙 B 재배치에서 함께 처리.

## 판정 ⑥ — #634: OHS 창구 표면은 모듈 함수 표준 유지 [제품 수정 — 검사기 무변경]

**무엇을**: 창구 파일(`*_service.py`)의 공개 표면=모듈 함수 표준을 유지한다. tarot의 `PaidReadingEntryService` 클래스를 모듈 함수 `create_paid_tarot_reading(request)`로 전환한다(조립은 함수 내부에서 build_* 호출 — identity 선례 동형).

**왜**: 경계면 ABI 최소화(import 경로+요청/응답 타입만 — 생성자 시그니처가 경계 밖으로 새지 않음). 의미군 묶기는 모듈 네임스페이스 import(`refund_service.refund_now(...)`)가 동일하게 제공. provider별 변형 등 다형성은 BC 내부의 정책 클래스로 두고 창구는 안정된 연산 하나로 유지(확장 시 경계 불변 — 원칙 04). 병합 4개 BC(identity·notification·image)와 그 호출부가 이미 함수 방식.

**어떻게**: tarot 재작업 사이클에 포함 — 클래스→함수 전환·기존 테스트 의미 보존·registry #634 소멸 확인.

## 판정 ⑦ — #157·#484: 계약 어노테이션의 type 별칭 해소 추적 [검사기 수정]

**무엇을**: check-context-isolation #157(계약 타입 하나=파일 하나, 보조 dataclass 예외)과 #484(계약 클래스 `<Operation>Request` 명명, 보조 예외 동일)의 «주 계약이 어노테이션으로 참조하는 보조 dataclass» 판정에서, 어노테이션이 **`type` 별칭(PEP 695)을 경유**하는 경우 별칭을 해소해 실제 구성 클래스까지 따라가도록 보완한다.

**왜**: 규칙의 예외 조항 의도는 이미 보조 자료형을 허용하는데, 별칭(`type PaidCardSelection = PaidMajorCardSelection | PaidMinorCardSelection`)을 못 풀어 사실상 «계약 파일에서 별칭 금지»가 돼 버림. 별칭은 표준 문법이고 반복 타입 표기를 개념 이름으로 묶는 정당한 수단 — 소유자 판정: 별칭 사용이 옳다.
**어떻게**: 어노테이션 추적기에 모듈 내 `type X = ...` 별칭 테이블을 만들어 1단계(중첩 별칭이면 재귀) 해소 후 기존 보조-예외 판정 적용. 양성 fixture: 별칭 경유 참조 보조 dataclass 2개 → 진단 0. 음성: 별칭이 참조하지 않는 무관 공개 클래스 → 기존 진단 유지. 해소: tarot #157×1·#484×2.

## 판정 ⑧ — #169: 예외 파일명 표준 정당 — tarot 이탈 교정 [제품 수정 — 검사기 무변경]

**무엇을**: 파일명=주 클래스 snake_case 규칙은 그대로 유지. tarot 창구 contract/exception/ 파일 5개를 클래스명에 맞춰 rename(`*_exception.py`→`*_published_error.py`).
**왜**: 표준 정당(파일만 보고 내용 식별)·identity/notification 선례 일치·tarot만 이탈. 타 BC 배선 전이라 지금 rename 파급 0.
**어떻게**: tarot 재작업 사이클 포함 — 파일 5개 rename+내부 import 추종·registry #169×5 소멸 확인.

## 판정 ⑨ — #490: 실패 예외 파일 표준 자리 이사 [제품 수정 — 검사기 무변경]

**무엇을**: 트리 표준(실패 예외는 도메인 개념의 exception/ 등 지정 자리) 유지. tarot의 유스케이스 폴더 내 낱개 예외 3파일(paid_reading_entry_temporarily_unavailable·invalid_reading_cursor·invalid_reading_limit)을 표준 자리로 이사(정확한 목적지는 tarot 런이 표준 트리 안에서 설계 — 도메인 예외 폴더 또는 입구 검증 흡수).
**왜**: 표준 정당·review 등 선례 일치(domain_layer/<개념>/exception/)·tarot만 이탈. 새 트리 자리 공식화는 수요 없는 표준 확장이라 기각.
**어떻게**: tarot 재작업 사이클 포함 — 이사+import 추종·registry #490 영구 3행 소멸 확인.

## 판정 ⑩ — #456: 형식 검증 published error 이원 처분 [제품 수정 + 검사기 보완]

**무엇을**:
- (제품) tarot OHS request dataclass 내부의 수동 형식 검사(«undeclared fields» 류)와 `InvalidPaidReadingEntryPublishedError`를 제거한다 — 같은 저장소 내 typed dataclass 호출에서 형식 불일치는 런타임에 도달 불가(TypeError+mypy+테스트가 CI에서 차단). 발동 불가능한 방어 코드이자 거짓 대외 계약.
- (검사기) #456이 published error를 형식 검증으로 분류할 때 이름 패턴(`Invalid~`)이 아니라 **발생 지점**을 봐야 한다: 유스케이스 outcome 매핑에서 raise되는 semantic 실패(`InvalidPaidReadingSelectionPublishedError` — 사용자 데이터 의존, 타입으로 판정 불가)는 정당한 published error로 인정.

**왜**: OHS는 pydantic 없는 in-process 경로 — 형식 보증은 타입 시스템 소유(HTTP 입구의 pydantic 검증과 별개). semantic 검증은 런타임 소유. 두 부류를 발생 지점으로 구분해야 함.
**어떻게**: (제품) tarot 사이클 포함 — 형식 검사·에러 제거, 대외 에러 목록·정본 갱신. (검사기) #456 판정에 raise-지점 분석(contract factory 내 raise=형식 검증 위반 유지 / service outcome 매핑 raise=인정) + 양·음성 fixture. 해소: #456×2.

## 판정 ⑪ — #188: 구역 1:1 규칙 유지 — tarot 구역 재배치 [제품 수정 — 검사기 무변경]

**무엇을**: application `<area>` ↔ `driving_layer/api/<area>` 1:1 규칙 유지. tarot의 짝 없는 구역 `reading`·`generation`을 선례(notification 단일 구역 중첩·review 재작업·identity 컨트롤러 슬라이스)대로 재배치 — 구체 배치는 tarot 런이 G1′ 개정에서 설계.
**왜**: 규칙 취지=폴더 구조만으로 API 표면 항해 가능. 병합 3개 BC 전부 제품 측 정렬로 해결한 선례 — 검사기 완화 필요 없음.
**어떻게**: tarot 사이클 포함 — 구역 재배치+import 추종·registry #188×2 소멸 확인.

## 판정 ⑫ — #396/에러 정본 경로: tarot 중복 폴더 제거 + 2.17.4 ㉮ 변형 가산 되돌림 [제품 수정 + 검사기 되돌림]

**무엇을**: tarot의 `framework/django_ninja/`(error_schema.py·controller_registrar.py)를 삭제하고 정본 `framework/ninja/framework_error_schema.py`(check-error-centralization L76-82 하드코딩 정본) 사용으로 전환한다. 2.17.4에서 이 이탈을 수용하느라 추가한 «canonical 변형 집합(framework/django_ninja/error_schema.py 가산)»(㉮)은 원인 제거로 불필요 — 차기 릴리스에서 되돌려 정본 경로를 단일화한다.

**왜**: 공용 에러 부모의 정본 위치는 플러그인에 명시(하드코딩)돼 있고 main(image 런 산출)이 그 규칙대로 실재. tarot은 분기 시점에 framework/가 없어 병렬로 중복 발명(경로·이름 이탈 — 기술 폴더명은 import 이름 `ninja` 기준이라 `django_ninja`는 4단 판정 불가). 병합 시 이중 실재(㉮가 exit 1로 차단)를 예방한다.

**어떻게**: (제품·tarot 사이클) django_ninja 삭제·전 참조를 framework.ninja.framework_error_schema로 전환·controller_registrar 거취는 표준 안에서 런이 설계. (검사기) ㉮ 변형 가산 제거+단일 정본 fixture 복원. 해소: #396×1 + 병합 위험 1.

---

# 최종 집계 (2026-08-25 판정 세션 종료)

## tarot 49행 처분
- 이관 계열 10행: 원칙 B(판정 ③)로 scripts/ 재배치 — 소멸
- 제품 수정(표준 정당·tarot 이탈) 6축: #630 모델명(⑤)·#634 창구 함수(⑥)·#169 파일명(⑧)·#490 예외 이사(⑨)·#456 형식검사 제거(⑩ 제품분)·#188 구역(⑪)·#396 정본 전환(⑫)
- 검사기 수정 4건: #256/#351 0바이트 제외(④)·#157/#484 별칭 추적(⑦)·#456 semantic 인정(⑩ 검사기분)·㉮ 되돌림(⑫)

## 플러그인 수정 배치 (소유자 작업 목록)
1. #247 — UoW 역할 수식어 허용 (①)
2. #245 — 검사기 3자 정합·dunder 문구 (②)
3. #63 — 에러 하위 타입 선언 인정 (2번 세션 기확정)
4. #256/#351 — 0바이트 골격 제외 (④)
5. #157/#484 — type 별칭 해소 추적 (⑦)
6. #456 — raise 지점 기반 판정(semantic published error 인정) (⑩)
7. ㉮ 되돌림 — django_ninja 변형 가산 제거 (⑫)
8. #195 — factory-born aggregate 정규화 (billing 발견·worklist 상세)
9. #16 — registrar import provenance 분석 불능 (기술 한계 — tarot 재작업 후 잔존 여부 재확인)
10. (선택) #189/#205 — BC 내 usecase-caller 증분 패턴 인정 (identity transition debt 24건)
11. (부수) #197 진단 문구-구현 불일치(check-transaction-boundary.py:337·:491) — 사례는 원칙 B로 소멸, 문구 버그만 잔존
