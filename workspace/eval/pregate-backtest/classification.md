# fortune_reading 백테스트 선행 분류 게이트 — 실측 위반 52건 전수 판정

- 판정일: 2026-09-01
- 대상: STOP-fortune-reading-p1-tree-contract.md(24건) + STOP-fortune-reading-p2-registry-contract.md(28건)
- 명세 기준: G1 승인 `b5392f0` design-spec.md(P1 24건 대조) · P2 승인 `2d44743` design-spec.md(P2 28건 대조)
- 판정 원칙: «결함이 명세에 있었는가»만 본다(커버리지 불문). 애매하면 하류-유래로 보수 분류.

## 재현 방법(건별 인스턴스 확정 근거)

- **P1 24건**: STOP 정지 커밋 `95dd54e` 트리에 v2.17.12 태그 검사기(`registry_gate.py . --anchor b5392f0`)를 재실행해 **귀속 24건을 건별로 원판정 재현**(`p1-gate-v21712.txt`). v2.17.13 검사기 재실행 결과 귀속 집합 동일(diff 0) → P1 버전-델타 0건.
- **P2 28건 중 18건(테스트 측)**: STOP 직전 커밋 `7560b2e` 트리에 v2.17.12/v2.17.13 게이트 재실행 — 양쪽 모두 동일 18건(#13×9 · #385×9) 재현(`p2-gate-tests-v2171{2,3}.txt`).
- **P2 나머지 10건(제품 측)**: STOP 시점 제품 WIP는 미커밋 보존(41f7922은 STOP 문서만 커밋)이라 직접 재실행 불가. 계수는 ①STOP 문면 명시 수(#574 «두 건 모두», #216 «두 owner 파일»), ②검사기 방출 단위 소스 분석(#473=ACL 파일당 1건 후 continue, #129=catch-all raise당 1건, #216=비허용 파일당 1건), ③잔여 산술 28−18−2−2−1=5 → #212×2+#551×2+#129×1 로 확정.

## P1 — tree contract STOP 24건 (명세 기준: `b5392f0` design-spec.md)

| # | 위반(검사기·내용 요지) | 분류 | 근거 인용 |
|---|---|---|---|
| 1 | check-context-isolation `#160` — OHS `contract/response/allowed_evidence.py` 공개 클래스 3개(계약 타입 하나=파일 하나) | **명세-유래** | L488(트리) `│ ├── allowed_evidence.py` — 명세가 이 한 파일을 계획; L231~233이 같은 파일 소유의 중첩 폐쇄 구조를 고정 — L232 «source required/closed: `source_url`, `source_locations`» → 보조 공개 클래스 동거가 명세 배치다 |
| 2 | check-context-isolation `#472` — `contract/response/allowed_evidence.py`의 `pydantic.experimental.missing_sentinel` import(contract/는 stdlib·자기 BC 계약 외 import 금지) | **명세-유래** | L236 «Pydantic 모델은 missing sentinel/field-set 기반으로 optional-by-absence를 표현해 `None` 허용으로 넓히지 않으며» — missing sentinel 사용을 명세가 직접 지시 |
| 3 | check-context-isolation `#472` — `contract/response/allowed_evidence.py`의 `pydantic` import | **명세-유래** | L229 «`AllowedEvidence` Pydantic contract는 CAS 1.1.0과 exact 동치여야 한다.» — contract/ 내 Pydantic 사용이 명세 계약 |
| 4 | check-context-isolation `#472` — `contract/response/cited_answer.py`의 `pydantic` import | **명세-유래** | L236 «…T09가 Pydantic generated schema와 두 CAS에서 …양방향 비교한다.» — 두 CAS(allowed-evidence·cited-answer) 모두 Pydantic 모델임을 명세가 고정(+L202 CitedAnswer exact 계약) |
| 5 | check-context-isolation `#484` — 같은 response/ 계약 클래스 `AllowedEvidence`가 `<Operation>Response` 명명 아님 | **명세-유래** | L71(§2.1) «Allowed Evidence | CAS 1.1.0 exact 4필드 item» + L229 — 클래스명 `AllowedEvidence`와 response/ 배치 둘 다 명세 소유(명명·배치 충돌) |
| 6 | check-context-isolation `#484` — 같은 파일 `EvidenceSource`가 `<Operation>Response` 아님(보조 **dataclass** 예외 불충족 — Pydantic 모델) | **명세-유래** | L232 «source required/closed: `source_url`, `source_locations`» + L229(Pydantic 의무) — 중첩 보조 모델을 Pydantic으로 강제해 #484의 보조-dataclass 면제가 성립 불가 |
| 7 | check-context-isolation `#484` — 같은 파일 `SourceLocation`이 `<Operation>Response` 아님(동상) | **명세-유래** | L233 «location closed: required `location_id`, `provider`, …» + L229 — 위 6번과 동일 구조의 명세 배치·형식 결함 |
| 8 | check-context-isolation `#484` — `contract/response/cited_answer.py`의 `CitedAnswer`가 `<Operation>Response` 아님 | **명세-유래** | L487(트리) `│ ├── cited_answer.py` + L202 «`CitedAnswer`는 CAS 1.1.0 exact `answer: str`, `citations: tuple[AllowedEvidence, ...]`(min 1)다.» — 명명·배치 모두 명세 고정 |
| 9 | check-domain-model `#267` — `shared_value_object/allowed_evidence.py` 공개 클래스 4개(값 객체 하나=파일 하나) | **명세-유래** | L550(트리) `│ ├── allowed_evidence.py` — §3.5 전 가족(item·source·location·digest)을 한 파일로 계획(트리에 분리 파일 없음) |
| 10 | check-domain-model `#267` — `shared_value_object/calculation_projection.py` 공개 클래스 10개 | **명세-유래** | L545(트리) + L182 «`CalculationProjection` | `schema_id…`, `four_pillars: FourPillarsProjection`, …» + L889 «`CalculationOutputContractMismatch`는 `domain_layer/shared_value_object/calculation_projection.py`» — 투영 8종+예외를 한 파일에 명세가 귀속 |
| 11 | check-domain-model `#267` — `shared_value_object/evidence_bundle.py` 공개 클래스 6개 | **명세-유래** | L549(트리) `│ ├── evidence_bundle.py` — §3.3의 EvidenceSet/Group/Crosswalk/ReadingMethod 등 view 가족의 분리 파일이 트리에 없음(그룹 배치가 명세 계획) |
| 12 | check-domain-model `#267` — `shared_value_object/outcome.py` 공개 클래스 2개 | **명세-유래** | L551(트리) `│ └── outcome.py` — Abstained·Blocked(§2.1 L74~75) 두 결과 타입을 한 파일로 계획 |
| 13 | check-domain-model `#267` — `shared_value_object/pinned_reading_bundle.py` 공개 클래스 5개 | **명세-유래** | L546(트리) + L88 «`PinnedReadingBundle`: … VO가 caller `requested_bundle_ref …` mismatch는 domain `BundleSelectionMismatch`다.» — VO·구성 타입 동거를 한 파일로 계획 |
| 14 | check-domain-model `#267` — `shared_value_object/reading_request.py` 공개 클래스 5개 | **명세-유래** | L544(트리) + L889 «`InvalidReadingRequest`는 `domain_layer/shared_value_object/reading_request.py`» — 요청 VO 가족+예외를 한 파일에 명세가 귀속 |
| 15 | check-domain-model `#267` — `shared_value_object/retrieval_plan.py` 공개 클래스 2개 | **명세-유래** | L548(트리) `│ ├── retrieval_plan.py` — RetrievalTarget·RetrievalPlan(§2.1 L67~68) 두 값 객체를 한 파일로 계획 |
| 16 | check-domain-model `#310` — `domain_service/citation_gate.py` 공개 정의 3개(무상태 규칙 하나=파일 하나) | **명세-유래** | L557(트리) + L889 «`InvalidCitation`은 `domain_layer/domain_service/citation_gate.py`» — 게이트 규칙과 예외(및 판정 결과)의 동거를 명세가 고정 |
| 17 | check-domain-model `#8` — domain `shared_value_object/allowed_evidence.py`의 `rfc8785` import(domain 바깥 방향 import 0) | **명세-유래** | L90 «`EvidenceAssemblyService`: … full 4-field RFC 8785 digest 기반 dedupe/order» + L238 «full-item digest는 … RFC 8785 canonical JSON으로 직렬화한 SHA-256» — digest 계산을 domain에 귀속시키면서 port/value 경계를 안 둠(STOP-p1 결정문도 «digest 의존 경계…G1 재설계에서 정리»로 명세 측 수리 확정) |
| 18 | check-layer-skeleton `#488` — 고정 slot `contract/exception/citation_validation_published_error.py` 부재 | **하류-유래** | 명세 무결: L491(트리) `│ ├── citation_validation_published_error.py` — 명세는 파일을 계획했고 코더가 생성 누락. STOP-p1도 «설계 변경 없이 coder가 고칠 수 있[는]» 항목으로 명기 |
| 19 | check-public-surface-annotation `#493` — `allowed_evidence.py` 모듈 변수 `NonEmptyString` 첫 대입 타입 누락 | **하류-유래** | 명세 전문에 `NonEmptyString` 부재(grep 0건) — 코더의 지역 표기 슬립. STOP-p1 coder-수리 목록 명기 |
| 20 | check-test-config `#388` — `test/unit/test_evidence_assembly_service.py`가 `factories/` import | **하류-유래(경계 사례)** | 명세 테스트 계획(T05 계열)에 factory 사용 지시 없음 — factory를 지목한 행은 T01뿐(L700). 유일 positive payload 소유 지정(L267)이 유인이나 unit 내 인라인 재료로 명세 준수 구현 가능 — STOP-p1 coder-수리 목록 명기, 보수 원칙 적용 |
| 21 | check-test-config `#388` — `test/unit/test_reading_request_policy_service.py`가 `factories/` import | **하류-유래(경계 사례)** | L701(T02 행)에 factory 재료 지시 없음 — «`test_reading_request.py`, `test_reading_request_policy_service.py`; required absent→invalid, …» 판정 행렬만 고정. 20번과 동일 판단 |
| 22 | check-test-config `#389` — `test/integration/test_calculation_output_contract.py` DB 신호 없음(integration 부적격) | **명세-유래** | L700(T01 행) «test `application/fortune_reading/test/integration/test_calculation_output_contract.py`» — DB 무관 계약 검증 테스트를 integration/에 명세가 배치 |
| 23 | check-test-config `#389` — `test/integration/test_evidence_schema_equivalence.py` DB 신호 없음 | **명세-유래** | L708(T09 행) «add \| `application/fortune_reading/test/integration/test_evidence_schema_equivalence.py`» — 순수 schema 동치 비교를 integration/에 명세가 배치 |
| 24 | check-test-config `#392` — `test/factories/fortune_calculation_output_factory.py`가 factory_boy 픽스처 아님 | **명세-유래** | L700 «fixture owner `application/fortune_reading/test/factories/fortune_calculation_output_factory.py`» + L267 «(a) …모두 넣은 **유일 positive** payload, (b) …negative payload로 소유한다» — payload dict 소유 파일을 factories/에 명세가 배치(모델 없는 BC라 factory_boy 성립 불가) |

**P1 소계**: 명세-유래 20 · 하류-유래 4 · 버전-델타 0 (24건 전부 v2.17.13 재실행에서 동일 재현 실측)

## P2 — registry contract STOP 28건 (명세 기준: `2d44743` design-spec.md)

18건(#25~#42)은 전부 `test/unit/test_query_translation_adapter.py`(T11 acceptance)의 타 BC OHS import 9개를 #13(context-isolation)·#385(test-config)가 각각 계수한 것이다. 공통 근거: **L1282(T11 행)** «acceptance unit `…test/unit/test_query_translation_adapter.py`: 한 `translate`의 exact published `TranslateRequest` 하나, primitive term/trace normalization과 `invalid_translation_request.py`/`translation_contract_mismatch.py` 번역만 보호» + **L987** «published `InvalidTranslationRequestException`만 …로, `TranslationConfigurationMissingException`, `TranslationConfigurationInvalidException`, `GlossaryUnavailableException`, `GlossaryReferenceMismatchException`, `GlossaryContractInvalidException`, `GlossarySystemMismatchException`과 malformed response는 …`TranslationContractMismatch`로 번역한다.» — exact published request·7종 concrete 예외 번역 검증을 이 테스트에 고정 → 타 BC OHS contract 직접 import가 명세 테스트 계획의 필연이다. STOP-p2도 «T11 acceptance owner는 …직접 사용해 …검증하도록 고정돼 있다»로 확인.

| # | 위반(검사기·내용 요지) | 분류 | 근거 인용 |
|---|---|---|---|
| 25 | `#13` — 타 BC OHS import: `…contract.exception.glossary_contract_invalid_exception` | **명세-유래** | 위 공통 근거(L987에 `GlossaryContractInvalidException` 열거) |
| 26 | `#13` — `…contract.exception.glossary_reference_mismatch_exception` | **명세-유래** | 위 공통 근거(L987 `GlossaryReferenceMismatchException`) |
| 27 | `#13` — `…contract.exception.glossary_system_mismatch_exception` | **명세-유래** | 위 공통 근거(L987 `GlossarySystemMismatchException`) |
| 28 | `#13` — `…contract.exception.glossary_unavailable_exception` | **명세-유래** | 위 공통 근거(L987 `GlossaryUnavailableException`) |
| 29 | `#13` — `…contract.exception.invalid_translation_request_exception` | **명세-유래** | 위 공통 근거(L987 `InvalidTranslationRequestException`) |
| 30 | `#13` — `…contract.exception.translation_configuration_invalid_exception` | **명세-유래** | 위 공통 근거(L987 `TranslationConfigurationInvalidException`) |
| 31 | `#13` — `…contract.exception.translation_configuration_missing_exception` | **명세-유래** | 위 공통 근거(L987 `TranslationConfigurationMissingException`) |
| 32 | `#13` — `…contract.request.translate_request` | **명세-유래** | 위 공통 근거(L1282 «exact published `TranslateRequest` 하나») |
| 33 | `#13` — `…contract.response.translate_response` | **명세-유래** | 위 공통 근거(L987 «response와 trace의 glossary triple은 모두 input과 exact 같아야» — published response 실물 대조 검증 고정) |
| 34 | `#385` — 타 BC import(test/에는 그 BC 테스트만): `…exception.glossary_contract_invalid_exception` | **명세-유래** | 25번과 동일(같은 명세 결함의 이중 계수) |
| 35 | `#385` — `…exception.glossary_reference_mismatch_exception` | **명세-유래** | 26번과 동일 |
| 36 | `#385` — `…exception.glossary_system_mismatch_exception` | **명세-유래** | 27번과 동일 |
| 37 | `#385` — `…exception.glossary_unavailable_exception` | **명세-유래** | 28번과 동일 |
| 38 | `#385` — `…exception.invalid_translation_request_exception` | **명세-유래** | 29번과 동일 |
| 39 | `#385` — `…exception.translation_configuration_invalid_exception` | **명세-유래** | 30번과 동일 |
| 40 | `#385` — `…exception.translation_configuration_missing_exception` | **명세-유래** | 31번과 동일 |
| 41 | `#385` — `…request.translate_request` | **명세-유래** | 32번과 동일 |
| 42 | `#385` — `…response.translate_response` | **명세-유래** | 33번과 동일 |
| 43 | check-port-adapter-pairing `#216` — `port/query_translation/invalid_translation_request.py`(port/에는 `*_port`·`*_in/_out`·`exception.py`만 허용) | **명세-유래** | L644(트리) `│ ├── invalid_translation_request.py` + L987 «각 파일의 public symbol은 하나이고 `query_translation/exception.py`는 required fixed 0-byte empty slot이라 import/re-export가 0이다.» — 분리 owner 파일+0-byte slot 배치가 명세 고정 |
| 44 | check-port-adapter-pairing `#216` — `port/query_translation/translation_contract_mismatch.py`(동상) | **명세-유래** | L645(트리) `│ ├── translation_contract_mismatch.py` + L1671 «…`translation_contract_mismatch.py`가 각각 sole public symbol로 소유하며 fixed …`exception.py`는 0-byte/import/re-export 0이다.» |
| 45 | check-port-adapter-pairing `#574` — use case가 `ReadingBundleIn` 생성(`<data>_in`은 어댑터만 만든다) | **명세-유래** | L1063 «(1) `ReadingBundlePort.pin(ReadingBundleIn(requested_bundle_ref=request.requested_bundle_ref))` 정확히 1회» — use case의 `<data>_in` 생성을 exact 순서로 명세가 지시 |
| 46 | check-port-adapter-pairing `#574` — use case가 `TranslateQueryIn` 생성 | **명세-유래** | L1063 «(7) …key당 `QueryTranslationPort.translate(TranslateQueryIn(...))` 정확히 1회» |
| 47 | check-context-isolation `#473` — ACL `query_translation_adapter.py`에 상대 창구 기저(`*_published_error`) import 없음 | **명세-유래** | L987 — 번역 매핑을 concrete 7종 열거로만 고정(기저 published error import 계획 0). STOP-p2 «현재 query_translation published 계약에는 G1이 승인한 concrete import만 반영» + 발주자 결정 5항이 «fortune_intent 선례(기저 published error+concrete mapping)와 동형으로 개정»을 명세 수리로 지시 |
| 48 | check-port-adapter-pairing `#551` — `ReadingBundlePort`가 (별칭 표기로) ABC 비상속 판정 | **하류-유래** | 명세 무결: L846 «port는 `ABC`+`@abstractmethod`다» + L866 `class ReadingBundlePort(ABC):`(exact 코드) — 검사기는 리터럴 `ABC`/`abc.ABC` 베이스를 통과시키므로 별칭 import는 코더 표기 슬립. STOP-p2 «구현 표기를 고쳐 줄일 수 있»는 finding·결정 7항 «checker대로 수리» |
| 49 | check-port-adapter-pairing `#551` — `QueryTranslationPort` 동상 | **하류-유래** | L966~969 exact 코드 `class QueryTranslationPort(ABC): @abstractmethod def translate(…) -> …: ...` — 48번과 동일 |
| 50 | check-port-adapter-pairing `#212` — port 메서드 `pin`에 «구현이 있다» 판정(별칭 abstractmethod·docstring body) | **하류-유래** | L868 exact 코드 `def pin(self, request: ReadingBundleIn) -> PinnedReadingBundleOut: ...` — 명세 본문은 `...`·리터럴 데코레이터; docstring body/별칭은 코더 표기 |
| 51 | check-port-adapter-pairing `#212` — port 메서드 `translate` 동상 | **하류-유래** | L969 exact 코드 `def translate(self, query: TranslateQueryIn) -> TranslatedQueryOut: ...` — 50번과 동일 |
| 52 | check-synthetic-infra-exc `#129` — reading bundle adapter의 catch-all(`except Exception`) 안 예외 번역 | **하류-유래(경계 사례)** | L935는 번역 대상을 구체 계열로 열거 — «`ServiceActivationError`, ontology artifact/JSON/schema/path/shape 오류는 adapter가 …`ReadingBundleContractMismatch` 하나로 번역» — 전수 명시 매핑으로 명세 준수 구현 가능. «raw exception을 application에 누출하지 않는다» 문구가 catch-all 유인이나, STOP-p2·결정 7항이 구현 표기 수리 대상으로 분류 — 보수 원칙 적용 |

**P2 소계**: 명세-유래 23 · 하류-유래 5 · 버전-델타 0

## 집계

| 분류 | P1 | P2 | 계 |
|---|---:|---:|---:|
| **명세-유래** (백테스트 분모) | 20 | 23 | **43** |
| 하류-유래 (분모 제외) | 4 | 5 | 9 |
| 버전-델타 (분모 제외) | 0 | 0 | 0 |
| 합계 | 24 | 28 | 52 |

**백테스트 합격선 분모 = 명세-유래 43건.**

### 명세-유래 43건의 규칙 축 구성

| 규칙 축 | 건수 | 결함 유형 |
|---|---:|---|
| #13+#385 (T11 타 BC OHS import) | 18 | 테스트 계획(acceptance 소유·검증 재료 지정) |
| #267 (VO 파일 그룹 배치) | 7 | 계획 배치(트리) |
| #484 (OHS response 계약 명명·배치) | 4 | 명명+배치 |
| #472 (contract/ Pydantic import) | 3 | 계약 형식(import) |
| #216 (port 예외 owner 분리 파일) | 2 | 계획 배치(트리) |
| #574 (use case `<data>_in` 생성) | 2 | 계약(exact 호출 순서) |
| #389 (DB 무관 integration 배치) | 2 | 테스트 계획 |
| #160 (계약 파일 다클래스) | 1 | 계획 배치 |
| #310 (무상태 규칙 동거) | 1 | 계획 배치 |
| #8 (domain rfc8785 import) | 1 | import 경계(digest 소유 설계) |
| #392 (factories/ 비-factory_boy) | 1 | 테스트 계획 |
| #473 (ACL 기저 예외 미채택) | 1 | 계약(예외 매핑 설계) |

## 주의 사항

1. **계수 방식(같은 규칙 복수 인스턴스)**: registry_gate의 귀속 단위는 «검사기×규칙×파일×메시지» finding 라인이다(라인번호는 정규화되어 동일성에서 제외). 같은 파일이라도 대상 심볼/import가 다르면 각각 1건(#472는 한 파일에서 `pydantic`·`missing_sentinel` 2건), 같은 import 9개를 두 검사기(#13·#385)가 **이중 계수**해 18건이 된다. 백테스트에서 pre-gate 적발 수를 셀 때도 동일 계수법을 써야 분모 43과 대조 가능하다 — pre-gate가 «T11 테스트 계획 결함»을 1회 지적하면 명세-유래 18건(#25~#42)을 전부 적발한 것으로 세는지, 라인 단위로 세는지 사전에 고정할 것(권고: 명세 결함 라인 기준이면 축 단위 12개, 검사기 라인 기준이면 43 — 혼용 금지).
2. **P2 제품 측 10건의 재현 한계**: STOP 시점 WIP 미보존으로 10건(#43~#52)은 문면·검사기 소스·산술로 복원했다. #212/#551의 2:2 배분은 «포트 2개 × 동일 표기» 가정의 추정이다(합 4는 산술로 닫힘). 두 규칙이 같은 분류(하류-유래)라 배분이 뒤집혀도 집계는 불변이다.
3. **버전-델타 0건의 근거**: 재실행 가능한 42건(P1 24+P2 테스트 18)은 v2.17.13 검사기로 동일 집합 재현을 실측했고, 제품 측 6규칙(#216·#574·#473·#212·#551·#129)은 v2.17.12→13 diff에서 방출 코드 무변(개정은 #328 면제·#63 성공 보충·#493 선언 베이스 3이름·#416 스캔 정밀화·#396 어휘뿐). 단 **#396(framework/pydantic 승인 빚 1건)**은 2.17.13에서 방출 자체가 소멸했으나(실측: 7560b2e 재실행에서 빚 매칭 0) — 애초에 귀속 28건에 불포함된 승인 빚이라 52건·분모와 무관하다.
4. **경계 사례 3건**(#20·#21 `#388`, #52 `#129`)은 명세에 유인 문구가 있으나(유일 positive payload 소유 지정·«raw exception 누출 금지») 명세 준수 구현 경로가 실존했고, STOP/발주자 결정문 스스로 coder-수리 대상으로 분류했다 — 보수 원칙(분모 과대 방지)에 따라 하류-유래. 백테스트에서 pre-gate가 이 3건을 추가 적발해도 분모 위반이 아니라 보너스로만 계상할 것.
5. **P1 #488**(고정 slot 부재)은 명세 트리(L491)가 파일을 계획했으므로 «명세에 없는 파일» 유형이 아니라 «명세대로 안 만든» 코더 누락이다 — pre-gate 표적 아님.
