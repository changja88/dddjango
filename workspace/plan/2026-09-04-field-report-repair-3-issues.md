# 현장 보고 3 — 문제 목록(추적표) · 재작성 1단계 (2026-09-04)

원문: `workspace/plan/2026-09-04-field-report-spring-dream-django-stubs-generic-base.md`(발주자 세션 작성 · 대상 v2.17.16 · 264행).
이 문서: 원문에서 «보고받은 문제»와 «보고자가 추천한 수정 방향»만 번호를 붙여 뽑은 목록이다. 판단·실측·결정은 아직 없다 — 그건 ⓪~⑥ 판형에서 한다. 원문 행 번호(`L…`)는 위 파일 기준이다.
우리 쪽 현재 = v2.17.17(e842759). 보고서가 «E(명시 `Any` 금지)»라고 부르는 것은 v2.17.17에 #645·R-3447/R-3448로 이미 들어갔다 — 그 영향은 §3에 따로 적었다.

상태 값: `접수`(목록화만) · `⓪`(실측 중) · `①`(문제 리뷰) · `결정 대기` · `계획` · `구현` · `완료` · `기각` · `발주측` · `범위 밖`.

## §0 추적표

| ID | 문제(한 줄) | 종류 | 보고자 추천 방향(요약) | 결정 표시 | 상태 |
|---|---|---|---|---|---|
| S-1 | django-stubs 제네릭 기저(`ModelForm`·`ModelAdmin`·`TabularInline`/`StackedInline`·`BaseInlineFormSet`)는 런타임 subscript 불가인데 플러그인 문면이 없어 레인 10개가 세 모양(맨몸/ignore/별칭)으로 갈렸다 | 문면 | `implementation-django`에 admin·ModelForm 타이핑 절 신설 + 문장 3개 + 정본 예시 1벌 · houserules §4 참조 한 문장 · 검사기 불요 | **결정 09-04 «확정»** — 방향은 §2-A(문면 + 검사기 #646 · 보고자 원안과 다름) | 결정 |
| S-2 | Django 기저에 `# type: ignore[type-arg]`를 붙여 8 BC가 빚을 숨겼다 — 문면만으론 재발 가능 | 검사기(선택) | `check-public-surface-annotation.py`(#493) 확장 또는 신규 규칙: `ClassDef` 헤더·`inlines` 첫 대입 줄의 `type: ignore[type-arg]` = 위반 | **S-1 ⓑ에 흡수**(09-04) — 별도 결정 없음 | 흡수 |
| S-3 | fortune_character 빌드 lane-report가 자기 BC를 빼고 mypy를 돌려 «Success» — 공허한 통과 | 발주측 | 플러그인 수정 없음. R-12 발주 가이드 1줄에 «자기 BC 경로 필수» 있는지만 확인 | **결정 09-04 «확정»** — §2-B(플러그인 수정 없음 · R-12 행에 반영 문구 추기) | 결정 |
| S-4 | 딕셔너리를 레코드로 쓰는 모양(`dict/Mapping[str, object\|Any]` 1,110줄 · mypy 70건)을 플러그인 예시·권고가 만든다 | 문면 + 검사기 | 한 줄 규칙 «모든 JSON은 입구에서 `TypedDict`» + 붙임 2·예외 1 + 결정표 6행 · houserules §4·implementation-python·architecture-ddd 문면 · 검사기 (a) 주석 스캔 (b) `json.load` 무파싱 | **결정 09-04 «확정»(이 세션 재확인)** — §2-C(문면 + R-3447 개정 + 검사기 #647 위반 · `json.load` 무검증은 ⓓ 후보) | 결정 |
| S-5 | ninja 컨트롤러 반환 주석 `Status[A] \| Status[B]`·오류 응답 base 뭉뚱그림·200 union의 `Schema`+`RootModel` 다중 상속을 문면·검사기가 안 막는다(mypy 9건) | 문면 + 검사기 | `implementation-django-ninja` 두 문장 + 정본 예시 2개 · `check-api-error-controller-contract.py` 규칙 (a)(b)(c) | — | 접수 |
| N-1 | notification admin 2건(`obj is None` 재검사 → `[redundant-expr]`/`[unreachable]`) — 보고자: A/R-3443의 admin 변종, 새 항목 아님 | 관측 | 없음(기존 규범 적용 확인만) | — | 범위 밖 |
| N-2 | parler `TranslatableAdmin`·`TranslatableModelForm`의 `# type: ignore[misc]` 6곳 — 보고자: 서드파티 미타입이라 정당 | 관측 | 없음 | — | 범위 밖 |
| N-3 | 발주측 처리 계획(fortune_character 28건 직접 상환 · ignore 18줄 보류 · G2 grep 조건 · P1/P5 상환) | 발주측 | S-1/S-2/S-4/S-5 처분 뒤 발주측이 진행 | — | 발주측 |

## §1 항목 상세

### S-1 · django-stubs 제네릭 기저 처리 규칙 부재 (L11 · L95~L161)

증거(보고자 실측 · L67~L77):
- BC 10개 · admin 클래스 40개가 세 모양 — ① 맨몸 14(fortune_character · mypy `[type-arg]` 26건) · ② `# type: ignore[type-arg]` 17 + `inlines` 1줄(8 BC) · ③ `TYPE_CHECKING` 별칭 9(service_policy · 정답).
- ①과 ③이 같은 날(8/30) 두 레인에서 나왔다 — 문면이 없으니 레인 운.
- 맨몸에 타입 인자를 그냥 붙이면 `django.setup()`이 `TypeError: … is not subscriptable`로 죽고 mypy plugin까지 INTERNAL ERROR(L50~L65).
- 플러그인 문면 검색(L79~L91): `django-stubs`·`ModelForm[`·`type-arg` 0건. `implementation-django-web/references/final.md:208` 예시 `class ArticleForm(forms.ModelForm):`가 ①의 모양 그대로. `implementation-django`에 admin 절 없음(L88). houserules §4에 «제네릭 기저 타입 인자»·«런타임 subscript 불가»·`type: ignore` 규칙 없음(L90).

보고자 추천 방향(세부 ID):
- S-1a 문장 1(L100): django-stubs는 위 기저를 제네릭으로 선언하지만 **런타임 클래스는 subscript 불가** — 기저에 직접 `X[Model]`을 쓰면 import 시 `TypeError`.
- S-1b 문장 2(L101): 기저로 쓰는 별칭은 `if TYPE_CHECKING:`에 `TypeAlias`(`# noqa: UP040`) · `else:`에 런타임 클래스를 같은 이름으로. **주석에만 쓰는 별칭은 `type` 문**(PEP 695 · 지연 평가).
- S-1c 문장 3(L102): Django 기저에 `# type: ignore[type-arg]`를 붙이지 않는다 — 통과가 아니라 은폐.
- S-1d 조건 한 줄(L161): 프로젝트 settings/`manage.py`에 `django_stubs_ext.monkeypatch()`가 있으면 별칭 없이 `X[Model]` 직접 표기. 플러그인이 monkeypatch를 강제하지는 않는다(의존성 0인 별칭이 기본값).
- S-1e 배치(L97): `implementation-django`에 «Django admin·ModelForm 타이핑» 절 신설(admin은 driven_layer 저작 화면이라 django 코어 스킬이 맞다) · houserules §4에는 참조 한 문장. 원문 추적표(L11)는 `implementation-django-web` §6 web form 절도 후보로 적었다.
- S-1f 정본 예시(L106~L158): service_policy 실물을 일반화한 코드 1벌 — `_ModelFormBase`·`_InlineFormSetBase`·`_InlineBase`·`_ModelAdminBase` 4별칭 + 주석 전용 `type ParentInlineFormSet = BaseInlineFormSet[Any, ParentModel, Any]` + `ChildInlineForm`/`ChildInlineFormSet`/`ChildInline`/`ParentAdmin`(`save_model`·`save_related` 시그니처 포함). #493 «첫 대입 타입» 규율과 함께 완결되는 모양이라고 명시.
- S-1g `Any` 자리(L160): 인라인 자식 모델이 여럿이면 `inlines`·`formsets`의 자식 인자는 `Any`일 수밖에 없다(`_M` invariant) — E(명시 `Any` 금지) 규범에서 «프레임워크 미러 조건부 허용»으로 빼야 한다.

보고자 판단 기준 적용(L21~L22): «플러그인이 만든 모양이면 문면 수정» → S-1 필수. «검사가 못 잡는데 두 레인 이상 반복» → S-1c 금지 문장 + S-2는 선택.

### S-2 · `# type: ignore[type-arg]` 부착 검사기 (선택 · L12 · L163~L165)

증거: 17클래스 + `inlines` 1줄(8 BC) · mypy `ignore-without-code`는 만족하므로 mypy가 못 잡는다(L27 · L72).

보고자 추천 방향:
- S-2a 규칙: `ClassDef` 헤더 줄과 `inlines` 첫 대입 줄의 `# type: ignore[type-arg]`를 위반으로 계수. 맨몸(①)은 mypy 몫이라 제외.
- S-2b 픽스처: good 1(별칭) / bad 2(ignore 부착).
- S-2c 배치: `check-public-surface-annotation.py`(#493) 확장 또는 신규 규칙. «E 배치와 같은 판형이라 E 착수 시 함께 넣는 편이 싸다»(→ E는 이미 완료 · §3).
- S-2d 대안(기각 시): 발주자 G2 체크리스트에 `grep -rn 'type: ignore\[type-arg\]' application/<bc>` 1줄로 대신.

결정 표시: 보고자가 «사용자 결정 대기»로 두었다. 채택/기각은 범위 확정 브리프에서.

### S-3 · 발주측 — 자기 BC 제외한 mypy «Success» (L13 · L167~L169)

증거: fortune_character 빌드(8/30) lane-report mypy 범위 `spring_dream_server framework`(자기 BC 미포함) · 증분 fortune-character-2(9/2)도 같은 범위 — 레인 2회.
보고자 추천 방향: 플러그인 수정 없음(B 처분대로 게이트는 프로젝트 소유). 발주서 G2 체크리스트는 이미 `--follow-imports=silent application/<bc>`. **R-12 발주 가이드 1줄**에 «자기 BC 경로 필수 · `spring_dream_server framework`만 돌린 결과는 증거가 아니다»가 들어가는지만 확인.
우리 쪽 할 일: R-12 문구 확인 1건(문면 추가가 필요하면 그때 항목 승격).

### S-4 · 딕셔너리-레코드 금지 · `TypedDict`/pydantic 강제 (L14 · L190~L236)

보고자 기재 결정(L192~L194): 발주자(사용자)가 P1 원인을 듣고 «레코드 모양 딕셔너리를 플러그인 차원에서 금지 · `TypedDict`(내부)·pydantic(외부 검증)·dataclass/값 객체(도메인) 강제 · **무조건 · 최대한 타입 강제**»로 결정. 발주자 세션의 «조회표 예외» 완화 제안은 사용자가 «무조건»으로 재확인. → **이 세션에서는 아직 결정으로 세지 않는다**(다른 세션 발화 · 범위 확정 브리프에서 재확인).

증거(L196~L200 · spring main `c20f525`):
- mypy P1 61 + P2 9 = 70건(훅 범위 124건의 56%). 대표: `rag_builder/source_adapter.py:19` `SourceBlock.coordinate: Mapping[str, object]` → `int(first["page_id"])` 11곳 `[call-overload]` · `cli.py` `"object" has no attribute` 10곳 · `service_runtime.py` 인덱스 6곳 · rfc8785 `_Value` 6곳.
- 주석 규모(비테스트) `(dict|Mapping)[str, (object|Any)]` **1,110줄** — `framework/technology/rag` 828 · **레인 BC 281**(fortune_reading 59 · llm_access 48 · chat_relay 35 · fortune_character 27 · fortune_calculation 24 · promotion 16 · fortune_catalog 14 · query_translation 11 · fortune_record 10 …). BC 281줄 = 레인 산출물.
- 좌표 레코드 실물 6종(`coordinates.py::_STRUCTURE_VALIDATORS`) — 종류마다 필수 키가 다르다.

원인(보고자 · L202~L205):
- `TypedDict`는 `implementation-python/references/final.md` §1.5 5줄 **권고**뿐 · houserules·에이전트·검사기에 강제 없음.
- `architecture-ddd/references/final.md:1618` 도메인 예시 `values: dict[str, Any]`가 스킬 문면 중 유일한 `dict[str, Any]` 예시 — 권고 한 절 대 예시 한 줄이면 레인은 예시를 따른다.
- houserules §4 «모든 이름에 타입»은 `Mapping[str, object]`로 충족된다 — 정보 0. E만으로는 `Any`→`object` 이동을 못 막는다.

보고자 추천 방향(세부 ID):
- S-4a 한 줄 규칙(L209): **모든 JSON은 입구에서 `TypedDict`로 받는다. 받은 뒤 `object`·`Any`·`dict[str, …]`로 흘리지 않는다.**
- S-4b 붙임 2·예외 1(L211~L214): ⑴ 외부 JSON(파일·HTTP·타 시스템)은 `pydantic.TypeAdapter(그TypedDict).validate_json/validate_python`으로 **검증하며** 받는다 · 내부 JSON은 검증 없이 `TypedDict` ⑵ 키가 데이터인 조회표는 `dict[str, 그TypedDict]` · 예외: 구조를 정하지 않는 임의 JSON만 재귀 별칭 `type JsonValue = bool | int | float | str | None | list[JsonValue] | dict[str, JsonValue]`.
- S-4c 결정표 6행(L216~L225): 레코드(내부)→`TypedDict`(여럿이면 `Literal` 판별 union) · 레코드(외부)→`TypeAdapter`/pydantic 검증 파싱 · 도메인 개념→dataclass·값 객체 · 조회표→`dict[K, V]` 구체(V 레코드면 `TypedDict`) · 임의 JSON 통과→`JsonValue` · 타입 있는 값→실제 클래스. 각 행의 금지: `dict[str, object|Any]`·검증 없는 `TypedDict`·딕셔너리·값 타입 `object|Any`·자리표시 `object`.
- S-4d 배치(L14): houserules §4 + `implementation-python`(TypedDict·pydantic 경계 파싱) + `architecture-ddd`(DTO/VO).
- S-4e 예시 정정(L204): `architecture-ddd:1618` `dict[str, Any]` 예시 — 보고자는 원인으로만 지목(명시 제안은 없음 · 정정 대상으로 추적).
- S-4f 검사기 (a)(L229): 함수 시그니처·변수·클래스 속성 주석의 `(dict|Mapping|MutableMapping)[…, (object|Any)]` = 위반. AST `Subscript`만 · 오탐 거의 없음 · E와 같은 배치·판형.
- S-4g 검사기 (b)(L230): `json.load(s)` 결과가 pydantic `model_validate`/`TypeAdapter`/명시 파서를 거치지 않고 대입·반환 = 위반(1레인 실측 뒤 오탐률 확인).
- S-4h 전제(L231): legacy 1,110줄은 registry_gate 앵커 차분(N∖L)으로 격리 — 새 레인 산출물만 막힌다.

발주측 계획(L233~L236 · 추적만): P1 61건은 좌표 `TypedDict` 6종 + `SourceBlock.coordinate` union으로 상환(`as_int` 도우미 방식 불채택) · 나머지 1,040줄은 규칙 확정 뒤 RAG 런타임 타이핑 발주 후보.

### S-5 · ninja `Status` 반환 주석·오류 base 뭉뚱그림·`Schema`+`RootModel` (L15 · L238~L264)

증거(L240~L249 · spring main `f5ee428` · 리딩 BC 16행 산출물):
- `evidence_provisioning_controller.py:164` `-> Status[EvidenceProvisionResponseSchema] | Status[_FortuneReadingErrorSchema]` + `return Status(400, _InvalidRequestErrorSchema())` 5곳 → `[return-value]` **5건**. 원인 `ninja.Status(Generic[T])`의 `T` 불변.
- 같은 컨트롤러 `response={200: …, 400: _FortuneReadingErrorSchema, 503: _FortuneReadingErrorSchema}` — 2026-08-25 개정 규칙(«base로 뭉뚱그려 선언하지 않는다»)과 어긋남 · 리딩 e2e가 그 모양을 동결 단언.
- `schema/schema_out.py:151` `class EvidenceProvisionResponseSchema(_Schema, _RootModel[_EvidenceProvision])` → `[metaclass]` + `[no-untyped-call]` **2건** · 파생 `[call-arg] root` 컨트롤러 71·122 **2건**. 런타임 정상.
- 실측: `-> Status[Resp | Base]`(상자 하나) 통과 · `_Schema` 기저 제거 시 mypy 통과 + OpenAPI 200 컴포넌트 바이트 동일 · `response={200: A | B}` 익명 union은 이름 붙은 컴포넌트·discriminator 상실(계약 변경) · 오류 응답 concrete 선언은 e2e 단언 2개 변경(OpenAPI 변경 승인 사안).

원인(보고자 · L251~L255):
- `implementation-django-ninja/references/final.md` 184·677·727·777 예시는 `Status` 하나 형태지만 산문 규칙 없음(«반환 주석» 0건) — 레인이 «`A | B`면 된다»로 읽어 상자 둘.
- 200 discriminated union 응답 문면 없음 · `RootModel` 언급 0(architecture-ddd 이벤트 봉투 1곳뿐).
- `check-api-error-controller-contract.py`는 `NINJA_STATUS`·`node.returns`를 읽지만 (a) `Status[…]` 항 2개 이상 (b) `response=` 값이 `bc_error_schema.py` 안 하위 클래스를 가진 base 를 위반으로 안 낸다 — 리딩 G2에서 0건.

보고자 추천 방향(세부 ID):
- S-5a 문장 1(L259): 컨트롤러 반환 주석은 `Status` **하나**에 성공·오류 union(`-> Status[Out | ErrA | ErrB]`). `Status[A] | Status[B]`는 불변성 때문에 금지.
- S-5b 문장 2(L259): 성공 응답이 판별 키로 갈리는 union이면 `class XResponseSchema(RootModel[Annotated[A | B, Field(discriminator="kind")]])` · `Schema`를 함께 상속하지 않는다(메타클래스 충돌) · `response={200: A | B}` 익명 union 금지(discriminator 상실).
- S-5c 정본 예시: 두 형태 각 1개.
- S-5d 검사기 (a)(L260): 반환 주석에 `ninja.Status` Subscript 2개 이상 → 위반 «반환 주석의 `Status`는 하나».
- S-5e 검사기 (b): `response=` 값이 `bc_error_schema.py`에서 하위 클래스를 가진 base → 위반 «base 뭉뚱그림(2026-08-25)».
- S-5f 검사기 (c): `schema_out.py` 클래스가 `ninja.Schema`와 `pydantic.RootModel`을 함께 상속 → 위반.
- 셋 다 AST 바인딩만으로 판정 가능(보고자).

발주측 계획(L262~L264 · 추적만): P5 9건은 최소형(반환 주석 1줄 + `_Schema` 기저 제거 1줄) 상환 후보 · 교리 정렬은 OpenAPI 변경 승인이 필요한 별도 결정.

### N-1 · N-2 · N-3 (범위 밖 · 추적만)

- N-1(L48 · L171~L173): `admin/email_notice_template/panel.py:79` `if obj is None or obj.pk is None` — 보고자: A/R-3443 «선언 타입 재검사 금지»가 admin display 메서드에도 적용된다는 관측. 처방은 `obj is None` 삭제 또는 `obj._state.adding`. 새 항목 아님.
- N-2(L77): parler 6곳 `# type: ignore[misc]`는 정당. 범위 밖.
- N-3(L184~L188): fortune_character 26 + notification 2는 service_policy 패턴으로 직접 상환(mypy 152→124 기대 · 기저 교체 시 #493 귀속 0을 위해 `model/form/formset/extra/readonly_fields` 주석 같은 커밋) · ignore 18줄은 S-1/S-2 처분 뒤 · G2 grep 조건은 S-2와 함께.

## §2 결정 기록(사용자 «확정» 발화만 · 09-04)

### §2-A · S-1 확정(09-04) — 문면 + 검사기

사용자 이해 확인: 문제 = «admin에서 상속하는 django-stubs 제네릭 기저에 모델 타입 인자를 안 적었다(14 맨몸 · 17 ignore)» · 원인 = «그냥 적으면 런타임이 죽는데 플러그인이 적는 법을 안 알려 줬고 예시마저 맨몸». 사용자 방침: «타입을 작성하라고 하자 · 작성하라고 했으면 검사기도 봐야 한다».

1. 문면(houserules §4 신설 R): django-stubs 제네릭 기저(`ModelForm`·`ModelAdmin`·`TabularInline`/`StackedInline`·`BaseInlineFormSet` 등)는 모델 타입 인자를 적는다 · 런타임 전제는 settings의 `django_stubs_ext.monkeypatch()`(django-stubs 공식 처방 · `django-stubs-ext` 운영 의존성 · §6.1 «표준 도구 없으면 셋업»이 덮음) · 패치를 못 쓰는 프로젝트만 `TYPE_CHECKING` 별칭 · `# type: ignore[type-arg]` 금지. 예시: implementation-django에 admin 1벌(직접 표기 + 별칭 대안) · django-web §6 `class ArticleForm(forms.ModelForm):`(:208) → `forms.ModelForm[Article]` 정정.
2. 검사기 #646 신설(`check-public-surface-annotation.py` · #493/#645 옆): ⓐ 위 기저를 맨몸으로 상속 = 위반 ⓑ 그 줄의 `# type: ignore[type-arg]` = 위반 · `TYPE_CHECKING` 별칭 상속은 별칭 정의를 따라가 통과 · AST만(mypy 불요).
3. 픽스처 good(직접 표기·별칭) / bad(맨몸·ignore) · 삼중 등재 · 규칙 등재 3문서.
4. S-2는 ⓑ에 흡수. S-1g(`Any` 면제)는 ⓪ 실측 뒤 별도.
근거: 플러그인은 mypy를 돌리지 않으므로(S-3 «공허한 Success») 문면만으로는 안 울린다 — 플러그인 원칙 «문면 + 결정적 백스톱». 보고자 «검사기 불요»는 채택하지 않음. 별칭이 아니라 monkeypatch를 기본으로 한 이유: 파일마다 8줄 별칭 블록이 없어지고(속도), django-stubs README의 1번 처방이다.

### §2-B · S-3 확정(09-04) — 플러그인 수정 없음 · R-12 추기

R-12 발주 가이드는 문서 미착수(로드맵 51행 등재만)라, 그 행에 «mypy 증거는 자기 BC 경로 포함 필수 · `spring_dream_server framework`만 돌린 결과는 증거가 아니다» 1줄을 반영 문구로 추기(B 기각 때 «툴체인 게이트는 훅·발주서 소유» 1줄 선례). R-12 착수 시 반영.

### §2-C · S-4 확정(09-04) — 문면 + R-3447 개정 + 검사기

사용자 이해 확인: «받는 순간 dict인 건 어쩔 수 없고, dict인 채로 흘리거나 dict로 만든 게 문제» · «애초에 받을 때부터 TypedDict로 받으면 된다»(외부는 `TypeAdapter` 검증 포함 · 내부는 처음부터 그 모양으로 생성). spring 세션의 «무조건 · 최대 타입 강제»를 이 세션에서 «확정»으로 재확인.

1. 규칙(houserules §4 · R-3447 rev2 + 신설 R): «키가 정해진 값 묶음은 딕셔너리로 쓰지 않는다. 내부 데이터는 `TypedDict`, 외부에서 온 JSON은 `pydantic.TypeAdapter(그TypedDict).validate_python/validate_json`으로 검증하며 받는다, 도메인 개념은 값 객체. `dict[str, object]`·`dict[str, Any]` 주석 금지. 조회표는 `dict[K, 구체 V]`(V 레코드면 `TypedDict`) · 구조를 정하지 않는 임의 JSON만 `type JsonValue = …` 재귀 별칭.» 보고자 결정표 6행(L218~L225)을 §4에 그대로. R-3447의 «JSON 문서는 `Mapping[str, object]`» 문장은 삭제·대체.
2. 예시 정정: architecture-ddd `values: dict[str, Any]`(:1618) → `TypedDict`. implementation-python §1.5(TypedDict 5줄 권고)를 «어떻게» 절로 확장(TypedDict·`TypeAdapter`·`JsonValue`·`Literal` 판별 union).
3. 검사기 #647(`check-public-surface-annotation.py`): 주석(시그니처·변수·클래스 속성)의 `(dict|Mapping|MutableMapping)[…, object|Any]` = 위반. AST `Subscript`만. 결정 1(수리 2)에서 ⓓ 후보였던 `dict[str, Any]`는 이 자리에 한해 위반으로 승격 — 사용자 «확정».
4. `json.load(s)` 결과를 `TypeAdapter`/`model_validate`/명시 파서 없이 대입·반환 = ⓓ 후보(exit 불산입 · 감수자). 보고자 (b)의 «위반»은 채택하지 않음(오탐률 미확인 · 차단이면 레인 정지).
5. legacy 1,110줄은 registry_gate 앵커 차분으로 격리(새 레인 산출물만).
보고자 원안 대비 차이 3: (b) 후보화 · R-3447 개정 추가 · architecture-ddd 예시 정정 명시.

### 남은 결정 표시

- ~~S-4~~ → §2-C 확정.
- S-5e(오류 응답 base 뭉뚱그림 검사)는 발주측 OpenAPI 변경 승인과 맞물린다 — 플러그인 검사기 채택은 우리 결정, 발주측 상환은 그쪽 결정.

## §3 우리 쪽 메모 — v2.17.17과의 겹침·충돌(⓪ 실측 대상)

- **E는 완료됐다**: #645(시그니처 bare `Any` 차단 · 변수/제네릭 안 `Any`는 ⓓ 후보) + R-3447/R-3448. 보고서의 «E 착수 시 함께»(S-2c·S-4f)는 «별도 추가»로 읽는다.
- **S-4a ↔ R-3447 충돌**: R-3447(houserules §4 · v2.17.17)은 «경계 입력(JSON·…)은 `object` 또는 정확 타입으로 받아 받는 즉시 좁힌다 … **JSON 문서는 `Mapping[str, object]`**»라고 썼다. S-4a는 «JSON은 입구에서 `TypedDict` · `object`로 흘리지 않는다». 두 문면이 같은 자리에서 반대 처방이다 — S-4를 채택하면 R-3447 개정(rev2)이 같은 배치에 들어간다. ⓪에서 R-3447 정확 문면·위치 확인.
- **S-1g ↔ #645**: 예시의 `inlines: ClassVar[list[type[admin.TabularInline[Any, ParentModel]]]]`는 클래스 속성의 nested `Any` → ⓓ 후보(차단 아님). `type ParentInlineFormSet = BaseInlineFormSet[Any, ParentModel, Any]`는 `TypeAlias` 재별칭 — #645 docstring이 «검출 한계(표면 밖)»로 적은 자리. `save_related(…, formsets: list[ParentInlineFormSet], …)`는 별칭 이름이라 시그니처 bare 아님. → 보고자가 요구한 «프레임워크 미러 조건부 허용» 면제가 실제로 필요한지(#645 실행으로) ⓪에서 확인.
- **S-1e 배치 후보 2개**(원문 안에서도 갈림: `implementation-django` admin 절 신설 vs `implementation-django-web` §6) — ②에서 하나로.
- **S-5e 근거 «2026-08-25 개정 규칙(base 뭉뚱그림 금지)»** — ninja reference 안 실제 문면·R 번호 ⓪에서 확인.
- 보고서 수치(40클래스·1,110줄·70건·9건)는 spring `c20f525`/`f5ee428`/`d2eaafe` 기준 — ⓪에서 격리 사본으로 재실측(읽기 전용 · rsync/`git clone`+`checkout --detach`).
