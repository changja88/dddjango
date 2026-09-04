# S-5 ⓪ 실측 — ninja `Status` 반환 주석 상자 둘 · 오류 응답 base 뭉뚱그림 · `Schema`+`RootModel` 다중 상속

- 실측일 2026-09-04 · 실측자 ⓪(독립) · 브랜치 `fix/field-report-3`
- 격리 사본 `$S=/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3` — `spring-f5ee428`(보고 시점) · `spring`(HEAD `7bfe1aa`) · `spring-c20f525` · `spring-d2eaafe` · `kkebi`(HEAD `6608fb0`)
- 도구 핀: spring venv `mypy 2.3.1` · `django-ninja 1.6.3` · `pydantic 2.13.4` · `django 6.1` · `django-stubs 6.1.0` · python 3.14. kkebi venv도 mypy 2.3.1 · ninja 1.6.3 · pydantic 2.13.4(동일).
- 증거 파일(이 폴더): `proto_ninja3.py`(시제품) · `proto_repos.jsonl`(서고 5사본 122행) · `proto_fixtures.jsonl`(픽스처 87루트) · `mypy_f5ee428_fortune_reading.txt` · `mypy_head_fortune_reading.txt` · `mypy_kkebi_twobox_bcs.txt` · `mini/*.py`+`mypy_mini_results.txt`(형태별 실험) · `check-openapi-error-declaration_codejson_spring-f5ee428.txt` · `check-api-error-controller-contract_codejson_spring-f5ee428.txt` · `checker_api_error_auto_f5ee428.txt` · `dump_openapi.py`. 큰 산출(OpenAPI JSON 2벌 84K/88K, HEAD 검사기 출력)은 `$S/S5/`.

## ① 수치 대조표 (보고자 ↔ 재실측)

| 항목 | 보고자 | 재실측 | 일치 | 근거 |
|---|---|---|---|---|
| mypy f5ee428 `application/fortune_reading` P5 | 5(return-value)+2(metaclass·no-untyped-call)+2(call-arg)=9 | `[return-value]` 5(controller 187·195·199·203·207) · `[metaclass]` 1 + `[no-untyped-call]` 1(schema_out:151) · `[call-arg] root` 2(controller 71·122) = **9** — 파일 전체는 31건/7파일(나머지 22 = P3 `model_config` `[misc]` 15 · P6 Literal `[arg-type]` 4 · P1d `[arg-type]` 2 · `[redundant-expr]` 2 — 다른 대장 항목) | ✔ | `cd $S/spring-f5ee428 && <spring venv>/python -m mypy --follow-imports=silent application/fortune_reading` (9.1s) → `mypy_f5ee428_fortune_reading.txt` |
| mypy HEAD 같은 경로 | 0 | **0**(`Success: no issues found in 186 source files`) | ✔ | `mypy_head_fortune_reading.txt` |
| ⓐ 상자 둘(운영 함수) | 컨트롤러 1(5곳 반환) | f5ee428 **8 함수**(accounts 6 · fortune_record 1 · fortune_reading 1) · HEAD **7**(fortune_reading만 상환) · kkebi **6**(identity 2 · review 2 · saju 2) · 테스트 AnnAssign 3(spring `test/unit` — 운영 밖) | ✘ 과소(보고자는 자기 BC만 봄) | `proto_repos.jsonl` kind=`status_union` |
| ⓑ `response=` 값 = 하위 클래스 있는 base | 같은 컨트롤러 400·503 | spring **2 자리**(400·503 `FortuneReadingErrorSchema`, 하위 4) — f5ee428·c20f525·d2eaafe·**HEAD 동일(미상환)** · kkebi **31 자리**(identity 16 · saju 9 · review 5 · image 1 — 전부 단일값, union 0) · 정당 base(명시값 생성) 0 | ✔(spring) / kkebi 추가 | kind=`response_base` |
| ⓒ `Schema`+`RootModel` | `schema_out.py:151` 1 | f5ee428·c20f525·d2eaafe **1**(같은 자리) · HEAD **0** · kkebi **0** | ✔ | kind=`schema_rootmodel` |
| RootModel 단독(정보) | — | spring 4(`fortune_intent` ACL 어댑터 · driven_layer) + HEAD `schema_out.py:151` 1 · kkebi 1(`tarot/…/deck/schema/schema_out.py:50 TarotCardOut` — `RootModel[Annotated[A \| B, Field(discriminator="type")]]` 단독 상속 = S-5b 권장형이 이미 운영 중, e2e `test_tarot_openapi_success_contract.py:167`이 discriminator 단언) | — | kind=`rootmodel_only` |
| 기존 검사기(리딩 레인 방식 `auto`) | api-error 0건 | api-error `auto` exit 0 — ⓓ#125 후보 5(리딩 :167 포함) · 직접 위반 0 · openapi `auto` exit 0 | ✔ | `checker_api_error_auto_f5ee428.txt` |
| 기존 검사기 **code-json 프로필** | (미실행) | **openapi #63 `wrong-response-schema` 2건**(400 → `InvalidRequestErrorSchema` 선언 필요 · 503 → `RegistryContractMismatch \| ResourceLimit \| Temporary` 선언 필요 · 현재 base) — f5ee428·HEAD 둘 다 exit 2 · api-error code-json: **#125 blocker**(`raise failure` L208 «raise inside managed catch») f5ee428·HEAD 둘 다 exit 2 | — 보고자 미실측 | `check-openapi-error-declaration_codejson_spring-f5ee428.txt` · `check-api-error-controller-contract_codejson_spring-f5ee428.txt` |
| OpenAPI 200 컴포넌트 f5ee428↔HEAD | 6개 바이트 동일(sha `83b8f70c…`) | 6-set(`EvidenceProvisionResponseSchema`·`_EvidenceProvision`·`_EvidencePreparedSchema`·`_AbstainedSchema`·`_ProvisionTraceSchema`·`_EvidenceExcerptSchema`) 정규화 sha `48fe477c…` **양쪽 동일** · fortune_reading 컴포넌트 19개 sha `44356ce8…` 동일 · operation 응답 sha 동일 · 문서 전체는 accounts 증분(`birth_place`) 차이만 | ✔(값은 정규화 차이로 다름·동일성은 재현) | `dump_openapi.py` |

## ② 형상 전수 표 · HEAD 상환 모양

### ⓐ 반환 주석 `Status[…]` 2개 이상 (운영 · 라우트 함수)

| 사본 | 파일:줄 | 함수 | 주석 | mypy |
|---|---|---|---|---|
| spring f5ee428/HEAD | `accounts/driving_layer/api/account/account_controller.py:163/178` | `register_account` | `Status[AccountOut] \| Status[AccountsErrorSchema]` | 통과(값 변수 `x: AccountsErrorSchema = Concrete()`) |
| 〃 | 〃 `:303/318` `:349/364` `:504/550` | `reset_password` `change_password` `withdraw_account` | `Status[None] \| Status[AccountsErrorSchema]` | 통과 |
| 〃 | 〃 `:389/403` `:438/464` | `get_my_profile` `update_my_profile` | `Status[AccountProfileOut] \| Status[AccountsErrorSchema]` | 통과 |
| 〃 | `fortune_record/driving_layer/api/record_archive/record_archive_controller.py:94/99` | `get_fortune_record` | `Status[FortuneRecordDetailOut] \| Status[FortuneRecordErrorSchema]` | 통과(`record_missing: FortuneRecordErrorSchema = …`) |
| spring f5ee428만 | `fortune_reading/driving_layer/api/evidence_provisioning/evidence_provisioning_controller.py:159/164` | `prepare_evidence_bundle` | `Status[EvidenceProvisionResponseSchema] \| Status[_FortuneReadingErrorSchema]` | **오류 5**(값 변수가 concrete 주석) |
| kkebi | `identity/…/profile/profile_controller.py:127` · `identity/…/web_session/web_session_controller.py:452` | `record_first_touch` `refresh_web_session` | `Status[None] \| Status[IdentityErrorSchema]` | 통과 |
| kkebi | `review/…/review_controller.py:192` `:246` | `create_review` `delete_review` | `Status[MyReviewOut] \| Status[ReviewErrorSchema]` / `Status[None] \| …` | 통과 |
| kkebi | `saju/…/reading/reading_controller.py:145` | `start_reading_generation` | `ReadingGenerationOut \| Status[ReadingGenerationOut] \| Status[SajuErrorSchema]`(3항·상자 2) | 통과 |
| kkebi | `saju/…/relationship/relationship_controller.py:227` | `delete_relationship_profile` | `Status[None] \| Status[SajuErrorSchema]` | 통과 |

- 도입 커밋: spring accounts `06346ff`(08-30 dddjango 레인) · fortune_record `eda6b96`(08-30) · fortune_reading `585c9c6`(09-03) · kkebi review `fb14fa2`(08-25 dddjango G0→G2). 즉 상자 둘은 리딩 레인 하나가 아니라 **08-25 이후 dddjango 레인 4개 이상이 반복 산출**한 형태.
- kkebi 상자 둘 BC mypy: `cd $S/kkebi && <kkebi venv>/python -m mypy --follow-imports=silent application/review application/saju/driving_layer application/identity/driving_layer/api/profile application/identity/driving_layer/api/web_session application/tarot/driving_layer` → **0**(338 files) — `mypy_kkebi_twobox_bcs.txt`.
- 반환 주석 형태 분포(`*_controller.py` `) -> …:` 집계): spring — `Status[None] | Status[Err]` 3 · `Status[Out] | Status[Err]` 4 · `Out | Status[Err]` 다수 · `Status[Out | Err]` 1(HEAD 리딩) ; kkebi — `Status[None]` 16 · `Out | Status[Err]` 다수 · 상자 둘 6.

### ⓑ `response=` base 뭉뚱그림

- spring(4 커밋 전부): `evidence_provisioning_controller.py:140~144` `response={200: EvidenceProvisionResponseSchema, 400: _FortuneReadingErrorSchema, 503: _FortuneReadingErrorSchema}` — `bc_error_schema.py` 계층 `FortuneReadingErrorSchema(FrameworkErrorSchema)` ← `InvalidRequestErrorSchema` · `RegistryContractMismatchErrorSchema` · `TemporaryErrorSchema` · `ResourceLimitErrorSchema`(:15~:36). 본문 반환은 전부 concrete(400: InvalidRequest · 503: Registry/Temporary/ResourceLimit) → 정당 base(명시값 base 인스턴스) 아님.
- spring 다른 BC: accounts는 `400: VerificationCodeInvalidError | … | InvalidProfileError`(concrete 6 union) · fortune_record `404: FortuneRecordNotFoundError` — 위반 0. wallet 2곳은 `response=WalletBalanceOut`(dict 아님) → 대상 밖.
- kkebi 31 자리(전부 단일 base 값 · 08-25 개정 이전 이관분): identity `IdentityErrorSchema` 400×3·401×4·403×8·409×1 · saju `SajuErrorSchema` 404×8·409×1 · review `ReviewErrorSchema` 403·404×3·409 · image `ImageErrorSchema` 404. 본문은 `x: <Bc>ErrorSchema = Concrete()` 뒤 `Status(…, x)`.

### ⓒ 다중 상속

- f5ee428 `schema_out.py:151` `class EvidenceProvisionResponseSchema(_Schema, _RootModel[_EvidenceProvision])` — `_Schema`=`ninja.Schema`, `_RootModel`=`pydantic.RootModel` 별칭 import(:5~:10). `type _EvidenceProvision = _Annotated[_EvidencePreparedSchema | _AbstainedSchema, _Field(discriminator="kind")]`(:145~:148).

### HEAD 상환 모양 (`git -C $S/spring diff f5ee428 HEAD -- …controller.py …schema_out.py`)

```
-    ) -> Status[EvidenceProvisionResponseSchema] | Status[_FortuneReadingErrorSchema]:
+    ) -> Status[EvidenceProvisionResponseSchema | _FortuneReadingErrorSchema]:
…
-class EvidenceProvisionResponseSchema(_Schema, _RootModel[_EvidenceProvision]):
+class EvidenceProvisionResponseSchema(_RootModel[_EvidenceProvision]):
```
- 상환 커밋 `4cfedb4`(09-04 «ninja Status 반환 주석·RootModel 단독 상속 정리 — mypy 121→112» · «동작 보존 타이핑 수리 2줄 · 계약 변경 0 · response= 불변») → **최소형**. 같은 diff의 나머지(`model_config: _ConfigDict` 주석 제거 12곳 · `reason=provision.reason.value`)는 P3·P6 커밋(`a59cc3a`·`84e531b`) 몫.
- `response=` 400/503 base 선언은 HEAD에도 그대로(교리 정렬 미실행 — 발주측 OpenAPI 변경 승인 사안) → code-json #63은 HEAD에서도 red(①표).

## ③ mypy 재현 · 형태별 실험

- 재현: ①표. `ninja/responses.py`(venv 1.6.3) `:22 T = TypeVar("T")` · `:25 class Status(Generic[T]):` · `:35 def __init__(self, status_code: int, value: T)` — 불변 TypeVar. `ninja/schema.py` `:159 class ResolverMetaclass(ModelMetaclass)` · `:209 class Schema(BaseModel, metaclass=ResolverMetaclass)`; mypy note: «"ninja.schema.ResolverMetaclass" conflicts with "pydantic.root_model._RootModelMetaclass"».
- 형태별(`mini/`, `<spring venv>/python -m mypy --strict --python-version 3.14 <file>` · Django 플러그인 없음):

| 모듈 | 형태 | 결과 |
|---|---|---|
| m1 | `-> Status[Resp] \| Status[Base]` + `return Status(400, C1())` | **오류** `[return-value] got "Status[C1]", expected "Status[Resp] \| Status[Base]"` |
| m1b | 같은 주석 + `e: Base = C1(); return Status(400, e)` | 통과 (spring accounts·fortune_record·kkebi 6곳이 이 형태) |
| m1c | `-> Status[Resp] \| Status[C1] \| Status[C2]` + concrete 직접 | 통과 |
| m8 | 상자 둘 + `e: C1 = C1()` | **오류**(리딩 f5ee428 형태) |
| m2 | `-> Status[Resp \| Base]` + concrete 직접 | 통과 |
| m3 | `-> Status[Resp \| C1 \| C2]` (정본 :184 형태) | 통과 |
| m6 | `-> Resp \| Status[Base]` + `Status(404, C1())` 직접 | **통과**(상자 하나면 union 문맥에서 T=Base 추론) |
| m7 | `-> Resp \| Status[C1]`(정본 :677/:727/:777 형태) | 통과 |
| m4 | `class X(Schema, RootModel[Annotated[A \| B, Field(discriminator="kind")]])` + `X(root=…)` | **오류 3** `[no-untyped-call] __init_subclass__` · `[metaclass]` · `[call-arg] root` |
| m5 | `class X(RootModel[Annotated[…]])` 단독 + `X(root=…)` | 통과 |

- 해석: mypy가 막는 조합은 «반환 union에 `Status[…]` 항이 **둘 이상** + 값의 정적 타입이 선언 상자의 하위». `Status[…]` 항이 하나면(m2·m3·m6·m7) 그 항이 추론 문맥이 되어 concrete를 넣어도 통과. 따라서 ⓐ «Subscript 2개 이상»은 mypy가 막는 형상과 정확히 같은 축이되, 값 변수를 base로 주석하면(m1b) mypy는 통과하므로 ⓐ는 mypy보다 넓다(운영 13 함수가 mypy-clean 상자 둘).

## ④ 플러그인 문면 좌표 (+R 번호·블록 IRI) · 모순 예시

`implementation-django-ninja/references/final.md`(1,058줄 · 2.2/3.1/6.1/6.2 전부 graph-owned):

| # | 줄 | 내용 | 절(Section IRI 접미) | 블록 | 규범 |
|---|---|---|---|---|---|
| ① | :124~:128 | «직접 반환하는 BC 오류 status는 … 오류 타입 그대로 선언 … 명시값으로 채운 base 인스턴스면 base. 상위 base로 뭉뚱그리거나 반환하지 않는 타입을 적지 않는다(… 2026-08-25)» | `s009-2.2`(2.2 Operation 선언) | `…/final.md/s009-2.2/b9`(kind-norm · restates `s023-6.2/b30`·`b34`) | **R-0681**(rev2 `@2026-08-25` prefLabel «직접 반환 오류 타입 그대로의 response= 선언(concrete·Union·명시값 base — base 뭉뚱그림 금지)») · R-0682 |
| ①′ | :835~:839 | «**응답 선언과 OpenAPI.** … base로 뭉뚱그려 선언하지 않는다(2026-08-25 개정)» | `s023-6.2` | `s023-6.2/b34` | R-0086·**R-0087**(rev2 `@2026-08-25` «OpenAPI status mapping에 반환 concrete 그대로 노출(base 뭉뚱그림 금지)»)·R-0088·R-0089·R-0090 |
| ①″ | `SKILL.md:30` | 의미 미러 «…base로 뭉뚱그리지 않는다…» | `SKILL.md/s004` | `…/SKILL.md/s004/b8`(restates b9·b10·b30·b34) | R-2929(«…base 뭉뚱그림 금지») · R-2930~R-2932 |
| ② | :184 `-> Status[OrderOut \| OrderProductNotFoundError \| OrderInsufficientStockError]` | 예시(상자 하나·concrete union) | `s009-2.2` | `s009-2.2/b18`(kind-code) | — |
| ② | :677 `-> OrderOut \| Status[OrderProductNotFoundError]` | 예시 | `s023-6.2` | `s023-6.2/b20`(kind-code) | — |
| ② | :727 `-> OrderOut \| Status[OrderNotFoundError]` | 예시 | 〃 | `s023-6.2/b23` | — |
| ② | :777 `-> OrderOut \| Status[OrderTemporarilyUnavailableError]` | 예시 | 〃 | `s023-6.2/b28` | — |
| ③ | «반환 주석» 0줄 · `Status[` 184·677·727·777(4) · `RootModel` 0 · `discriminator` 346·349(이벤트 봉투)·636(URI 표기) · `union` 124·349·354·357·358·835 · `Union[` 124·349·835 | | | | |

- S-5b(성공 union 응답) 후보 절: `### 3.1 Request/response schema 분리`(:330~:364 · `s012-3.1` · graph-owned) — 현재 discriminated union 언급은 «발행 이벤트 봉투» 문맥(:346~:358)뿐. `### 6.1 Status code mapping`(`s022-6.1`)·`### 2.2`(`s009-2.2`)가 S-5a 후보.
- `architecture-api/references/final.md`(670줄): ④ «응답 계약» = `### 5.2 응답 계약` :199~:207(`s022-5.2` graph-owned · b1~b6 = R-1967~R-1972; b1 «상태 코드별 응답 본문 존재 여부와 schema를 분리해 정의한다» R-1967) · `### 5.3 계약 체크리스트` :209~:226 Response/Error 행 · `### 14.3 반영해야 할 계약 표면` :626~:639(`s065-14.3` · «상태 코드별 response body schema와 header»). `discriminat`·`oneOf`·`anyOf`·`union`·«둘 이상/두 모양/성공 응답» **0건** → 기존 계약 문면 없음(중복 없음). 계약 한 문장 자리 후보 = `s022-5.2` 새 블록(b7) 또는 b1 개정.
- ⑤ 코퍼스 코드 펜스 전수(`dddjango/skills/*/SKILL.md`·`*/references/final.md`·`agents/*.md`·`commands/*.md`): `Status[…] | Status[…]` **0** · `(Schema, RootModel` **0** · `RootModel` **0** · `response={…: A | B}` 익명 union **0** · `Status[`는 ninja final.md 4줄뿐(implementation-django :232·:1087의 `OrderStatus["PENDING"]`는 무관). → **모순 예시 없음**(보고자 «예시는 상자 하나» 일치).
- ⑥ 등재: `workspace/plan/2026-08-11-rule-owner-map.md` — 이 검사기 행 **11**(#59 #62 #120 #121 #123 #124 #125 #126 #131 #132 #474 · 표 547행 · 마지막 #645 :558) · `workspace/design/2026-08-08-tree-revision-spec.md` — 표 553행 · 해당 행 :385(#59) :386(#62) :450~:459(#120~#132) :771(#474) · 마지막 번호 #645(:1174) → S-1 #646·S-4 #647 뒤 S-5 ⓐⓑⓒ = **#648~#650** 예상 · `workspace/design/2026-08-11-predicates.md` — 표 153행 · #124(:117)·#125(:118)·#132(:119) 확인(나머지 번호는 단일 번호 행으로 안 잡힘 — 미확인). `ontology/ISSUED` 마지막 **R-3450**(09-04) → 신설 R은 R-3451부터(`ontology-authoring.md §5`). rulepack `by_checker` 145 R · `by_alias` 21(#59 등 미등재). registry #15(api-error) · #5(openapi). 검사기 byte 미러 `codex-dddjango/skills/dddjango/scripts/…` 동일 확인(`cmp`).

## ⑤ 검사기 구조 · 3규칙 자리 · 기존 규칙 겹침

`dddjango/scripts/check-api-error-controller-contract.py`(7,486줄):
- 두 레인. **code-profile 레인** `_run`(:6999) — `auto`·`preserve-established`·`--error-bc` 없음이면 `[]` 반환(:7002~:7005) → `_semantic_findings`(:6911)·`_discover_operations`(:2360)·`_analyze_operation`(:6033)은 `dddjango-code-json`+selector에서만 돈다. **표준 트리 슬라이스** `_tree_slice2`(:7203)·`_slice_check_controller_ast`(:7117) — «모든 프로필(auto 포함)에서 돈다»(:7071 주석), `application/*/driving_layer/api/<area>/**/*.py` 전 파일(controller/비controller 구분 `is_controller`)과 OHS `*_service.py`를 AST로 보며 `bc_error_schema` area는 건너뜀(:7226).
- `NINJA_STATUS`(:84 `"ninja.Status"`)는 `_status_call`(:2860 본문 `Status(...)` 호출 provenance)·`_exact_status_return`(:3033)에서만 쓴다. `node.returns`는 :893(inert 판정)·:1988(`computed_field` int)·:2234(바인딩 표현 수집)에서만 읽고 **반환 주석 형상 분석은 없다**; `:1079 BitOr`는 `_scalar_int_annotation`(필드 int 주석)이라 보고자 «반환 주석 BitOr/Subscript를 읽는다»는 부정확(읽되 형상 판정 없음).
- `response=` 키워드는 이 검사기가 **전혀 파싱하지 않는다**(`keyword.arg == "response"` 0). 파싱·대조는 `check-openapi-error-declaration.py`(3,604줄) — `_scan_response_statuses`(:647, 프로필 무관 status 집합) + code-json 카탈로그 `ErrorSymbol kind "base"/"concrete"`(:2224·:2265, `bc_error_schema.py` 상속 그래프) + `_constructed_error`(:2380, 명시값 base 인스턴스 = `field_values`) → `wrong-response-schema` #63.
- 방출: `_append_finding`(:2173, `Finding(path, lineno, category, shown, rule=…)`) · 트리 슬라이스는 `findings.add("#N", where, msg)`(공용 `findings.py`). 운영 경로 `_is_production_path`(:397 · `test|tests` 디렉터리·`test_*`·`conftest.py` 제외).
- **3규칙 자리**: ⓐ·ⓒ는 AST+import 바인딩만 필요 → `_slice_check_controller_ast`(프로필 무관)에 두면 리딩 레인처럼 `auto`로 도는 G2에서도 울린다. ⓑ는 `bc_error_schema.py` 계층이 필요(트리 슬라이스는 현재 그 파일을 건너뜀) — 그러나 아래 겹침.
- **겹침 판정**: ⓑ(S-5e) ≡ 기존 **#63 `wrong-response-schema`**(openapi 검사기 code-json) — f5ee428·HEAD에서 이미 400/503을 위반으로 낸다(①표). #124(요청=메서드 1:1)·#125(입구 로직)·#126(helper)는 무관. ⓐ·ⓒ는 기존 규칙과 겹침 없음. 부수 발견: openapi 검사기 자체 문면이 stale — `:6` docstring «`response={status: <Bc>ErrorSchema}` 선언의 일치» · `:3362` 조치 «각 직접 반환 status를 같은 BC의 <Bc>ErrorSchema **base로 선언**하고» ↔ 같은 실행의 위반 메시지는 concrete/union을 요구(R-0681 rev2).
- 픽스처: `workspace/eval/fixtures/api_error_controller/{good,bad_rules}`(AUTO_PAIRS `fixture_matrix.py:61` · `--error-profile auto`) · `api_error_controller_code/{good,bad_rules}`(`checker_baseline_matrix.py:97` `_RISK_SELECTOR_ARGS` code-json · `findings_count_matrix.py:158` · `checker_cross_matrix.py:216~225`) · `openapi_error_declaration`·`openapi_decl_missing`·`response_schema_bypass`. 삼중 등재 = `fixture_matrix.py`+`checker_baseline_matrix.py`+`findings_count_matrix.py`(Makefile :145~:147). `bc_error_schema.py`를 가진 픽스처 20루트 중 하위 클래스 있는 base는 `api_error_controller_code`(`LessonErrorSchema` ← `LessonNotFoundError`·`LessonConflictError`)뿐이고 `response={…404: LessonNotFoundError}` concrete → ⓑ 무해. 87 픽스처 루트 전수에서 ⓐⓑⓒ·RootModel **0**(`proto_fixtures.jsonl`) → 새 good/bad 픽스처 필요 · 기존 픽스처 red 전환 없음.

## ⑥ 시제품 결과 · 오탐 (`proto_ninja3.py`)

- 판정: import 바인딩(`from ninja import Status as _S`·`from ninja.responses import Status`·상대 import·단순 재별칭) 해소 · 반환 주석 `A | B`/`Union[…]`/`Optional[…]`/문자열 평탄화 후 `Subscript.value∈{ninja.Status, ninja.responses.Status}` 계수 · `response=` dict 값 union 각 항을 `application/<bc>/…/bc_error_schema.py` 파일 안 상속 그래프에 대조(자식 있는 클래스=base) · 클래스 bases에 `ninja.Schema`∧`pydantic.RootModel`. 부가: 정당 base 휴리스틱(`_base_constructed_for_status` — 같은 status로 base를 직접 생성해 반환하면 `response_base_justified`).
- 실행: `python3 $S/proto/proto_ninja3.py --root $S/spring-f5ee428 … --root $S/kkebi …` → `proto_repos.jsonl`; 픽스처 87루트 → `proto_fixtures.jsonl`.

| 사본 | ⓐ status_union | ⓑ response_base | ⓑ justified | ⓒ schema_rootmodel | rootmodel_only | response 비dict |
|---|---|---|---|---|---|---|
| spring d2eaafe | 8 | 2 | 0 | 1 | 4 | 2 |
| spring c20f525 | 8 | 2 | 0 | 1 | 4 | 2 |
| spring f5ee428 | 8 | 2 | 0 | 1 | 4 | 2 |
| spring HEAD 7bfe1aa | 7 | 2 | 0 | 0 | 5 | 2 |
| kkebi 6608fb0 | 6 | 31 | 0 | 0 | 1 | 0 |
| 픽스처 87 | 0 | 0 | 0 | 0 | 0 | 0 |

- 오탐 분석: (1) «명시값으로 채운 base 인스턴스면 base»(final.md:125) 정당 사례가 두 서고에 **0** — ⓑ의 오탐 여부를 실데이터로 못 잰다; 시제품 휴리스틱은 있으나 픽스처 good에 이 사례를 반드시 넣어야 한다. 기존 #63은 `_constructed_error`가 `field_values`로 이 사례를 이미 구분한다(:2380~:2420). (2) `response=` 값 union(accounts 400 concrete 6) → 각 항 concrete라 미검출(정상). (3) `Status` 별칭 `_Status`(테스트)·`ninja.responses` 경로 해소됨; `ninja_extra` 재수출은 두 서고에 없음(`from ninja import Status`만 · spring 10파일·kkebi 18파일). (4) RootModel이 `schema_out.py` 밖(spring `fortune_intent` driven_layer ACL 4클래스) — ⓒ는 `Schema` 동반 상속만 보므로 무해; ⓒ를 `schema_out.py`로 한정하면 driving_layer 밖은 애초 대상 밖. (5) kkebi `TarotCardOut`은 S-5b 권장형 그대로 → ⓒ 통과(참양성 0·오탐 0). (6) ⓐ는 mypy-clean 상자 둘 13 함수(spring 7·kkebi 6)를 잡는다 — 레거시라 앵커 차분(N∖L) 격리 전제. (7) 테스트 파일의 상자 둘 AnnAssign 3(spring `test/unit`)은 운영 경로 제외로 대상 밖. (8) 상자 둘이 3항 union 안에 섞인 kkebi saju :145도 검출.

## ⑦ OpenAPI 실측

- 방법: `cd $S/<사본> && DJANGO_SETTINGS_MODULE=spring_dream_server.settings.test <spring venv>/python $S/S5/dump_openapi.py <out.json>` — `django.setup()` + `spring_dream_server.api:api.get_openapi_schema()`만(DB 접속 없음 · 성공).
- 200 컴포넌트: `EvidenceProvisionResponseSchema` = `{"$ref": "#/components/schemas/_EvidenceProvision", "title": …, "description": …}`; `_EvidenceProvision` = `{"oneOf": [_EvidencePreparedSchema, _AbstainedSchema], "discriminator": {"propertyName": "kind", "mapping": {…}}}` — f5ee428(`Schema`+`RootModel`)과 HEAD(`RootModel` 단독) **바이트 동일**(6-set sha `48fe477c…`, fortune_reading 19 컴포넌트 sha `44356ce8…`, operation `POST /api/fortune-readings/evidence-bundles` 응답 200/400/503 sha 동일). 400·503은 둘 다 `$ref …/FortuneReadingErrorSchema`(e2e `test_evidence_openapi.py:233` `400==503` · `:238 endswith("/FortuneReadingErrorSchema")` 동결 그대로).
- 보고자 sha `83b8f70c…`는 정규화 방식이 달라 값 재현 불가 — «동일함»은 재현.

## ⑧ 확정 방향과 어긋나는 사실

1. **S-5e(ⓑ)는 신설이 아니라 기존 #63과 중복.** `check-openapi-error-declaration.py` code-json 프로필이 f5ee428·HEAD 모두에서 400/503 base 선언을 `wrong-response-schema`로 이미 낸다. 리딩 G2 «0건»의 원인은 규칙 부재가 아니라 레인이 두 검사기를 `--error-profile auto`로만 돌린 것(`.dddjango/20260831-2331-fortune-reading/refactor-scope.md` 5·15행; Coordinator `commands/dddjango.md:119` «Error response와 무관한 G2는 … `auto`»). api-error 검사기에 ⓑ를 새로 두면 한 사건 두 소유자(#63 vs 신규) — 「한 주제 한 소유자」와 충돌.
2. **검사기 자리 미특정 — code 레인에 두면 여전히 auto에서 무동작.** `_run`은 auto/`--error-bc` 없음이면 `[]`. «리딩 G2에서 잡히게» 하려면 ⓐ·ⓒ는 프로필 무관 트리 슬라이스(`_slice_check_controller_ast`)여야 한다(결정 기록은 자리를 안 적음 — 보충 사항).
3. **ⓐ 근거 문장이 사실보다 넓다.** «`Status[A] | Status[B]`는 불변이라 concrete 반환이 mypy strict에서 막히므로 금지» — 상자 둘이어도 값 변수를 base로 주석하면 통과(m1b · spring 7·kkebi 6 = 13 운영 함수가 mypy-clean 상자 둘). 막히는 것은 «상자 둘 + concrete 정적 타입 값». 문면은 «concrete 값을 직접 넣으면 막힌다 / 형태 자체를 금지한다»로 정확히 써야 한다. 또 `-> Out | Status[Base]`(상자 하나)는 concrete를 직접 넣어도 통과(m6).
4. **레거시 규모.** ⓐ 13 함수·ⓑ kkebi 31·spring 2(HEAD 잔존)는 전부 기존 산출물 — 앵커 차분 격리 없이는 kkebi 전체 실행이 대량 red.
5. **openapi 검사기 문면 stale**(`:6` docstring · `:3362` 조치 «<Bc>ErrorSchema base로 선언»)이 R-0681 rev2와 반대 지시 — 확정 방향에 없는 수리 대상.
6. **S-5b 실증 근거는 kkebi에 이미 있다**: `tarot/…/schema_out.py:50 TarotCardOut(RootModel[Annotated[…, Field(discriminator="type")]])` + e2e discriminator 단언 — 정본 예시로 인용 가능(플러그인 밖 사례).
7. 범위 밖 관찰: api-error code-json이 리딩 컨트롤러 `raise failure`(HEAD :208)를 #125 blocker로 낸다(f5ee428·HEAD) — 같은 레인이 code-json이었다면 S-5와 무관하게 red였음(auto 사각의 또 다른 증거).
- 어긋남 없음으로 확인된 것: 코퍼스 예시 모순 없음 · architecture-api에 기존 계약 문면 없음(중복 없음) · mypy 9건·OpenAPI 동일성·ⓒ 1건·발주측 최소형 상환은 보고자 그대로.

## ⑨ 사각 · 불확실

- 보고자 sha `83b8f70c…` 값 미재현(정규화 불명) — 동일성만 재현.
- kkebi mypy는 kkebi venv python(`~/Desktop/kkebi-server/.venv`)을 사본 cwd에서 읽기 실행 — 지시의 «spring venv» 범위 밖 도구 사용(읽기 전용·`uv run` 아님).
- `predicates.md`에서 #59·#62·#120·#121·#123·#126·#131·#474 행을 단일 번호 정규식으로 못 찾음(결합 행 가능) — 집계 3행(#124·#125·#132)만 확인.
- 시제품 상속 그래프는 `bc_error_schema.py` 파일 안만(파일 밖 base — `FrameworkErrorSchema` — 는 대상 밖이라 무관) · 함수 안 중첩 클래스·`ninja_extra` 재수출·`__init__` 재수출은 미처리(두 서고에 사례 없음).
- `_RootModelMetaclass` 이름은 mypy note 인용(pydantic 2.13.4 소스 직접 확인 안 함).
- 형태별 실험은 Django 플러그인 없이 `--strict`만 — spring 설정(`warn_unreachable`·추가 error code)과 동일하지 않으나 return-value/metaclass 판정에는 영향 없음(실서고 재현과 일치).
