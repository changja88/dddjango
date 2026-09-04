# 현장 보고 3 · ⓪ 실측 — S-4 (딕셔너리-레코드 금지 · `TypedDict`/pydantic 강제)

작성 2026-09-04 · 브랜치 `fix/field-report-3` · 실측 사본 `$S=/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3`
(`$S/spring-c20f525` = 보고자 S-4 시점 · `$S/spring` = HEAD `7bfe1aa` · `$S/kkebi` = HEAD `6608fb0`). 실서고는 읽지 않았고 사본에서만 실행했다.
이 문서 옆의 스크립트·출력은 `evidence/S4/`(작은 것) · 큰 jsonl 은 `$S/S4/`(`proto_*.jsonl`·`findings_*.jsonl`·`mypy_cache_*`).

## ① 수치 대조표

| 항목 | 보고자(L196~L200) | 재실측 c20f525 | 재실측 spring HEAD 7bfe1aa | 재실측 kkebi 6608fb0 | 명령/스크립트 |
|---|---|---|---|---|---|
| 주석 줄 `(dict\|Mapping)[str, (object\|Any)]` framework+application 비테스트 | **1,110** | **1,110** (일치) | 1,098 | 431 (application 만 · framework 0) | 보고자 명령 그대로 (`broad_grep.sh` «reporter cmd») |
| ├ `framework/technology/rag` | 828 | 828 | 822 | — | 〃 |
| └ `application`(레인 BC) | 281 | 281 | 276 | 431 | 〃 |
| 넓힌 패턴 `(dict\|Dict\|Mapping\|MutableMapping)\[[^]]*, *(object\|Any)\]` · 소스 루트 전부 · 비테스트 | — | 1,123 (app 288 · fw 830 · spring_dream_server 5) | 1,111 (283 · 823 · 5) | 550 (app 437 · **web 111** · fw 1 · kkebi_server 1) | `broad_grep.sh` → `broad_grep.out` |
| ├ 키가 `str` 아닌 것 | — | 9줄 (`dict[object, object]` 12회 · `dict[str \| None, object]` 1) | 9 | 7 (`dict[object, object]` 8 · `Mapping[object, object]` 1) | 〃 |
| ├ 중첩 `list[dict[str, Any\|object]]` | — | 175 | 172 | 36 | 〃 |
| ├ 값 `Any` : `object` (출현 수) | — | 701 : 495 | 694 : 487 | **157 : 417** | 〃 |
| └ `dict` : `Mapping` (출현 수) | — | 821 : 375 | 805 : 376 | 475 : 99 | 〃 |
| mypy 훅 범위(`application framework spring_dream_server`) | 124 | **124** (25 files / 2,938 checked) | **0** (2,951 checked) | 미실행 | `mypy_c20f525.txt` |
| ├ P1 | 61 | **61** (a17 b18 c11 d11 e4) | 0 | — | `classify_mypy.py`(대장 줄 표 file:line 대조 · 미대응 0) |
| └ P2 | 9 | **9** | 0 | — | 〃 |
| #647 시제품 exact 히트(주석 AST) | — | 1,076 히트 / 863 줄(def 줄 기준) | 1,061 / 848 | 759 / 723 | `proto_647.py` → `proto_*.out` |
| json.load(s) 호출 / ⓓ 후보 | — | 95 / 95 | 95 / 95 | 60 / 59 | 〃 |
| #645 ⓓ 후보 줄(현 검사기) | — | 575 | 569 | 379 | `check-public-surface-annotation.py` + `DJR_FINDINGS_JSON` |

보고자 수치 4종(1,110 · 828 · 281 · 70=61+9)은 전부 **그대로 재현**된다. 훅 범위 표기만 어긋난다 — `.pre-commit-config.yaml:70` 실제 훅은 `uv run mypy spring_dream_server framework`(application 없음)이고, 124건은 대장 «검증 명령»(`docs/superpowers/plans/2026-09-04-mypy-debt-ledger.md` L42 `uv run mypy application framework spring_dream_server`) 기준이다. 사본에서는 `~/Desktop/spring_dream_server/.venv/bin/python -m mypy …`(cwd=사본)로 실행했고 결과가 대장과 file:line 단위로 124/124 일치했다.

## ② BC별 분포 · HEAD 상환 모양

보고자 명령(비테스트) BC별 — c20f525 → HEAD(변한 곳만 굵게):

| BC | c20f525 | HEAD | 넓힌 패턴 HEAD |
|---|---|---|---|
| fortune_reading | 59 | **54** | 54 |
| llm_access | 48 | 48 | 48 |
| chat_relay | 35 | 35 | 35 |
| fortune_character | 27 | 27 | 27 |
| fortune_calculation | 24 | 24 | 24 |
| promotion | 16 | 16 | 16 |
| fortune_catalog | 14 | 14 | 14 |
| query_translation | 11 | 11 | 11 |
| fortune_record | 10 | 10 | **17**(`Dict[`/비-str 키 변종 7) |
| product 9 · service_policy 8 · fortune_intent 8 · media_library 6 · wallet 3 · notification 2 · accounts 1 | 동일 | 동일 | 동일 |

kkebi(보고자 명령): billing 169 · saju 78 · product_observability 53 · tarot 51 · identity 33 · notification 18 · share 17 · daily 6(넓힌 12) · top3 3 · image 2 · review 1. 넓힌 패턴은 `web/` 111줄·`scripts/` 206줄(시제품 기준)이 추가로 잡힌다.

**HEAD 상환 모양(c20f525..HEAD · `git log` 60커밋 · 머지 `c3117ef` «39행 RAG 런타임 타이핑 · D58 집행»)**
- 주석 줄은 **1,110 → 1,098(−12)** 뿐이다. 줄 단위 차분(`$S/S4/rep_c20.txt`/`rep_head.txt` comm): 제거 18(`source_adapter.py: coordinate: Mapping[str, object]` · `coordinates.py` 머저/`_registered` 반환 `dict[str, Any]` 6 · `rfc8785_adapter.py` 5 · `service_runtime.py cast` 3 · `ontology_c11.py` 2 · `cited_answer_schema.py` 1) · 추가 6(코드 3: `Sequence[Mapping[str, object]]`×2 · `-> Mapping[str, object]` · 주석/독스트링 3).
- 채택 도구(rag+application 비테스트 · `git grep` 계수 c20f525→HEAD): `TypedDict` 2→**19** · `TypeAdapter` 0→**5**(`service_runtime.py:100~103` 모듈 상수 4 + 호출) · `JsonValue` 38→67 · `Literal[` 129→137 · `RootModel` 7→7 · `model_validate` 8→8 · `NotRequired` 0→0 · `@dataclass` 600→602.
- 실물: `framework/technology/rag/runtime/rag_builder/source_adapter.py:13~124` — 좌표 6종을 `coordinate_kind: Literal[…]` 판별 키 `TypedDict` 6개 + union `CitationCoordinate`로, `SourceBlock.coordinate: CitationCoordinate`. `framework/technology/rag/runtime/json_value.py`(신설 36줄) — `type JsonValue = JsonScalar | Sequence[JsonValue] | Mapping[str, JsonValue]`(공변 arm · D4) + **`to_json_value(value: object) -> JsonValue`** 브리지(독스트링: «TypedDict는 라이브러리의 재귀 `_Value` 타입과 호환되지 않으므로»).
- 대장 P1/P2 정의(c20f525 `2026-09-04-mypy-debt-ledger.md` L22~L28): P1 «동적 JSON 값을 `object`로 타이핑해 사용 지점마다 좁힘이 없다» 61(P1a `int()/float()`에 object 17 · P1b 속성/인덱스/반복 18 · P1c 구체 타입 매개변수 전달 11 · P1d `dict/Mapping[str, object]`→rfc8785 `_Value`/pydantic `JsonDict` 11 · P1e 컬렉션 불변성 4) · P2 «`json.load` 등 `Any`를 구체 반환형에서 그대로 반환» 9. HEAD 대장 요약표: P1·P2 «상환 완료»(D58 · `c3117ef` + P1d 3 `08acee4`), 재분류 «① 레코드 TypedDict 30 · ② 자리표시 object 반환형→실제 클래스 19 · ③ 직렬화 경계 JsonValue 12 · ④ 파일 경계 파싱 9». 그리고 **«2차 정리(전면 cast 151·`dict[str, object|Any]` 822 — 플러그인 S-4 검사기 뒤)는 별도 발주»** — 즉 발주측은 mypy 70건만 갚았고 주석 822줄은 플러그인 검사기 이후로 미뤘다.

## ③ mypy 재현

- `$S/spring-c20f525`: `Found 124 errors in 25 files (checked 2938 source files)` · 코드별 arg-type 29 · misc 21 · attr-defined 20 · call-overload 16 · no-any-return 9 · index 7 · return-value 6 · assignment 5 · 기타 11. 파일별 상위: `rag_builder/cli.py` 29 · `coordinates.py` 17 · `fortune_reading/…/schema_out.py` 14 · `steps/__init__.py` 9 · `evidence_provisioning_controller.py` 8 · `service_runtime.py` 7 · `framework/pydantic/cited_answer_schema.py` 7.
- 대장 대조(`classify_mypy.py`): P1a 17(call-overload 16·arg-type 1) · P1b 18(attr-defined 13·index 5) · P1c 11(arg-type 9·operator 2) · P1d 11(arg-type 10·typeddict-item 1) · P1e 4 · P2 9(no-any-return 9) · P3 19 · P4 4 · P5 9 · P6 3 · P7a 5 · P7b 14 = 124 · 미대응 0. `object` 문면이 든 오류 줄 59.
- `$S/spring`(HEAD): `Success: no issues found in 2951 source files`.
- 주의: venv 는 실서고 `.venv`를 그대로 썼다(cwd=사본). django 플러그인의 settings 해소가 cwd 의 사본에서 됐는지는 확인하지 않았다 — 결과가 대장과 file:line 로 124/124 일치하므로 판정에는 영향이 없다고 본다.

## ④ 플러그인 문면 좌표 + 모순 목록

코드 펜스/산문 구분은 `corpus_grep.py`(펜스 상태 추적) → `corpus_dict.tsv`·`corpus_kw.tsv`.

| # | 좌표 | 블록 IRI(`ontology/rules/*.ttl`) | 원문 요지 | 구분 |
|---|---|---|---|---|
| ① | `dddjango/skills/discipline-houserules/SKILL.md:76` (§4 · graph-owned 마커 L64) | `…/discipline-houserules/SKILL.md/s007-4/b7` · `statesNorm R-3447, R-3448` | «**`Any` 는 타입이 아니라 검사 포기다 — 어디에도 쓰지 않는다.** … 제네릭 인자(`dict[str, Any]`) 전부다 … 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 쪽 선언은 `object`(또는 정확 타입)로 쓴다 … 시그니처의 `Any` 는 #645 가 차단하고, 변수·제네릭 안의 `Any` 는 ⓓ 후보(#645) … 경계 입력(JSON·폼 `cleaned_data`·`request.user`·무스텁 서드파티)은 `object` 또는 프레임워크가 주는 정확한 타입으로 받아 **받는 즉시** 좁힌다(`TypeIs`·`isinstance`·`type() is` — implementation-python §1.12 · … architecture-ddd §3.1 …). JSON 문서는 `Mapping[str, object]`.» | 산문 |
| ①′ | R 소유 | `djr:R-3447`(Prohibition · prefLabel «Any 금지 — 시그니처…·프레임워크 오버라이드도 object/정확 타입…») · **`djr:R-3448`(Obligation · prefLabel «경계 입력…은 object/정확 타입으로 받아 받는 즉시 좁힘 … · JSON 은 Mapping[str, object]»)** · 둘 다 `@2026-09-04` rev1 · `ISSUED:3447~3448` | «JSON 문서는 `Mapping[str, object]`» 문장은 **R-3448 의 것**이다 | — |
| ① codex | `codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md:69` | (의미 미러) | 같은 문단 | 산문 |
| ② | `dddjango/skills/implementation-python/references/final.md:106~124` (§1.5 · graph-owned) | `…/implementation-python/references/final.md/s007-1.5/b1`(norm · `R-2715` «이종 데이터 딕셔너리의 TypedDict 사용») · `/b2`(code) | L109 «외부 API, JSON 등 이종 데이터를 담는 딕셔너리에는 TypedDict를 사용하라.» + 펜스 L112~L123(`NutritionInfo`/`RecipeNutrition`) — 검증·`TypeAdapter`·`JsonValue`·`Literal` 판별 언급 0 | 산문 1줄 + 펜스 |
| ③ | `dddjango/skills/architecture-ddd/references/final.md:1618` (§5.5 «대규모 구조 (Large-Scale Structure)» L1568 · graph-owned 마커 L1569 · «지식 수준(Knowledge Level) 패턴» 예시 `FormInstance`) | `…/architecture-ddd/references/final.md/s040-5.5/b10`(kind-code) | `values: dict[str, Any] = field(default_factory=dict)` + L1620 `def set_field(self, field_name: str, value: Any)` | 펜스 |
| ④ 전수 | 코퍼스(`skills/*/SKILL.md`·`*/references/final.md`·`agents/*.md`·`commands/dddjango.md`)에서 `(dict\|Dict\|Mapping\|MutableMapping)[…, object\|Any]` | — | **2줄뿐**: 산문 = ①(SKILL.md:76 · `dict[str, Any]`·`Mapping[str, object]` 같은 줄) · 펜스 = ③(1618). `Dict[str, Any]`·`MutableMapping[…]`·`Mapping[str, Any]` 0 | — |
| ⑤ | `TypedDict` 언급: implementation-python:106·109(산문)·116·117·121(펜스) · `model_validate`: implementation-python:1509(펜스 · pydantic v1→v2 이전표) · **`TypeAdapter`·`JsonValue`·`RootModel` 0** | — | S-4 결정표가 요구하는 도구 3종은 코퍼스에 없다 | — |
| ⑥ | `dddjango/commands/dddjango.md:108` R-0284 (rev3 `@2026-09-04`) | `…/commands/dddjango.md/s007/b6` · `statesNorm R-0283~R-0287` | «… 감사 호출 입력에 `check-layer-skeleton`(registry #4)의 ⓓ 후보 채널 출력(…)과 `check-public-surface-annotation`(registry #11)의 ⓓ 후보(#645 — 변수·제네릭 안의 명시 `Any` · 해당 범위 실행분)를 동봉한다. …» | 산문 |
| ⑥ | `dddjango/commands/dddjango.md:133` R-0345 (rev2 `@2026-09-04`) | `…/commands/dddjango.md/s007/b28` · `statesNorm R-0345` | «11. `${CLAUDE_PLUGIN_ROOT}/scripts/check-public-surface-annotation.py` — 타입 전면(#493 …)·명시 `Any`(#645 — 시그니처는 차단·변수/제네릭 안은 ⓓ 후보)·Thin Read 반환(#358)·계약 검증 토큰(#456).» | 산문 |

`#645` 를 문면에 쓰는 좌표는 위 3곳(SKILL.md:76 · dddjango.md:108 · :133)이 전부다(에이전트 md 0).

**새 규칙(#647·S-4a)과 모순되어 개정해야 할 목록**
- 산문: ① SKILL.md:76 의 «JSON 문서는 `Mapping[str, object]`»(R-3448) · 같은 줄의 «경계 입력(JSON…)은 `object` … 로 받아 받는 즉시 좁힌다»(R-3448 본문 — S-4a «`object`로 흘리지 않는다»와 정면) · «프레임워크 오버라이드 … 우리 쪽 선언은 `object`»(R-3447 — `dict[str, object]` 처방을 함의 · #647 위반) · «변수·제네릭 안의 `Any` 는 ⓓ 후보(#645)»(R-3447 — `dict[str, Any]` 가 위반으로 승격되면 거짓). ⑥ dddjango.md:108 «ⓓ 후보(#645 — 변수·제네릭 안의 명시 `Any`)»(R-0284) · :133 «#645 — … 변수/제네릭 안은 ⓓ 후보»(R-0345).
- 펜스: ③ architecture-ddd:1618(+1620 `value: Any`) · ② implementation-python §1.5 펜스는 모순은 아니나 검증 없는 `TypedDict` 만 보여 준다(S-4b ⑴ 「외부는 검증」 부재).
- 좌표 정정: 보고자 «architecture-ddd:1614»(L204) → 실제 **1618**(결정 기록은 이미 1618).

## ⑤ 픽스처 충돌

`grep -rnE --include='*.py' '(dict|Dict|Mapping|MutableMapping)\[[^]]*, *(object|Any)\]' workspace/eval/fixtures` → 4줄(`fixture_hits.txt`) · 시제품도 같은 4줄(`proto_fixtures.jsonl`):

| 픽스처 | file:line | 자리/위치 | 원문 | #647 영향 |
|---|---|---|---|---|
| `public_surface/good` (check-public-surface-annotation · `workspace/tools/fixture_matrix.py:44` · 기대 exit **0**) | `…/admin/order/form/order_form.py:9` | sig-return · nested(`TypeIs[Mapping[str, object]]`) | `def _is_mapping(value: object) -> TypeIs[Mapping[str, object]]:` 독스트링 «경계 입력은 `object` 로 받아 받는 즉시 좁힌다(R-3448)» | **red** |
| 〃 | `order_form.py:20` | sig-return · top | `def clean(self) -> dict[str, object]:` (Django `Form.clean` 오버라이드) | **red** |
| 〃 | `order_form.py:21` | variable · top | `cleaned: dict[str, object] = dict(super().clean() or {})` | **red** |
| `public_surface/bad_rules` (기대 exit 2) | `…/place_order/any_signature.py:41` | variable · top | `y: dict[str, Any] = {}` (현재 #645 ⓓ 후보 «nested») | red 유지(위반으로 승격 · 메시지 변경) |

→ #647 도입 시 `make verify`(`verify-base-*` 의 `fixture_matrix` good=0)가 **깨진다**. good 픽스처 3줄은 R-3448 을 시연하려고 쓴 것이라 «정리»가 아니라 규칙 충돌 그 자체다(⑧-2·3 참조 — `clean()` 줄은 대체 주석이 없다).

## ⑥ #647 · json.load 시제품 결과 · 오탐

시제품 `proto_647.py`(evidence/S4 사본): 대상 선별은 검사기 `_is_target_file` 그대로(SKIP_DIRS·migrations·scaffold·`test_*`/`conftest`·`test/` 아래는 `factories/`·`fake/` 만 · 숨김 디렉터리 제외 · **루트 필터 없음** — `scripts/`·`docs/`·`web/` 의 .py 도 대상). 자리 = 시그니처(인자·`*args/**kwargs`·반환)·AnnAssign 변수·ClassDef 직계 AnnAssign(클래스 속성). 위치 = 최상위(주석 루트) vs 중첩(`list[…]`·`Optional`·`X | None`·`TypeIs[…]`·`Callable` 안). 컨테이너·`Any` 는 모듈 수준 import 바인딩으로 해소(`typing.Mapping`·`collections.abc.Mapping`·`import typing as t; t.Mapping`·`Mapping as _Mapping`), `object` 는 builtins 이름. 문자열 주석은 `_unstring` 판형으로 재파싱(중첩 문자열 포함). `from __future__ import annotations` 는 AST 가 이미 표현식이라 무관(기록만 — spring 히트의 1,014/1,061 이 future 파일 · kkebi 230/759). 줄 좌표는 #645 와 같은 def 줄(`line`) + 인자 자신의 줄(`own_line`).

| | c20f525 | spring HEAD | kkebi |
|---|---|---|---|
| exact 히트 / 줄(def 기준) | 1,076 / 863 | 1,061 / 848 | 759 / 723 |
| 자리 sig-param / sig-return / variable / class-attr | 419 / 278 / 334 / **45** | 418 / 272 / 327 / 44 | 245 / 120 / 327 / 67 |
| 위치 top / nested | 706 / 370 | 693 / 368 | 569 / 190 |
| 값 object / Any | 404 / 672 | 395 / 666 | **599 / 160** |
| 컨테이너 dict / Mapping | 695 / 381 | 679 / 382 | 571 / 188 |
| union-값 변종(`dict[str, object \| None]` 류) | 0 | 0 | 0 |
| `*args/**kwargs` 에 `dict[…]` 주석 | 0 | 0 | 0 |
| `Mapping[str, object]` top 매개변수 | 34 | 34 | 69 |

BC별(줄 · HEAD): rag 557 · fortune_reading 53 · llm_access 38 · chat_relay 36 · fortune_character 28 · fortune_calculation 24 · fortune_record 18 · promotion 16 · fortune_catalog 13 · scripts 12 · product 10 · query_translation 9 · fortune_intent 8 · service_policy 8 · media_library 6 · spring_dream_server 5 · wallet 3 · notification 2 · accounts 1 · docs 1. kkebi: **scripts 206** · billing 147 · **web 111** · saju 74 · product_observability 49 · tarot 47 · identity 33 · notification 18 · share 17 · daily 12 · top3 3 · image 2 · review 1 · fabfile/framework/kkebi_server 각 1. (자리별 표는 `proto_*.out`.)

grep 대 시제품 차분(`analyze.py` · c20f525 framework+application): grep 1,110 · 시제품 1,228(own_line∪line) · **grep에만 113** = `cast("dict[str, object]", …)` 문자열 103 + 별칭/다중 행 표현식 10(`"dict[str, Any]",` 같은 cast 인자 행·`Mapping[str, object],` 단독 행) · 시제품에만 231 = `test/fake`·`factories`(검사기는 대상 · grep -v /test/ 는 제외) + 다중 행 시그니처의 def 줄. kkebi: grep 431 · 시제품 466 · grep에만 16(cast 12).

**오탐·정당 자리 분석**
- `**kwargs: object`/`Any` — 무발화 확인(sig-star 히트 0). 분포: spring `Any` 11·`object` 10 · kkebi `object` 27·`Any` 23(비테스트) — `**kwargs: Any` 는 이미 #645 bare 위반.
- `Mapping[str, object]` 최상위 매개변수 = **전부 좁히기/검증 도우미**(R-3448 취지 자리): spring 34 — `_require_exact_keys`·`_validate_core_four`·`_validate_request_value`·`_freeze_object`·`_normalize(raw)`·`rehydrate(request_payload)`·`is_widget_item(item)`·`create(structure)` 등(`analyze_spring_head.out`); kkebi 69 — `classify_*`·`map_*`·`_require*`·`_reject_unknown(record)`·`__init__(wire)` 등. #647 은 이 자리를 예외 없이 위반으로 낸다.
- 프레임워크 오버라이드: `clean() -> dict[str, Any]` **spring 15 · kkebi 7**(6 `Any`+1 `object` · web/ 2 포함) · Protocol `__call__ -> dict[str, object]` 5(spring) · `deconstruct` 1(kkebi). mypy 탐침(`probe.py`·`mypy_probe_result.txt` · django-stubs 포함 venv): `clean() -> Cleaned(TypedDict)` **[override] 오류** · `-> Mapping[str, object]` **[override] 오류** · `-> dict[str, object]` 통과(#647 위반) · `-> dict[str, JsonValue]` 통과(의미 불일치 — cleaned_data 는 모델·date 등).
- TypedDict 호환: `TypedDict → Mapping[str, object]` 통과 · `→ dict[str, object]` **arg-type 오류** · `→ JsonValue` **arg-type 오류** · `json.loads(...)` 를 `-> TypedDict` 로 반환 **no-any-return**(strict).
- 직렬화 계열 함수(`dumps/serial/to_json/canonical/digest/payload/encode` 이름) 시그니처 히트 spring 31 · kkebi 13 — 결정표 «임의 JSON 통과→`JsonValue`» 행으로 옮길 후보(위반 판정 자체는 정당).
- 조회표(키가 데이터) 프록시: top 히트 중 라벨이 `by_/index/map/registry/table/lookup/…` 인 것 spring 21/693(3%) · kkebi 11/569(1%) — 대부분은 레코드형(키 고정)이라 «`dict[K, TypedDict]`» 행보다 «레코드→TypedDict» 행이 지배적. 단 P1 근원인 dataclass 필드(class-attr)는 4~9% 뿐이고 대다수가 함수 매개변수/반환이다.
- 검출 한계(무발화): `cast("dict[str, object]", …)` 문자열(spring 103줄 · kkebi 12) · `X = dict[str, Any]`/`type X = …` 별칭 대입(Assign — AnnAssign 아님) · 별칭 이름을 통한 간접 사용.

**json.load(s) ⓓ 후보(F)** — 소비자 분류(`analyze_*.out`):
- spring(양 시점 동일) 95 호출 → 후보 **95(100%)** · 직접 파서 인자 0. 분포: assign 45 · ListComp 21(`[json.loads(line) for line …]`) · assign `[dict[str, Any]]` 6 · assign+다음 줄 이름 있는 호출 6 · GeneratorExp 4 · subscript 4 · assign `[Mapping[str, str]]` 3 · assign `[object]` 2 · assign+다음 줄 isinstance 1. 표본 10: `chat_relay/…/turn_controller.py:123` `body: object = json.loads(request.body)` · `fortune_calculation/…/lunisolar_calendar/packaged_table_adapter.py:48` `manifest: Mapping[str, str] = json.loads(…)` · `:50` `payload: dict[str, Any] = json.loads(raw)` · `place_directory/packaged_table_adapter.py:88·90` 같은 꼴 · `regenerate_place_tables.py:103` `document: Any = json.loads(…)` · `:254` `payload: dict[str, Any] = …` · `solar_term_calendar/packaged_table_adapter.py:53` · `:55` `payload: dict[str, list[dict[str, str]]] = json.loads(raw)` · `turn_controller.py:346` `body: object = …`.
- HEAD 의 실제 «검증 파싱» 형상은 오라클과 다르다: `ontology_canonical.py:35 load_json_object(path) -> dict[str, Any]`(안에서 `json.loads` + `isinstance(value, dict)` 가드) → 소비처에서 **하위 키**를 `_CONTENT_DIGEST_REF.validate_python(descriptor["ontology_release_ref"], strict=True)`(`service_runtime.py:345~346·380·662`). 즉 json.load 결과 «전체»가 파서로 직접 들어가는 자리는 0 이고, 검증은 문서의 부분에 걸린다 — (b) 오라클로는 정당 형상이 100% 후보다.
- kkebi 60 → 후보 59. 지배 형상 = **`x: object = json.loads(...)`(34) + 다음 줄 `isinstance`(5)/이름 있는 호출(3)** — R-3448 처방 그대로. `cast('list[object]', json.loads(…))` 5 · dict 리터럴 안 4 · 반환 2 · `_require_object(json.loads(…))` 1(유일한 비후보).
- 오탐 판정: 두 저장소 모두 «정당 사용»이 (b) 오라클에 잡힌다 — 후보 채널이라도 신호 대 잡음이 0 에 가깝다. 쓸모가 있으려면 오라클을 «대입 대상 주석이 `object`/`TypedDict`/`Mapping[str, str]` 등 구체 · 또는 다음 문에 파서/isinstance» 로 바꿔야 하고, 그러면 spring 은 대략 assign 45 중 `dict[str, Any]`·`Any` 주석 7 + ListComp 21 정도가 남는다(미실측 추정).

## ⑦ #645 중복 추정

현 검사기를 사본 루트에서 실행(`DJR_FINDINGS_JSON=$S/S4/findings_<사본>.jsonl python3 dddjango/scripts/check-public-surface-annotation.py $S/<사본>` · 루트 모양 `application/` 있어 사용 오류 없음 · exit 2): spring HEAD blocker 3,292(#493 3,216 · #645 76) · ⓓ 805(#645 708 레코드 = 569 줄 · #69 97); kkebi blocker 294(#645 121) · ⓓ 557(#645 385 = 379 줄); c20f525 #645 ⓓ 714(575 줄).

시제품과 def-줄 기준 교집합: **spring HEAD — #647 `Any` 줄 518 중 518(100%)이 이미 #645 ⓓ 후보 · `object` 줄 335 는 #645 무관 · #645 bare 위반과 같은 줄 14**. kkebi — `Any` 157/157(100%) · `object` 568 · 위반 동거 24. c20f525 — 524/524 · 344 · 15.
→ #647 을 #645 와 독립으로 얹으면 `[…, Any]` 줄은 **전부 두 번**(ⓓ #645 + blocker #647) 인쇄되고, R-0284 «ⓓ 후보(#645) 동봉» 목록에 blocker 가 섞인다. `_check_explicit_any` 의 AnnAssign/nested 분기에서 #647 판정을 먼저 하고 #645 후보를 억제하는 식의 배타 처리가 필요하다.

## ⑧ 확정 방향(§2-C)과 어긋나는 사실

1. **R 번호**: «JSON 문서는 `Mapping[str, object]`» 문장과 «경계 입력은 `object`로 받아 즉시 좁힌다»는 **R-3448**(Obligation)의 것이다(`discipline-houserules-skill.ttl:699~701` prefLabel). §2-C-1 «R-3447 rev2 로 삭제·대체»는 대상이 어긋난다 — R-3448 개정(또는 폐기)이 필요하고, 두 규범이 한 블록(`s007-4/b7`)을 공유하므로 R-3447 본문(«우리 쪽 선언은 `object`» · «변수·제네릭 안의 `Any` 는 ⓓ 후보(#645)»)도 같은 렌더에서 거짓이 된다.
2. **Django `Form.clean()` 오버라이드에는 #647·mypy 를 동시에 만족하는 주석이 없다**: TypedDict 반환·`Mapping[str, object]` 반환 = `[override]`(탐침) · `dict[str, object|Any]` = #647 위반. 남는 것은 `dict[str, 구체 union]`/`dict[str, JsonValue]` 뿐(의미 불일치). 실코드 spring 15 · kkebi 7 · 픽스처 good 1.
3. **good 픽스처 red**: `public_surface/good/…/order_form.py:9·20·21` 이 #647 로 red → `fixture_matrix` good=0 계약이 깨져 `make verify` 가 red. 이 파일은 R-3448 시연용이라 «정리»가 아니라 규칙 충돌이며, :20 은 2 때문에 대체 주석이 없다.
4. **TypedDict ↔ JsonValue 비호환**: TypedDict 는 `dict[str, object]`·`JsonValue` 자리에 못 들어간다(탐침 arg-type 2건). HEAD 는 `to_json_value(value: object) -> JsonValue` 브리지로 풀었다 — 결정표 «레코드→TypedDict»와 «직렬화 경계→JsonValue»는 `object` 매개변수 브리지 없이는 합성되지 않고, 그 브리지는 같은 표의 «자리표시 `object` 금지»와 충돌한다.
5. **«내부 JSON은 검증 없이 TypedDict»**: 파일에서 `json.load` 한 내부 JSON 을 `-> TypedDict` 로 반환하면 strict `no-any-return`(탐침). HEAD 도 `load_json_object -> dict[str, Any]`(#647 위반 형상)로 받고 하위 레코드만 `TypeAdapter` 로 검증한다 — 규칙대로 하려면 내부 JSON 도 `TypeAdapter`/`cast` 가 필요하다.
6. **R-3448 형상이 kkebi 의 지배 패턴**: `json.loads` → `x: object`(34/60) + isinstance · `Mapping[str, object]` 도우미 매개변수 69 · 값 `object` 417 : `Any` 157. S-4a «받은 뒤 `object`로 흘리지 않는다»는 현행 권장 패턴을 일괄 위반으로 재분류한다. 그런데 #647(Subscript 만)은 `x: object` 를 보지 않는다 — 문면은 금지·검사기는 침묵으로 갈린다.
7. **`Mapping[str, object]` 정당 자리 n건**: 최상위 매개변수 spring 34 · kkebi 69 가 전부 좁히기·검증 도우미다. 보고자 «오탐이 거의 없다»(S-4f)는 «`dict[str, Any]` 레코드»에는 맞지만 `Mapping[str, object]` 경계 입력에는 맞지 않는다 — «무조건 금지»면 이 103 자리에 대체 주석(TypedDict 는 검증 전 값에 못 붙임)이 없다.
8. **#645 이중 보고 100%**(⑦) — 배타 처리 없이는 출력·감사 입력 계약(R-0284)이 흔들린다.
9. **json.load ⓓ 후보 (b) 는 양 저장소에서 정당 형상을 100%/98% 잡는다**(⑥) — 후보 채널이라도 오라클 재설계 없이는 감수자 잡음이다.
10. **legacy 격리 규모가 보고보다 크다**: 발주측 상환은 주석 줄을 12 줄만 줄였고(1,110→1,098 · 대장 «822 는 S-4 검사기 뒤 별도 발주»), 검사기 대상은 grep 보다 넓다(spring 시제품 1,213 줄 · kkebi 723 줄 — `scripts/` 206·`web/` 111 포함). 앵커 차분 `_normalize`(`registry_gate.py:145` · `_LINENO_RE=r":\d+"`→`:N` · 경로 유지)는 legacy 파일의 함수 이름 변경·파일 이동·메시지 문구 변경을 전부 귀속으로 낸다.
11. **§2-C-2 «예시 정정»의 소유**: architecture-ddd:1618 은 graph-owned 절(§5.5 마커 L1569 · 블록 `s040-5.5/b10` kind-code) · implementation-python §1.5 도 graph-owned(`s007-1.5/b1·b2` · R-2715) — md 직접 수정이 아니라 ttl 개정+재투영 대상이다(결정 기록에 소유 표기 없음).
12. **kkebi `web/`(111줄)·`scripts/`(206줄)**: 검사기에 루트 필터가 없어 dddjango-web 영역과 운영 스크립트가 #647 대상에 든다 — 자매 플러그인 경계와 «BC 산출물만»이라는 보고 취지가 어긋난다.
13. **훅 범위 표기**: 보고서 «훅 범위 124건»은 실제 pre-commit 훅(`spring_dream_server framework`)이 아니라 대장 검증 명령(`application framework spring_dream_server`) 기준이다(수치 자체는 정확).

## ⑨ 사각 · 불확실

- mypy 는 실서고 venv(3.14.7 · mypy 2.3.1)를 cwd=사본에서 썼다 — django-stubs settings 가 사본에서 해소됐는지 미확인(결과 일치로 대체). kkebi mypy 는 과제 밖이라 미실행.
- registry_gate 앵커 차분은 실행하지 않았다(사본에서 `--anchor` 런 없음) — S-4h 는 `_normalize` 판독으로만 본 것.
- 시제품은 검사기 #645 판형을 모사했지 검사기 코드에 끼우지 않았다(중복 억제 방식은 제안일 뿐). `_module_bindings` 와 달리 시제품은 출처 모듈을 유지하므로 검사기에 넣을 때 바인딩 함수를 따로 둬야 한다.
- json.load 오라클 재설계 뒤의 후보 수(⑥ 끝 «추정»)는 미실측.
- 조회표 비율은 라벨 이름 프록시(1~3%)라 하한 추정이다.
- 검사기가 사본 `.dddjango/violations/` 에 레코드를 썼다(사본 안 · 실서고·dddjango 저장소 무변).

Serena: skipped — 워크트리에 `.serena/project.yml` 없음.
