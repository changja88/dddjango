# 현장 보고 3 · ① 문제 리뷰 — 리뷰어 A(기술 축 — 검사기·실행기·코드 형상) · 2026-09-04

- 대상: `workspace/plan/2026-09-04-field-report-repair-3-issues.md` §2-A~§2-D 와 각 «수정 1»(⓪ 뒤 조정 방향). 증거 `workspace/eval/field-report-3/evidence/{S1,S4,S5,map}/`.
- 재실행 산출: `$S/rv1A/`(`$S=/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3`). 실서고 무접촉(사본 5 + spring venv mypy · cwd=사본). 사본 `$S/spring` 에 내가 만든 `rv1a_probe/` 는 실행 뒤 `$S/rv1A/rv1a_probe_mypy/` 로 옮겼다(다른 리뷰어 런 오염 방지).
- 성격: 적대 리뷰. «확정 방향과 어긋나는 사실»은 ⓐ 규칙에 따라 브리프 사유로 표시한다(§3).

## 1. 판정 표

| # | 항목 | 판정 | 핵심 근거(상세 §2) |
|---|---|---|---|
| A-1 | S-1-3 #646 세 통과·두 위반의 결정적 구현 | 검증됨(조건) | AST 만으로 결정적 — 단 `_module_bindings` 는 출처 모듈을 버려 정본 경로 대조 불가 → #645 `_any_bindings` 선례처럼 **별도 바인딩 워커** 필요(§2.1) |
| A-2 | S-1-3 타 모듈 import 별칭 fail-open | **MAJOR** | ⓐ 무발화는 mypy 가 사용처 헤더에서 `[type-arg]` 를 내므로 무해하나, 시제품은 **ⓑ(헤더 ignore)까지 같이 침묵** — 공유 별칭 모듈 + 사용처 헤더 `# type: ignore[type-arg]` = mypy 통과·#646 침묵의 완전 사각(§2.2 synth 실측). ⓑ 헤더 판정을 기저 해소와 **독립**시켜야 한다 |
| A-3 | S-1-3 여러 줄 헤더 | 검증됨 | 기저 표현 줄의 ignore 를 헤더 범위(class 줄~`:` 줄)가 덮는다(synth E14 + 내 케이스) · mypy 가 진단을 내는 줄 = 기저 표현 줄 ⊂ 헤더 범위 |
| A-4 | S-1-3 naming/bad_rules 3클래스 → 등재 vs 정정 | 검증됨(⓪ 정정) | **둘 다 불요** — `checker_cross_matrix.lanes()` 는 `good` 만 돌리고(`workspace/tools/checker_cross_matrix.py:56~60`), `bad_rules` 는 자기 검사기만(`fixture_matrix.py:114~136`·`findings_count_matrix.py:80~81`). ⓪ S1 ⑦-9 «EXPECTED 미등재 쌍 red» 는 오류 |
| A-5 | S-1-3 기저 집합에 CBV | 검증됨 | 픽스처 46루트·양 저장소 CBV 적중 0(`proto_646 --include-cbv`) · 비용 = 이름 24 + 모듈 5 · `View`/`TemplateView`(default TypeVar) 제외로 오탐 0 |
| A-6 | S-1 «#493 개정»(§2-A 수정 1-4) 검출 집합 변화 | 검증됨 | 시제품 패치 before/after: spring HEAD 3,292→3,292 · d2eaafe 3,303→3,303 · kkebi 294→294 · 픽스처 4레인 무변 — **lost 0 · gained 0**(§2.3). 감소 방향이되 현장 감소분 0(레인이 전 필드를 이미 주석) · 다른 클래스로 새는 확대 0 · synth 5→0 으로 기능 확인 |
| A-7 | S-1-3 클래스당 1건·CBV 코퍼스 예시 | 검증됨 | ⓐ+ⓑ 동시 → 헤더 1건(ⓑ 문면)로 접는 구현은 단순(같은 ClassDef 노드) |
| A-8 | S-4-3 #647 결정성(자리·중첩·별칭·문자열) | 검증됨 | 자리(sig-param/sig-return/variable/class-attr)·위치(top/nested)·값(Any/object) 매트릭스 실측(§2.4) · good 픽스처 `order_form.py:9·20·21` → **차단 0 · exit 0** ✓ · bad `any_signature.py:41` → 차단 승격 ✓ |
| A-9 | S-4-3 면제 목록(Form.clean · TypeIs) | MINOR | 불완전 — kkebi `PaymentOrderModel…deconstruct -> tuple[str, Sequence[Any], dict[str, Any]]`(스텁이 `Any` 고정 · `object` 로 바꿔도 nested 반환 차단) · spring `_ProviderResponse.model_dump -> Mapping[str, object]` Protocol 2. «메서드 이름 × 기저 계열» 면제 표로 일반화 권고 · 기저 해소는 #646 별칭 워커 공용 가능(실측: spring/kkebi 폼 기저 전부 모듈 내 해소) |
| A-10 | S-4-3 #645 배타 구현 지점 | 검증됨 | `_check_explicit_any`(:471~513) AnnAssign(:504)·nested(:497·:502) 분기 앞에서 #647 판정 → 같은 애너테이션에 #647 위반이면 #645 nested ⓓ 생략 · bare(:495·:500)는 독립 유지 |
| A-11 | S-4-4 json.load ⓓ 오라클(수정 1-4) | **MAJOR** | 문면 그대로면 «반환» 조건이 `-> object` 함수까지 잡는다(kkebi 후보 2/2 가 R-3448 정당형) · 구체 주석 무검증 대입(`manifest: Mapping[str, str] = json.loads(…)` spring 4)을 놓친다. refined 오라클(§2.5) 실측 spring 41/95 · kkebi 8/60 · 표본 정당형 0 |
| A-12 | S-5-2 ⓑ 철회 — #63 «같은 강도» | 검증됨 | #63 code-json = blocker exit 2 · 400/503 각 1건 정확 문면(`evidence/S5/check-openapi-…codejson…txt`) |
| A-13 | S-5-2 auto 사각을 플러그인이 메우는 방안 | **MAJOR** | §2-D 수정 1 은 «회신 3 안내»뿐 — Coordinator 문면(`commands/dddjango.md:119` «Error response와 무관한 G2는 … auto»)이 만든 사각을 발주측에 떠넘긴다. 처방 2안(§2.6): (a) `check-openapi-error-declaration.py` **tree 슬라이스(#63 · 프로필 무관)** 에 base 뭉뚱그림 판정 이식(같은 소유자 · AST 만) (b) Coordinator 문면 «`response=` 에 4xx/5xx 를 선언한 컨트롤러가 슬라이스에 있으면 code-json 렌더» |
| A-14 | S-5-2 ⓐ·ⓒ 자리·바인딩 | 검증됨(조건) | `_slice_check_controller_ast` 는 `api/**/*.py` 전 파일(schema_out.py 포함)+OHS `*_service.py` · `main:7355` 무조건 호출(프로필 무관) ✓ · 단 바인딩은 `domain_names` 뿐(:7133~7137) → `_Schema`·`_RootModel`·`from ninja import Status` 해소용 origin 워커 추가 필요 |
| A-15 | S-5-3 ⓒ 충돌 | 검증됨 | 검사기 27종 `RootModel` 언급 0 · `Schema` 기저 판정은 error-centralization(`NINJA_SCHEMA` :75 — ErrorSchema 전용)·public-surface(선언적 면제 — RootModel 미등재이나 본문 필드 없어 무영향) · response-schema-bypass 는 기저 미검사 → 충돌 0. ⓒ 를 `schema_out.py` 로 한정할 이유 없음(메타클래스 충돌은 파일 무관) |
| A-16 | S-5-3 openapi stale 문면 범위 | 검증됨 | 필수 2: `:6` docstring · `:3362` 조치 문장 · 권장 1: `:3371` 주석 · 보류 2: `:3358` BLOCKER 헤더·`:3477` tree 메시지(`<Bc>ErrorSchema` 계열 표기 — :3477 변경은 발화 라인 변경 → findings_count EXPECTED 재생성) |
| A-17 | MAP-1 섹션 말미 추가 좌표 `s080-17` | **MAJOR** | **좌표 충돌** — `s080-17` 은 이미 «## 17. Django 5.x 새 기능»(prose · `ontology/LEDGER.tsv` 등재). 헤딩 93개 뒤 말미 새 절은 **`s094-18`**(«참고 자료» 뒤) · 9ef6c4f 레시피 자체는 doc 무관하게 동작(`ontology_render.graph_sections` 가 manifest 경로별) · «참고 자료 뒤 §18» 배치는 부자연 → `s038-7` 블록 append 우선 검토 |
| A-18 | MAP-1 registry_gate 앵커 차분 legacy 격리 | 검증됨 | `registry_gate.py $S/spring --anchor d2eaafe` 68s · legacy 잔존 2,676 격리 · 귀속 1 = ⓪ 조사자가 사본에 남긴 `mp_probe_s1/alias_inlines.py`(오염 · §3) |
| A-19 | MAP-1 두 조각 → EXPECTED 2회 | MINOR | public-surface 가 두 조각에 걸려 2회 불가피 · 대안 분할(조각 1 = S-1+S-4 · 조각 2 = S-5)이면 검사기 파일당 1회 |
| A-20 | 영향 목록(빠진 표면) | MINOR | `gen_pregate_symbol_kinds` **ROSTER 행 2**(#646 기저 집합 · #649 Schema/RootModel — 닫힌 세계 «베이스 판정 재료 전수» 주장 유지 · 도구는 새 `.bases` 판정 자리를 자동 감지하지 않음 `:395~446`) · findings_count 메시지 해시 · `registry_gate_smoke` P0′ 는 `skeleton/good_bc` 에 신규 형상 0 → 무영향(실행 확인만) · Codex SKILL.md hand 미러 |
| A-21 | 정본 예시 mypy 형상(S-1) | MINOR | django-stubs `options.pyi:108·178` — `list_display` 는 **ClassVar 아님**(의도적) · `readonly_fields`/`search_fields`/`inlines` 는 ClassVar(:122·:185·:194). 내 probe: `list_display: ClassVar[…]` → `[misc]` red. 현장(spring/kkebi 47·45·44)은 정확히 그 모양. ② 정본 예시는 mypy 로 검증하고 이 구분을 문면에 고정 |

## 2. 항목별 상세

### 2.1 #646 결정성 — 바인딩 판형 (A-1)

- `check-public-surface-annotation.py:152~188 _module_bindings` 는 `{로컬 이름: 원명}` 만 남긴다(`from x import A as B` → `B: A` · `import a.b as c` → `c: a.b`). #646 은 «정본 dotted 경로»(`django.forms.ModelForm` · `django.contrib.admin.ModelAdmin` · CBV 5모듈) 대조가 오탐 0 의 근거(parler `TranslatableAdmin` 무발화 · E10/E11)라 출처 모듈이 필요 → `_any_bindings`(:350~395)가 같은 이유로 따로 선 선례 그대로 **`_origin_bindings`**(proto `module_bindings` 판형 · if/try 하위 · 그림자 pop)를 신설한다.
- 별칭 값·TYPE_CHECKING 중간 ClassDef 추적은 #493 개정(§2.3)과 #647 `Form.clean` 면제(§2.4)에도 필요 → **공용 `_alias_values(mod)`** 하나(값이 Name/Attribute/Subscript 인 모듈 수준 Assign/AnnAssign + TYPE_CHECKING 분기 ClassDef 첫 기저 · depth≤4). 내 시제품 패치 `$S/rv1A/patch493.py` 가 그 판형이다.
- 시제품 dead code: `proto_646.py:319 cand-alias-unresolved` 는 `classify_base`(:193~224)가 `alias-unresolved` shape 를 만들지 않아 **절대 방출되지 않는다**(import 된 이름은 `resolve_path` → `canonical None`·`lenient None` → `return None`). ⓪ 문면 «후보 = 별칭 미해소(import 된 이름)»(:10)은 구현과 다르다.

### 2.2 타 모듈 별칭 fail-open 의 실제 위험 (A-2 · MAJOR)

synth `$S/rv1A/synth646/…/admin/{_bases.py,panel.py}` 를 `proto_646.py` 에 넣은 결과:

```
violation-a    panel.py:7  MultiLineIgnoreOnBaseLine   맨몸 상속 admin.ModelAdmin (bare)     ← 여러 줄 헤더 기저 줄 ignore
violation-b-header panel.py:7 MultiLineIgnoreOnBaseLine 헤더 7-9 `# type: ignore[type-arg]`
violation-b-attr panel.py:24 LocalBareIgnoreOnAttr      속성 `inlines` 줄 ignore
(무발화) MethodSigIgnore(_ModelAdminBase)            ← 타 모듈 별칭 · save_model 시그니처 줄 ignore
(무발화) ImportedAliasHeaderIgnore(_ModelAdminBase)  # type: ignore[type-arg]   ← ★ 헤더 ignore 인데 침묵
(무발화) LocalBareIgnoreOnAttr.get_form(...) -> type[forms.ModelForm]  # type: ignore[type-arg]  ← 메서드 시그니처 줄
```

mypy 실측(`$S/rv1A/rv1a_probe_mypy/` · spring venv · cwd=사본): 공유 모듈의 맨몸 별칭 `_ModelAdminBase = admin.ModelAdmin  # type: ignore[type-arg]` 는 **`[unused-ignore]`** 이고 `[type-arg]` 는 **사용처 클래스 헤더**(`panel_shared.py:7·13`)에 난다. 즉 레인이 별칭을 `_bases.py` 로 모으고 mypy 를 잠재우려면 ignore 는 사용처 헤더에 붙게 되는데, 시제품은 기저 미해소 클래스를 통째로 건너뛰어 ⓑ 도 못 본다. 처방: ⓑ 헤더 판정은 **모든 ClassDef** 에 적용(기저 해소 무관 — `# type: ignore[type-arg]` 가 클래스 헤더에 있는 것 자체가 은폐) · 기저가 집합 밖/미해소면 문면만 «기저 미해소 — django-stubs 제네릭이면 위반» 로 낸다(위반 유지 · 오탐 후보는 서드파티 제네릭에 한정되며 그것도 은폐다). ⓐ 의 타 모듈 무발화는 mypy 의존이라 docstring 검출 한계로 남긴다.

메서드 시그니처 줄·모듈 수준 별칭 정의 줄의 `[type-arg]`(현장: kkebi `catalog_controller.py:101 Query(None)` 1) 는 결정 범위 밖 — ⓓ 후보 채널(«이 ignore 가 django-stubs 제네릭 은폐인가»)로 두면 결정성 손실 없이 사각을 줄인다.

### 2.3 #493 개정 before/after (A-6)

- 패치: `$S/rv1A/patch493.py` → `$S/rv1A/ps493/check-public-surface-annotation.py`(`_is_declarative_class` 만 교체 — Subscript 벗김 + `_alias_values` 추적).
- 실행(`[#…]` blocker 라인 sort → comm · `mp_probe_s1` 제외):

| 대상 | before | after | lost | gained |
|---|---|---|---|---|
| spring HEAD 7bfe1aa | 3,292 | 3,292 | 0 | 0 |
| spring d2eaafe | 3,303 | 3,303 | 0 | 0 |
| kkebi 6608fb0 | 294 | 294 | 0 | 0 |
| public_surface/good · bad_rules | 0 · 20 | 0 · 20 | 0 | 0 |
| naming/bad_rules | 4 | 4 | 0 | 0 |

- 해석: «줄어드는 방향»은 맞지만 **현장 감소분 0** — spring 별칭 22·kkebi 별칭 31+TC 15 클래스가 전부 필드를 주석하고 있다(발주측 `1288e4a` 메시지 «#493 첫 대입 주석 동일 커밋 처리»가 비용을 이미 치른 증거 · kkebi `list_display: tuple[str, ...]` 47). 따라서 개정은 소급 변화 0 · «Config/Meta 밖 클래스로 새는» 확대도 0(양 저장소·픽스처). 기능은 synth(`$S/rv1A/synth493/` — Subscript·TypeAlias·TC ClassDef 기저 아래 맨몸 `list_display`)에서 5→0 으로 확인.
- 무손실 증명 방식(⑤ 구현 리뷰용): 위 6 대상 before/after comm = ∅ 를 그대로 재실행 기준으로 쓴다.

### 2.4 #647 «수정 1» 매트릭스 (A-8·A-9·A-10)

`$S/rv1A/proto_647_rev1.py`(evidence `proto_647.py` 스캔 재사용 · 판정만 수정 1 · 출력 `$S/rv1A/647-*.txt`):

| | spring HEAD | c20f525 | kkebi | fx good | fx bad |
|---|---|---|---|---|---|
| exact 히트 | 1,061 | 1,076 | 759 | 3 | 1 |
| 차단(값 Any) | 666 | 672 | 160 | 0 | 1 |
| 차단(값 object · 반환/속성) | 87 (69/18) | 90 (71/19) | 150 (91/59) | 0 | 0 |
| ⓓ(값 object · 매개변수/변수) | 308 | 314 | 448 | 1 | 0 |
| 면제(TypeIs · Form.clean) | 0 | 0 | 1 | 2 | 0 |
| 차단 줄(def 기준) / ⓓ 줄 | 600 / 267 | 609 / 273 | 304 / 436 | **0** / 1 | 1 / 0 |

- 자리 판별은 AST 부모(FunctionDef.args/returns · AnnAssign 부모가 ClassDef 인가)로 결정적. 문자열 주석은 `deep_unstring`, `Dict`/`typing.Mapping`/`collections.abc`/`import typing as t` 는 모듈 바인딩으로 해소(proto §6 검증). 중첩은 값 Any 전 위치 + 값 object 반환/속성 nested 포함으로 재현했다(spring nested object 반환 21 · kkebi 속성 nested 28 — 수정 1 문면은 위치를 안 적었으니 ② 에서 명시).
- `Form.clean` 잔존 차단 spring 15 · kkebi 6 은 전부 `-> dict[str, Any]`(수정 1-1 «object 로 바꾸면 통과» 대상 · legacy). 면제 기계는 `_alias_values` 로 spring `_ModelFormBase`·kkebi `forms.Form` 모두 해소됐다(면제 1 · 미해소 0).
- 값 object 차단 표본 10(정당해 보이는 자리 여부): `OutputItemIn.item: Mapping[str, object]`(LLM 출력 아이템 — 결정표 «임의 JSON→JsonValue» 행) · `TurnWireMapper.scaffold -> dict[str, object]`(wire 본문 — TypedDict/JsonValue) · `DjangoCharacterRepository._time_rule_to_columns -> dict[str, object]`(ORM kwargs — TypedDict `**` 언패킹 가능) · `SaveFortuneRecordCommand.response_json_structure: Mapping[str, object]`(JsonValue) · `_ProviderResponse.model_dump -> Mapping[str, object]`(SDK Protocol — A-9) · `service_runtime._load_release_documents -> Mapping[str, object]`(RAG legacy) · kkebi `FortuneCycle.to_wire`·`SelectedMajorCardSnapshot.to_payload -> dict[str, object]`(VO→wire — TypedDict) · `TarotShareSnapshot.spread_snapshot: dict[str, object]`(VO 필드) · `analytics_controller._schema_ref -> dict[str, object]`(OpenAPI ref — JsonValue). 10/10 이 결정표 행에 대체가 있다 — 단 `JsonValue` 별칭은 프로젝트에 정의가 있어야 하므로(spring 은 `framework/technology/rag/runtime/json_value.py` 신설로 풀었다) 문면이 «어디에 정의하는가»를 줘야 한다(B 축).
- #645 배타: 실측 이중 보고 100%(⓪ ⑦)는 `_check_explicit_any` 에서 #647 을 먼저 판정하고 «같은 애너테이션 노드에 #647 위반 → nested ⓓ 생략»으로 닫힌다. 유니온 `dict[str, Any] | Any` 는 #645 bare + #647 둘 다 남는다(서로 다른 슬롯 · 허용).

### 2.5 json.load ⓓ 오라클 (A-11 · MAJOR)

수정 1-4 문면(«결과가 `dict[str, Any]`류·`Any` 주석 변수 / 반환 / 컴프리헨션으로 감»)을 그대로 구현(`proto_647_rev1.py`): spring 32/95 · **kkebi 2/60 — 둘 다 `def …(…) -> object: return json.loads(…)`**(`scripts/import_legacy_saju/source_loader.py:631` · `seed_canonical_tarot_deck/extractor.py:52`) = R-3448 정당형. 또 `manifest: Mapping[str, str] = json.loads(…)`(spring `packaged_table_adapter.py:48·88`, `:53·:55`) 4건은 «검증 없는 구체 주석» 인데 놓친다.

refined 오라클(`$S/rv1A/jsonload_refined.py`): **후보 ⟺ AnnAssign 주석 ≠ `object` · Return(함수 반환 주석 ≠ `object`) · 컴프리헨션 요소 · 직접 Subscript/Attribute 접근 · 리터럴 컨테이너 요소** / 비후보 = `x: object = …` · 호출 인자·키워드(피호출자 시그니처가 #647 대상) · 무주석 Assign(#493 몫).

| | spring HEAD | kkebi |
|---|---|---|
| 호출 | 95 | 60 |
| 후보 | **41**(annassign 12 · comprehension 25 · direct-access 4) | **8**(literal-container 6 · annassign 2 `dict[str, object]`) |
| 비후보 | annassign object 2 · 무주석 52 | annassign object 42 · call-arg 6 · return object 2 |
| 표본 10 정당형 | 0 | 0(리터럴 컨테이너 6 은 사용처 미추적 — §5) |

메시지에 파서 후보(«`TypeAdapter(<TypedDict>).validate_python/json` 또는 `x: object` 뒤 즉시 좁힘»)를 싣고 R-0284 감사 입력 목록에 «json.load ⓓ 후보» 를 추가하면 감수자가 집행 가능한 형태가 된다.

### 2.6 S-5 (A-12~A-16)

- ⓑ 철회의 강도 동일성: `evidence/S5/check-openapi-error-declaration_codejson_spring-f5ee428.txt` — `[#63] …:137 wrong-response-schema … status 400는 … InvalidRequestErrorSchema 선언 필요 (현재 … FortuneReadingErrorSchema)` + 503 1건 · exit 2. 신설 ⓑ 와 동일 사건·동일 강도 ✓. 그 바로 아래 조치 문장(`:3362`)이 «base로 선언하고» 라 같은 출력 안에서 자기모순 — 필수 수리.
- auto 사각(A-13): `_run`(:6999~7005)은 `error_bcs` 없으면 `[]` — ⓑ 가 어디에 있든 code 레인이면 auto 에서 침묵. #63 의 tree 슬라이스(`_tree_slice63` :3438~ · «모든 프로필에서 돈다» :3371)는 현재 `openapi_extra`·override·monkeypatch 만 본다(`response=` 값 미검사 :3470~3487). 같은 소유자(#63) 안에서 «`response=` 값이 같은 BC `bc_error_schema.py` 안 하위 클래스를 가진 base» 를 tree 슬라이스에 두면 프로필 무관·AST 만·한 소유자 원칙 유지 — proto_ninja3 `build_hierarchy`(:172~186)가 그 판형(파일 안 상속 그래프 · `_constructed_error` 의 명시값 base 는 `field_values` 로 code 레인이 이미 구분하므로 tree 에선 «본문 `Status(<status>, Base(...))` 직접 생성»만 정당으로 인정 → 오탐은 anchor 앞 tree↔code overlap 키로 억제). 이걸 안 하면 최소한 Coordinator `:119` 문면을 «슬라이스에 `response=` 4xx/5xx 선언 컨트롤러가 있으면 code-json 렌더»로 고쳐야 «플러그인이 만든 사각»이 닫힌다.
- ⓐ·ⓒ 자리(A-14): `_tree_slice2`(:7203) → `api.rglob("*.py")`(:7260) 전 파일 + OHS `*_service.py`(:7272) 에 `_slice_check_controller_ast` — 운영 기준 f5ee428 `schema/schema_out.py:151` 도 방문한다. 신설 규칙은 `findings.add("#648"|"#649", where, msg)` + `finding_keys.append(None)`(overlap 비대상). 바인딩: 현재 :7133~7137 은 `domain_layer` import 이름만 모은다 → `from ninja import Schema as _Schema` · `from pydantic import RootModel as _RootModel`(f5ee428 schema_out.py:5~10) · `from ninja import Status`(controller:2) 해소용 origin 워커(모듈 수준 Import/ImportFrom → dotted · 상대 import 불요) 추가.
- ⓐ 판정: `FunctionDef.returns` 평탄화(`|`·`Union`·`Optional`·문자열) → `Subscript.value` origin ∈ {`ninja.Status`, `ninja.responses.Status`} 계수 ≥2. 라우트 데코 유무 무관(테스트 AnnAssign 3 은 api/ 밖이라 대상 밖). 현장 legacy 13(spring 7 · kkebi 6) → 앵커 격리.
- ⓒ 판정: `ClassDef.bases`(Subscript 는 `.value`) origin 이 `ninja.Schema`∧`pydantic.RootModel` — `schema_out.py` 한정 불필요(A-15).
- 픽스처 현황: `api_error_controller/good/…/order_controller.py` 는 반환 주석 자체가 없다(`def get_order(self, order_id: str):`) — ⓐ good 예(`-> Status[Out | Err]`)·ⓒ good 예(`RootModel[Annotated[…]]` 단독)·bad 각 1 을 신설 파일로 넣는다(기존 파일 무변 → #493 cross 계수 무변).

### 2.7 MAP-1 (A-17~A-20)

- 섹션 키 = `s{헤딩 서수:03d}-{번호}`(`ontology_census.py:101~103`). implementation-django-final 헤딩 93개(펜스 밖): 80 `## 17. Django 5.x 새 기능`(:1730) … 87 `#### Composite Primary Key`(graph · s087) … 90 `## 참고 자료`(:1831) … 93 `### 커뮤니티 가이드`(:1849). LEDGER 에 `s080-17`·`s081-17.1`·…·`s093` 이 prose 로 이미 있다. 지도의 «s080-17 «Django admin 타이핑»» 은 기존 §17 과 키 충돌 — 밀림 0 인 말미 추가는 **`## 18. …` → `s094-18`**(«커뮤니티 가이드» 뒤). 관찰: LEDGER 에 `implementation-django-final s087` 행이 prose·graph **2개**(기존 결함 · 이번 범위 밖 기록).
- 9ef6c4f 레시피(md 헤딩+마커 시드 → `--apply` → LEDGER 행 → 소스 미러 append → target-counts SectionShape+1 → q4 골든 → rulepack)는 `ontology_render.graph_sections` 가 manifest 경로 기준이라 doc 무관 — 동작한다. SectionShape 545→546 은 S-1 새 절 하나일 때(S-4·S-5 는 블록 append 라 +0).
- registry_gate(A-18): `$S/rv1A/gate-spring-d2eaafe.txt` — 27종 anchor/current 표 · «귀속 1 · legacy 잔존 2,676 · 해소 9» · exit 2. 귀속 1 은 `mp_probe_s1/alias_inlines.py:N`(⓪ S1 조사자의 untracked 시제품) — 기계는 정확했고 증거 위생 문제다. 두 저장소 소급(1,110줄·상자 둘 13·ignore 38)은 이 산식(N∖L · `_normalize :145` 경로 유지·행번호 `:N`)으로 격리되며, 브라운필드 update 잎이 legacy 파일의 **함수/클래스 이름·메시지 문구**를 바꾸면 귀속으로 바뀐다(설계대로 · #646 메시지에 클래스 이름이 들어가므로 클래스 rename 은 귀속).
- EXPECTED 2회(A-19): 조각 1(#646 public-surface + #648/#649 api-error) → findings_count/checker_baseline/checker_cross 의 public_surface·api_error_controller(+_code) 행 regen · 조각 2(#647) → public_surface 행 재-regen + bad `any_signature.py:41` info→violation 계수 변화. 다른 레인 good 픽스처에는 신규 형상 0(⓪ S4 ⑤ grep 4줄 전부 public_surface · CBV/admin 0)이라 cross 신규 red 는 신설 good 파일 자체가 다른 검사기에 걸릴 때만 생긴다.

## 3. 새로 발견한 문제(확정 방향·증거와 어긋남)

1. **[MAJOR · 지도] `s080-17` 좌표 충돌**(A-17) — ② 가 그대로 쓰면 LEDGER 키 충돌·prose §17 덮어쓰기. 진행 정지 사유는 아니나 계획 좌표를 `s094-18` 또는 `s038-7 append` 로 바꿔야 한다.
2. **[MAJOR · 검사기] ⓑ 가 기저 해소에 종속**(A-2) — 수정 1-2 «타 모듈 import 별칭은 표면 밖»을 ⓑ 까지 적용하면 mypy·#646 동시 침묵 경로가 남는다.
3. **[MAJOR · 검사기] json.load 오라클 «반환» 조건**(A-11) — `-> object` 반환을 후보로 잡음 · 구체 주석 무검증 누락.
4. **[MAJOR · 배선] auto 사각 미봉합**(A-13) — 플러그인 문면이 만든 사각을 회신으로만 처리.
5. [MINOR · 증거] ⓪ S1 ⑦-9 «naming/bad_rules → cross matrix EXPECTED» 오류(A-4) — 계획 항목 삭제.
6. [MINOR · 증거] `proto_646.py` `cand-alias-unresolved` dead code(§2.1) · 사본 `$S/spring/mp_probe_s1/` untracked 잔존(A-18 귀속 1 오염) · 사본들 `.dddjango/violations/` 에 검사기 레코드 누적(무해 · 기록).
7. [MINOR · 문면] 면제 목록 불완전(A-9) — `deconstruct`(kkebi 1)·`model_dump` Protocol(spring 2).
8. [MINOR · 문면] 정본 예시 `list_display` ClassVar 금지 구분(A-21).

## 4. «② 계획에 넣을 것»

### 4.1 공용 기계(check-public-surface-annotation.py)
- `_alias_values(mod) -> dict[str, ast.AST]`: 모듈 수준(if/try 하위) Assign/AnnAssign 중 값이 Name/Attribute/Subscript 인 것 + `TYPE_CHECKING` 분기 안 ClassDef 첫 기저 · 소스 순서 · 뒤 정의가 앞을 덮음. 소비자 3: #493 `_is_declarative_class`(Subscript `.value` 벗김 → 별칭 추적 depth≤4 → `_resolved_name`) · #646 기저 해소 · #647 면제 기저 해소.
- `_origin_bindings(mod) -> dict[str, str]`(로컬 이름 → dotted origin · `_module_bindings` 와 별개 · `_any_bindings` 선례).
- docstring 「검출 한계」에 추가: TYPE_CHECKING 별칭 추적은 **같은 모듈**만 · 타 모듈 import 별칭의 맨몸 여부는 mypy 몫.

### 4.2 #646 판정 규칙(픽스처 명세 수준)
- 기저 집합: `ADMIN_FORM_PATHS`(ModelForm·BaseModelForm·ModelAdmin·InlineModelAdmin·TabularInline·StackedInline·BaseInlineFormSet·BaseModelFormSet × `django.forms(.models)`/`django.contrib.admin(.options)`) ∪ `CBV_PATHS`(proto `CBV_NAMES` 24 × 5모듈). `View`/`TemplateView`/`RedirectView` 제외(default TypeVar).
- 통과: 기저가 Subscript · 모듈 내 별칭(값 Subscript · `TYPE_CHECKING` 분기) · `TYPE_CHECKING` 분기 안 중간 ClassDef.
- ⓐ 위반: 기저(또는 모듈 내 별칭의 값)가 정본 경로의 맨몸 Name/Attribute. 좌표 = 클래스 헤더 줄.
- ⓑ 위반: (i) **모든 ClassDef** 헤더 범위(`cls.lineno` ~ 기저/키워드 마지막 `end_lineno` 이후 코드부가 `:` 로 끝나는 첫 줄)의 `# type: ignore[type-arg]` (ii) 기저 집합 클래스 본문 직계 AnnAssign/Assign 줄의 같은 주석. ⓐ+ⓑ(i) 동시 → 클래스당 1건(ⓑ 문면).
- ⓓ 후보: 헤더의 code 없는 `# type: ignore` · `TYPE_CHECKING` 밖 subscript 별칭(런타임 TypeError 후보) · 기저 집합 클래스 본문 메서드 시그니처 줄·모듈 수준 별칭 정의 줄의 `[type-arg]` ignore.
- 픽스처 `public_surface/good`(신설 파일 1): TypeAlias 별칭 4 + TC 중간 ClassDef 1 + subscript 직접 표기 1(주석 «monkeypatch 전제») · admin 필드 주석은 `list_display: tuple[str, ...]` / `readonly_fields: ClassVar[…]` / `inlines: ClassVar[list[type[InlineModelAdmin[Any, Any]]]]`(mypy 검증 필수). `bad_rules`(신설 1): 맨몸 2(Name·Attribute) · 헤더 ignore 1(여러 줄 헤더 기저 줄) · 속성 줄 ignore 1 · 타 모듈 별칭+헤더 ignore 1(ⓑ 만 기대).
- 기대 수치(앵커 격리 전 전량): spring HEAD ⓐ 0·ⓑ 17+1 · d2eaafe ⓐ 13·ⓑ 17+1 · kkebi ⓐ 0·ⓑ 21 (proto 표 그대로 · 이중 계수 접은 뒤).

### 4.3 #493 개정
- 위 `_alias_values` 적용 + docstring :36~46 «검출 한계» 갱신(Subscript 벗김 · 같은 모듈 별칭 추적 · 중간 ClassDef). 무손실 증명 = 6 대상 before/after comm ∅(§2.3 재실행).

### 4.4 #647 판정 규칙
- 컨테이너 `{dict, Dict, Mapping, MutableMapping}`(`typing`·`typing_extensions`·`collections.abc`·builtins 바인딩 해소) · 값 = 마지막 슬라이스 원소 · union 값은 제외 · 문자열 주석 재파싱 · `Literal[…]` 안 제외.
- 값 `Any`: 전 자리(sig-param·sig-star·sig-return·variable·class-attr)·전 위치 차단. 값 `object`: sig-return·class-attr 차단(nested 포함) / sig-param·variable ⓓ(«입구에서 즉시 좁히는가»).
- 면제(차단→무발화): 반환 루트 `TypeIs`/`TypeGuard` · 프레임워크 오버라이드 표 `{clean: {Form, ModelForm, BaseForm, BaseModelForm}, deconstruct: {Field 계열}}`(메서드 이름 × 기저 계열 · 기저 해소 = `_alias_values`) 의 top `dict[str, object]`. 표는 닫힌 상수(gen_pregate ROSTER 후보).
- #645 배타: `_check_explicit_any` 에서 애너테이션별로 #647 을 먼저 판정 → 위반이면 그 애너테이션의 nested ⓓ 생략(bare 유지). 좌표 = 시그니처는 def 줄 · AnnAssign 자기 줄(#645 동일).
- 픽스처: good `order_form.py` 무변(TypeIs 면제·clean 면제·변수 ⓓ 1 → exit 0) + `dict[str, JsonValue]`·TypedDict 반환 예 1 파일 · bad `any_signature.py:41` 승격 + 신설 1(`-> dict[str, object]` · `x: Mapping[str, object]` 속성 · `list[dict[str, Any]]` 매개변수 · `TypeIs[dict[str, Any]]`).
- 기대 수치: spring HEAD 차단 600줄·ⓓ 267줄 · kkebi 304·436(§2.4).

### 4.5 json.load ⓓ 후보(refined)
- §2.5 규칙 그대로 · 호출 식별 = `json.load|loads`(모듈 별칭·`from json import loads` 바인딩). 물음 «`TypeAdapter(<TypedDict>)` 로 검증하며 받거나 `x: object` 로 받아 즉시 좁혔는가». 기대: spring 41 · kkebi 8. R-0284 감사 입력 목록·R-0345 registry 줄 갱신.

### 4.6 S-5 검사기(#648 ⓐ · #649 ⓒ · ⓑ 철회로 #650 미채번)
- 자리 `_slice_check_controller_ast` + origin 워커 · 판정 §2.6 · `finding_keys.append(None)`.
- #63 auto 사각: (a) `_tree_slice63` 에 base 뭉뚱그림 판정 이식(파일 안 상속 그래프 · 직접 생성 정당 · overlap 키 `("response-base", rel, lineno)`) — 권장 / (b) Coordinator `:119` 문면. 둘 중 하나는 ② 에 필수.
- openapi 문면: `:6`·`:3362` 필수 · `:3371` 권장 · `:3358`/`:3477` 보류(변경 시 findings_count EXPECTED).
- 픽스처: `api_error_controller/{good,bad_rules}` 신설 파일 각 1(§2.6) · `_code` 레인 무변.

### 4.7 등재·도구 영향 목록(빠진 것 포함)
- 검사기 docstring 2(+openapi 1) · `rule-owner-map`·`tree-revision-spec`·`predicates`(ⓓ 채널은 «후보·물음» 필수 — spec_lint ⑥) · `spec_lint` 0 · rulepack · byte 미러 3(`codex-dddjango/skills/dddjango/scripts/`) · `manifest_seal --write`.
- **`gen_pregate_symbol_kinds`**: `--check` 는 source_sha 로 어차피 red → `--write` 재소성 + **ROSTER 행 2 추가**(public-surface #646 기저 집합 `assign_set` · api-error #649 `SCHEMA_ORIGINS/ROOTMODEL_ORIGINS`) — 도구가 새 `.bases` 판정 자리를 자동 감지하지 않으므로 빠뜨리면 «전수» 주장이 조용히 거짓이 된다.
- 매트릭스 3 `--emit-expected`(조각당 1회) · `fixture_matrix` 등재 불요(기존 레인 안 신설 파일) · `registry_gate_smoke` P0′ 는 `skeleton/good_bc` 에 형상 0 → 실행 확인만 · `findings_smoke`/`runtime_parity_check` 실행.
- 온톨로지: S-1 새 절이면 `s094-18`(또는 s038-7 append) · target-counts SectionShape +1 · LEDGER · ISSUED(R-3451~) · wiring enforcedBy(#646/#647 → `c/check-public-surface-annotation.py` · #648/#649 → `c/check-api-error-controller-contract.py`) · Codex SKILL.md hand 미러(houserules §4).
- 조각 분할: 매트릭스 regen 2회를 줄이려면 조각 = {S-1+S-4} / {S-5}(검사기 파일 기준) — 사용자 동의 사항이라 브리프 항목.

## 5. 사각

- mypy 는 실서고 venv 를 cwd=사본으로 썼다(django 플러그인 settings 해소 여부 미확인 · S1/S4 와 같은 대체 근거). kkebi mypy 미실행.
- #646 타 모듈 별칭 ⓐ 는 mypy 의존 — 플러그인은 mypy 를 돌리지 않으므로(S-3) 이 사각은 «별칭을 타 모듈에 두지 않는다» 문면 없이는 남는다(B 축 판단).
- #647 nested 포함·면제 표는 내 재현 기준(수정 1 문면 미명시) — ② 확정 필요. `JsonValue` 정의 위치·`dict[str, object]` 변수 ⓓ 와 json.load ⓓ 의 같은 줄 이중 후보(허용 여부) 미결.
- refined json.load 오라클의 kkebi 리터럴 컨테이너 6 은 사용처를 추적하지 않았다(정당 비율 미판독).
- registry_gate 는 현행 로스터로만 돌렸다 — 신규 규칙의 앵커 격리는 같은 산식이라는 구조 추론(직접 실측은 ⑤ 에서).
- CBV 코퍼스 예시 3줄·django-web 블록 정정의 렌더·LEDGER 영향은 B 축.

Serena: skipped — 워크트리에 `.serena/project.yml` 없음.
