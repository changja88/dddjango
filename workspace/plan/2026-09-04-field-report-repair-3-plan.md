# 현장 보고 3 — ② 계획 (2026-09-04 · ⓪ 실측 + ① 리뷰 3기 반영 · ③ 리뷰 대상)

문안 정본 출처: `workspace/eval/field-report-3/rv1/rv1-B.md` §3(«문안 초안» — 아래 «채택(+델타)»로 인용) · 검사기 명세 출처: `rv1/rv1-A.md` §4 · 효과·소급 수치: `rv1/rv1-C.md` §4~§5. 결정 정본: `2026-09-04-field-report-repair-3-issues.md` §2-A~§2-D + 수정 1. 이 계획은 그 문안·명세를 «어디에·어떤 순서로·무엇을 바꿔서» 넣는지 확정한다. 델타가 없는 항목은 rv1 문안 그대로다.

## §0 범위(확정 · ① 반영)

- **S-1**(문면 + #646 + #493 수리): 별칭 기본 · monkeypatch 채택(§6.1 관찰) 시 직접 표기 · `# type: ignore[type-arg]` 금지 · 범위 = «타입 매개변수에 기본값이 없는 django-stubs 제네릭 기저»(admin·form 8 + CBV · `View`/`TemplateView`/`RedirectView` 제외). §2-A 수정 1 ⑤(`Any` 조건부 구절) **철회** → R-3154 rev2로 대체.
- **S-4**(문면 + R-3447/R-3448 rev2 + 결정표 + #647 + #650 ⓓ): «선» = 값 `Any` 전 자리 차단 · 값 `object` 반환/속성 차단 · 매개변수/즉시 검증 지역 변수 ⓓ · 면제 `Form.clean`·`TypeIs/TypeGuard` · 반환 주석의 `object`(루트·컨테이너 원소)는 ⓓ.
- **S-5**(ninja 문면 2(2a·2b) + api 계약 1 + #648·#649): ⓑ 철회(#63 기존) · openapi 검사기 stale 문면·등재 수리.
- **확장(결정 밖 · ⑥ 고지 · 사용자 예고)**: ⓔ1 Coordinator R-0331 rev2(auto «무관» 판정식) · ⓔ2 registry_gate ⓓ 앵커 격리(N∖L) + R-0284 «앵커 차분 신규분».
- 무접촉: `design_pregate.py` · houserules-final · dddjango-web 플러그인.
- 조각: **조각 1 = S-1 + S-4**(houserules-skill §4·§6.1 · django-final §18 · django-skill 표 · django-web · python · ddd · command R-0284/R-0345 · `check-public-surface-annotation.py` · registry_gate ⓔ2) · **조각 2 = S-5 + ⓔ1**(ninja-final · ninja-skill · api-final · command R-0349/R-0331 · `check-api-error-controller-contract.py` · `check-openapi-error-declaration.py` 문면). 릴리즈는 하나.

## §1 온톨로지 변경 명세 (doc_key 10 · 신설 R 17 · 개정 9)

채번(ISSUED 순): 조각 1 — R-3451(S-4 도입) · R-3452~R-3457(결정표 6행) · R-3458·R-3459(S-1 b16) · R-3460·R-3461(django §18 b1·b3) · R-3462(django-web §6 b10) / 조각 2 — R-3463(ninja b13 상자 하나) · R-3464(ninja §3.1 b9) · R-3465(ninja §2.2 b1 익명 union) · R-3466(ninja-skill 불릿) · R-3467(api §5.2 b7). 개정: R-3447 rev2(`@2026-09-04b` amendment) · R-3448 rev2(`@2026-09-04b` **redefinition**) · R-3154 rev2 · R-3163 rev2 · R-2715 rev2 · R-0284 rev4(`b`) · R-0345 rev3(`b`) · R-0349 rev2 · R-0331 rev2(현행 날짜 확인 뒤 `b` 여부). 블록 order는 말미 append만(중간 삽입 0).

### 1.1 `discipline-houserules-skill`(조각 1)
- s007-4/**b7** text 교체 = rv1-B §3.1 채택(+델타: 말미에 «반환 주석의 `object`(루트·`tuple`/`list` 원소)도 입구 밖 자리표시라 #647 ⓓ 후보다 · `json.load(s)` 결과가 `Any`/`dict[str, Any]` 주석·반환·컴프리헨션으로 흐른 자리는 ⓓ #650»). statesNorm R-3447(rev2)·R-3448(rev2) · prefLabel 갱신(§3.1 귀속대로).
- **새 b8**(norm · R-3451) = §3.2 도입문 · **b9**(table-row · norms=[] · xsd:string) 머리 2줄 · **b10~b15**(table-row · R-3452~R-3457) = §3.2 6행(6행 «입구 밖» 한정 · 2행 «파싱한 JSON은 내부 것도 `TypeAdapter`» · 5행 `JsonValue` 공변 · 3행 ddd §3.1 참조).
- **새 b16**(norm · R-3458 Obligation + R-3459 Prohibition) = §3.3 S-1 문안(대안 문단은 쓰지 않는다 — ⑤ 철회). 마지막 블록이 `\n\n` 소유(§4.1 헤딩 앞) — b7의 말미 개행 조정.
- s007-4/**b5** R-3154 rev2 = §3.4 b5 문안 · s011-6.1/**b1** R-3163 rev2 = §3.4 b1 문안.
- wiring(`discipline-houserules-skill.ttl`): R-3451~R-3459 delegatedTo discipline-reviewer · enforcedBy public-surface = R-3451·R-3452·R-3455(#647)·R-3458·R-3459(#646) · **R-3448 enforcedBy public-surface 추가**.

### 1.2 `implementation-django-final`(조각 1) — 말미 새 절 **s094-18**
- md에 헤딩 `## 18. Django admin·폼 타이핑 — django-stubs 제네릭 기저` + graph-owned 마커 시드(«커뮤니티 가이드» 절 뒤 · 9ef6c4f 동형) → ttl Section 노드(headingSnapshot·inDocument·sectionOwner) + b1(norm R-3460 = §3.5 b1) · b2(code = §3.5 b2 **델타: admin 선언 속성 전부 무주석**(`readonly_fields = ("version",)` — R-3154 rev2 «재선언하지 않는다»와 일치) · `_ChildFormSetBase` 셋째 인자 전방 참조 문자열 유지) · b3(norm R-3461 = §3.5 b3) · b4(prose `---`). **④ 착수 시 정본 예시를 격리 사본에서 mypy strict 1회 검증**(B 탐침은 A·B·E 모양만).
- LEDGER baseline 행(graph) · target-counts SectionShape +1 · 소스 미러 `workspace/reference/implementation-django/reference/final.md` 절 수동 append.
- wiring(`implementation-django-final.ttl`): R-3460·R-3461 delegatedTo discipline-reviewer · R-3461 enforcedBy public-surface(#646) · `djr:restates` → houserules-skill s007-4/b16.
- **prose §13.4**(:1328 `EditArticleView(…, UpdateView)`): md 직접 = §3.8 마지막 항 + LEDGER prose 재기준선(s065-13.4).

### 1.3 `implementation-django-skill`(조각 1) — s005 상세 레퍼런스 표 **새 b18** `| Django admin·폼 타이핑(django-stubs 제네릭 기저) | §18 |\n\n`(b17 말미 `\n`) · norms=[] · codex `implementation-django/SKILL.md` hand 미러.

### 1.4 `implementation-django-web-final`(조각 1)
- s003-2/**b10** code 정정(= §3.8 · CBV 별칭 압축형 + 주석 1줄) · s007-6/**b9** code 정정(`_ArticleFormBase` 별칭) · s007-6 **새 b10**(norm · R-3462 = §3.8 문안 · delegatedTo discipline-reviewer). LEDGER graph 재기준선 2절.

### 1.5 `implementation-python-final`(조각 1) — s007-1.5/**b1** R-2715 rev2(= §3.6 b1) · **새 b3**(code = §3.6 b3 · `to_json_value` 브리지 포함). LEDGER.

### 1.6 `architecture-ddd-final`(조각 1) — s040-5.5/**b10** code 정정(= §3.7 `FieldValue` 닫힌 union · `Any` import 제거). LEDGER.

### 1.7 `command-dddjango`
- 조각 1: s007/**b6** R-0284 rev4(= §3.9 b6 + ⓔ2 델타: «해당 범위 실행분» → «registry_gate 앵커 차분의 **신규분**(legacy ⓓ는 보고 절만)» · `#6NN`→`#650`) · s007/**b28** R-0345 rev3(= §3.9 b28 · `#6NN`→`#650`).
- 조각 2: s007/**b32** R-0349 rev2(= §3.9 b32) · s007/**b16** R-0331 rev2(= §3.13 · ⓔ1).
- codex `codex-dddjango/skills/dddjango/SKILL.md` hand 미러(:125·:150·registry 11·15·scope별 실행 행).

### 1.8 `implementation-django-ninja-final`(조각 2)
- s009-2.2/**b13** text 확장 + statesNorm += R-3463(Prohibition · = §3.10 · R-0687 amendment 아님) · s012-3.1 **새 b9**(norm · R-3464 · = §3.11 b9 · tarot 인용) · s009-2.2/**b1** 말미 1문장 + statesNorm += R-3465(= §3.11 b1).
- wiring: R-3463 enforcedBy api-error-controller(#648) + delegatedTo discipline-reviewer · R-3464 enforcedBy api-error-controller(#649) + delegatedTo design-review-api · R-3465 delegatedTo design-review-api, discipline-reviewer.

### 1.9 `implementation-django-ninja-skill`(조각 2) — s004 «핵심 운영 원칙» 새 불릿(R-3466 · restates b13·b1·b9 · = §3.11 선택 문안) · codex `implementation-django-ninja/SKILL.md` hand 미러.

### 1.10 `architecture-api-final`(조각 2) — s022-5.2 **새 b7**(R-3467 · = §3.12 · delegatedTo design-review-api) · b6 말미 `\n\n`→`\n`.

### 1.11 공통 절차(조각마다)
rdflib 편집 스크립트(`scratchpad/fr3/impl/<조각>_ontology.py` — 롤백 가능 · canon 재직렬화 byte roundtrip 선검증) → `ontology_render --apply <doc_key…>` → LEDGER 행(graph 재기준선 · 새 절 baseline · prose 1) → ISSUED append → `workspace/eval/fixtures/ontology_gate/target-counts.json`(SectionShape +1 · BlockShape · NormShape/WorkShape +17 · ExpressionShape +17+9) → `query_golden_check --emit` → `make rulepack` → 소스 미러 span 교체 + `corpus_mirror_sync --write` → codex hand 미러 4(houserules · dddjango(Coordinator) · implementation-django · ninja SKILL.md) → `spec_lint` 0 → `make verify`.

## §2 검사기 변경 명세

### 2.1 `check-public-surface-annotation.py`(조각 1 · byte 미러)
- **공용 기계**(rv1-A §4.1): `_alias_values(mod)`(모듈 수준·if/try 하위 Assign/AnnAssign 값 Name/Attribute/Subscript + `TYPE_CHECKING` 분기 안 ClassDef 첫 기저 · 뒤 정의 우선 · 추적 depth≤4) · `_origin_bindings(mod)`(로컬 이름→dotted origin). docstring «검출 한계»: 별칭 추적은 같은 모듈만.
- **#493 수리**: `_is_declarative_class`가 기저를 `_alias_values`로 풀고 Subscript `.value`를 벗긴다 → admin·form 선언적 면제 회복. 무손실 = 두 저장소·픽스처 before/after 발화 집합 동일(A §2.3 재확인 · synth만 5→0).
- **#646**(rv1-A §4.2 채택 + 델타): 기저 집합 `ADMIN_FORM_ORIGINS`(8) ∪ `CBV_ORIGINS`(기본값 없는 것만 · `View`/`TemplateView`/`RedirectView` 제외) · 통과 3모양 · ⓐ 맨몸(좌표 클래스 헤더 줄 · 메시지에 클래스명·기저명) · ⓑ(i) **모든 ClassDef** 헤더 범위의 `# type: ignore[type-arg]`(기저 해소와 독립 — A-2) · ⓑ(ii) 기저 집합 클래스 본문 직계 AnnAssign/Assign 줄의 같은 주석 · ⓐ+ⓑ(i) 동시 = 클래스당 1건(ⓑ 문면) · ⓓ = code 없는 `# type: ignore` 헤더 · `TYPE_CHECKING` 밖 subscript 별칭 · **루트 필터**: `application/**`·`framework/**`만(신규 규칙 3종 공통 · docstring 명시 · 기존 규칙 무변).
- **#647**(rv1-A §4.4 채택 + 델타): 컨테이너 `{dict, Dict, Mapping, MutableMapping}` 바인딩 해소 · 값 = 마지막 슬라이스 원소 · 값 `Any` 전 자리·전 위치 차단 · 값 `object` sig-return·class-attr 차단(nested 포함) · sig-param·variable ⓓ · 면제 = `TypeIs`/`TypeGuard` 반환 루트 · `{clean: {Form, BaseForm, ModelForm, BaseModelForm}}` 기저 계열의 `-> dict[str, object]`(기저 해소 `_alias_values`) · **델타 ⓓ 추가**: 반환 주석에 `object`가 루트 또는 `tuple/list/Sequence/Iterable/Iterator/set/frozenset` 원소로 나타나면 ⓓ(«입구 밖 자리표시») · #645 배타: 같은 애너테이션 노드에 #647 위반이면 #645 nested ⓓ 생략(bare는 유지) · 루트 필터 동일.
- **#650**(ⓓ 전용 · rv1-A §2.5 refined 오라클): `json.load|loads`(모듈 별칭·from import 바인딩) 결과가 AnnAssign 주석≠`object` / 반환 주석≠`object` 함수의 Return / 컴프리헨션 요소 / 직접 Subscript·Attribute 접근 / 리터럴 컨테이너 요소로 흐르면 후보 · 비후보 = `x: object = …` · 호출 인자 · 무주석 Assign(#493 몫). 물음 «`TypeAdapter(<TypedDict>)`로 검증하며 받았거나 `x: object`로 받아 즉시 좁혔는가». 기대 spring 41 · kkebi 8.
- docstring: #646·#647·#650 항목 + 검출 한계 갱신 · `main` 호출 순서: `_scan_stmts` → `_check_explicit_any`(#645+#647 배타) → `_check_stub_generic_bases`(#646) → `_check_json_load`(#650).

### 2.2 `check-api-error-controller-contract.py`(조각 2 · byte 미러)
- `_slice_check_controller_ast`에 origin 워커(모듈 수준 Import/ImportFrom → dotted) 추가 · **#648** 반환 주석 평탄화(`|`·`Union`·`Optional`·문자열) 후 `Subscript.value` origin ∈ {`ninja.Status`, `ninja.responses.Status`} 계수 ≥2 → `findings.add("#648", …)` + `finding_keys.append(None)` · **#649** `ClassDef.bases`(Subscript는 `.value`) origin이 `ninja.Schema` ∧ `pydantic.RootModel` → `#649`(`schema_out.py` 한정 없음). 프로필 무관 트리 슬라이스라 auto G2에서 동작.
- docstring 갱신 · 기존 규칙 발화 무변(byte 동일 증명).

### 2.3 `check-openapi-error-declaration.py`(조각 2 · byte 미러) — stale 문면 2곳(rv1-B §3.14 문안 · `:5~7` docstring · `:3362` 조치) + 권장 `:3371` 검토. findings_count EXPECTED 영향 시 regen.

### 2.4 `registry_gate.py`(조각 1 · ⓔ2) — `_CANDIDATE_RE = ^\s*(\[ⓓ#\d+\].*)$` 추가 · ⓓ 라인도 `_normalize`로 앵커 L′/현재 N′ 집합 → «ⓓ 신규(N′∖L′)» 절 + «ⓓ legacy n건» 요약 · sidecar에 ⓓ 신규 레코드 동봉 · exit 산식 무변(ⓓ는 exit 불산입 유지) · docstring · `registry_gate_smoke.py`에 ⓓ 케이스 1(앵커에 있던 ⓓ는 legacy · 새 파일의 ⓓ는 신규). 두 저장소 재실행으로 ⓓ 신규 0(HEAD=앵커) 확인.

## §3 픽스처 · 매트릭스 · 등재 · 미러

- 픽스처(신설 파일만 · 기존 파일 무변): `public_surface/good/…/admin/<area>/stub_generic_panel.py`(별칭 4 + TC 중간 ClassDef 1 + subscript 직접 1 + 무주석 admin 선언 속성 · **mypy 검증 필수**) · `public_surface/good/…/record_types.py`(`TypedDict`·`TypeAdapter`·`dict[str, JsonValue]` 반환 · `x: object = json.loads` 즉시 검증) · `public_surface/bad_rules/…/stub_generic_bad.py`(맨몸 Name·Attribute · 여러 줄 헤더 ignore · 속성 줄 ignore · 타 모듈 별칭+헤더 ignore) · `bad_rules/…/record_leak.py`(`-> dict[str, object]` · `x: Mapping[str, object]` 속성 · `list[dict[str, Any]]` 매개변수 · `TypeIs[dict[str, Any]]` · `payload: dict[str, Any] = json.loads(raw)`) · `any_signature.py:41` 승격(메시지 변경) · `api_error_controller/good/…/<area>_controller.py` 신설(`-> Status[Out | Err]` · `RootModel[Annotated[…]]` 단독) · `api_error_controller/bad_rules/…`(상자 둘 · `Schema`+`RootModel`). good `order_form.py` 무변(TypeIs·clean 면제 · 변수 ⓓ 1 → exit 0).
- 삼중 등재: `fixture_matrix.py` 무변(기존 레인 안 파일) · `findings_count_matrix.py`·`checker_baseline_matrix.py`·`checker_cross_matrix.py` `--emit-expected`(조각당 1회 · 조각 1 = public_surface(+guard-zero 확인) · 조각 2 = api_error_controller(+_code 무변 확인)) · `registry_gate_smoke.py` P0′ + ⓓ 케이스 · `gen_pregate_symbol_kinds.py --write` + ROSTER 행 2(#646 기저 집합 · #649 origin 집합) · `findings_smoke`/`runtime_parity_check` · `manifest_seal.py --write`.
- 등재 3문서: `2026-08-08-tree-revision-spec.md` 행 5(#646 ast+ · #647 ast+ · #648 ast · #649 ast · #650 ast+) + 집계(`ast` 63→65 · `ast+` 57→60 · 계 547→552 · 읽는 법) + #63 행 stale 정정 · `2026-08-11-predicates.md` 행 5(셀 `|` 금지 · ⓓ 행은 «후보·물음») · `2026-08-11-rule-owner-map.md` 행 5 + #63 비고 · `spec_lint.py` 0.
- 미러: 검사기 byte 3(public-surface · api-error-controller · openapi-error-declaration) · final.md byte 6 · SKILL.md hand 4 · rulepack 2 · 소스 미러 corpus_mirror_sync.

## §4 순서

1. ④-1 조각 1: 정본 예시 mypy 검증(사본) → 검사기(#493 수리 → #646 → #647 → #650 → registry_gate ⓔ2) + 픽스처 → 매트릭스 regen → 온톨로지(1.1~1.7 조각 1분) → 등재 → 미러 → `make verify` → 무손실 증명(§5) → 커밋(경로 명시 · 여러 커밋 허용).
2. ⑤-1 리뷰 3기(조각 1) → 정정 커밋.
3. ④-2 조각 2: 검사기(#648·#649 · openapi 문면) + 픽스처 → 매트릭스 regen → 온톨로지(1.7 조각 2분 · 1.8~1.10) → 등재 → 미러 → `make verify` → 무손실 증명 → 커밋.
4. ⑤-2 리뷰 3기(조각 2) → 정정 커밋.
5. 회신 3(`2026-09-04-field-report-reply-3.md`: 처분 표 · 발주측 항목 8(rv1-B §5-13) · 효과 정직화(rv1-C §5) · legacy 규모) · 추적표 §0 상태 갱신 · 로드맵·조감도·ledger.
6. ⑥ 독립 감사 + 재검 → «머지 진행» 브리프.

## §5 무손실·검증 계획

- 검사기 retro(두 저장소 3사본 + 픽스처 87루트): main 검사기 vs 새 검사기 출력에서 **#646·#647·#648·#649·#650 이외 라인 byte 동일** · #645 nested ⓓ 감소분 = #647 위반과 1:1(spring 518·kkebi 157) · #493 lost 0/gained 0 · registry_gate 귀속 0(HEAD=앵커) · ⓓ 신규 0.
- 기대 계수(rv1-A·C): #646 spring HEAD ⓑ 17+1 · d2eaafe ⓐ 13·ⓑ 17+1 · kkebi ⓑ 21 / #647 spring 차단 600줄·ⓓ 267(+반환 object ⓓ ≈8) · kkebi 304·436(+34) / #650 41·8 / #648 spring 7·kkebi 6 / #649 f5ee428 1.
- 픽스처: good 전부 exit 0 · bad 신설 파일이 다른 검사기에 걸리지 않음(cross 신규 red 0) · `make verify` 6/6.
- 온톨로지: 편집 전 16 ttl canon roundtrip byte 동일 · 편집 후 gate/shacl/hierarchy/golden green · 렌더 md diff = 의도한 절만.

## §6 3축 체크(③ 리뷰어 필답)

- 코퍼스 정합: §1 IRI·order·statesNorm·revision 전수 · 개정 9의 revisionKind(R-3448만 redefinition) · 새 절 s094-18 레시피 · R-3447/R-3448 한 블록 두 Work의 문장 귀속 · 결정표 table-row 8블록 · Coordinator 4개정과 registry 소개행의 규칙 번호 일치 · 배선표(rv1-B §3.15) · 등재 3문서 집계.
- 일반화: Claude/Codex 미러 전수 · 프로젝트 플래그 비의존(루트 필터는 표준 트리 값) · kkebi 대조(별칭 31·TC 15 통과 · ⓓ 436의 감수 부담은 ⓔ2 격리 뒤 신규 0) · CBV 예시 정정이 web 레인에 배움을 주는가(R-3462).
- 무손실: §5 · #493 수리의 검출 집합 «불변» · #645→#647 이동의 1:1 · registry_gate exit 산식 무변 · 픽스처 정리 없음(신설만).

## §7 리스크·미결(③에서 판정)

1. 정본 예시(§1.2 b2)의 strict 통과 — 전방 참조 문자열·`type ParentInlineFormSet` bound 표기·무주석 admin 속성. 실패 시 형태 조정(문면은 유지).
2. #647 반환 `object` ⓓ의 오탐(spring 8·kkebi 34 형상 — `pull_events -> list[object]` 등 도메인 이벤트 자리): ⓓ라 exit 무관이나 문면 «입구 밖 자리표시»가 그 자리를 설명하는가.
3. ⓔ2 registry_gate 변경 범위(파서·보고·sidecar·smoke) — «exit 무변»을 smoke가 증명하는가.
4. ⓔ1 R-0331 rev2가 기존 lane(리딩 refactor-scope «auto»)을 소급 반송하지 않는가(문면은 신규 G2에만).
5. 채번·날짜 접미(`@2026-09-04b`)는 ④ 커밋일 기준 — 날짜가 바뀌면 `@<그날>`.
6. SKILL.md hand 미러 4의 의미 동치 확인(cmp 불가 · diff 검토).
