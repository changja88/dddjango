# ④-1 조각 1(S-1 + S-4) 구현 기록 (2026-09-04 · 브랜치 fix/field-report-3)

계획 v2(Δ1~Δ15) 집행. 순서 = Δ3: 검사기·픽스처 → pregate ROSTER → 매트릭스 → 온톨로지(md 시드·rdflib·gate·render) → prose §13.4 → 소스 미러 → LEDGER → ISSUED·target-counts·q4·rulepack → 등재 3문서 → corpus_mirror_sync·codex hand 3·byte 미러 → seal(draft) → spec_lint → verify → 무손실.

## 검사기 `check-public-surface-annotation.py`(패치 스크립트 `scratchpad/fr3/impl/patch_public_surface.py` + 별칭 해소 후속 1)

- 공용 기계: `_origin_bindings`(dotted origin) · `_alias_defs`(이름 → [(값, TC 분기 안)] · 뒤 정의 우선) · `_resolved_base`(Subscript 벗김 · 별칭 depth≤4) — 인자 전달(전역 0).
- #493 수리: `_is_declarative_class(cls, bindings, aliases)` — 별칭·subscript 기저의 선언적 면제 회복(`_scan_stmts`/`_scan_class` 시그니처 `aliases` 추가).
- #646: origin 집합 admin 5 + forms 9 + CBV 32(6.1.0) · 3모양 통과 · ⓐ 맨몸 · ⓑ 헤더(tokenize 범위)·속성 줄 `type: ignore[type-arg]` · ⓐ+ⓑ 1건 · ⓓ code 없는 ignore · ⓓ 런타임 subscript(별칭·헤더 직접) · 루트 필터.
- #647: `_record_value`(값 자리 · 컨테이너 이름 import 별칭 해소) · 매트릭스(Any 전 자리 차단 · object 반환/속성 차단 · 매개변수/변수 ⓓ) · 면제 `TypeIs/TypeGuard` 루트 · `clean`×Form 계열 · `deconstruct`×Field 계열 · 반환 자리표시 `object` ⓓ(union·시퀀스 원소) · #645 배타(위반 애너테이션의 nested ⓓ 생략 · bare 유지) · #645 문면·심각도 종전 그대로.
- #650(ⓓ 전용): `_slot_is_object` 오라클(A-9 refined) · 좌표 규칙 · 물음 두 갈래.
- docstring 규칙 3 + 검출 한계 + 루트 필터.

## 실측(격리 사본 · 기대 = rv3-C §2 루트 필터 뒤 값)

| 항목 | spring HEAD | 기대 | d2eaafe | 기대 | kkebi | 기대 |
|---|---|---|---|---|---|---|
| #646 위반 | 18 | 18 | 31 | 31 | 21 | 21 |
| #647 위반 줄 | 594 | 594 | — | — | 161 | 161 |
| #647 ⓓ 입구 줄 | 255 | 255 | — | — | 253 | 253 |
| #647 ⓓ 자리표시 object | 8 | 8 | — | — | 42 | 42 |
| #650 ⓓ | 40 | 40 | 38 | — | 1 | 1 |
| #645 위반 라인 | 76(byte 동일) | 76 | 78 | 78 | 121(byte 동일) | 121 |
| ⓓ#645 → #647 1:1 | 655/655(+5 `mp_probe_*` 사본 오염 제외) | — | — | — | 55/55 | — |
| #493 | 3,216(무변) | | 3,225 | | 173 | |

C-only/new-only 차분 0(스크립트 `scratchpad/fr3/impl/cmp647.py`). #647 별칭 해소 전에는 spring 22줄(`Mapping as _Mapping`)이 빠졌었다 — `_resolved_name` 으로 컨테이너 이름을 풀어 해소.

## 픽스처(신설만 · 기존 파일 정정 2)

- good: `admin/order/panel.py`(0B → 별칭 ModelAdmin+TabularInline · 무주석 선언 속성) · `admin/order/form/line_form.py`(별칭 ModelForm) · `admin/shipment/panel.py`(TC 중간 ClassDef) · `adapter/persistence/domain_bypass_query/ledger_record_query.py`(TypedDict·TypeAdapter·JsonValue·`x: object = json.loads` 즉시 검증). **정정**: `order_form.py`(`cleaned: dict[str, object]` 지역 변수 제거 — 하네스 green 축 «레코드 0» 요건 · R-3448 시연은 `raw: object` 즉시 좁힘 유지) · `place_order_use_case.py`(`-> object` → `-> int` — 자리표시 ⓓ 회피). 계획 Δ9의 `invoice/panel.py`(직접 subscript ⓓ ②)는 good 에 둘 수 없어(레코드 0 요건) bad 의 `AttributeLineIgnorePanel` 로 시연.
- bad_rules: `admin/order/stub_generic_bad.py`(맨몸 Name·Attribute · 여러 줄 헤더 ignore · 속성 줄 ignore · 타 모듈 별칭+헤더 ignore · 맨몸 ModelForm) + `_bases.py` · `place_order/record_leak.py`(object 속성·반환 · nested Any 매개변수 · `TypeIs[dict[str, Any]]` · `payload: dict[str, Any] = json.loads`) · `any_signature.py:41` #647 승격.
- 자기 검사기: good exit 0 · 레코드 0 / bad exit 2 · `#358×2,#456×2,#493×9,#645×8,#646×7,#647×6,#650×1,#69×2`(#493 +1 = 타 모듈 별칭 클래스 `SharedAliasPanel` 의 `list_display` — 별칭 해소는 같은 모듈만 · 의도).

## 등재·도구

- `gen_pregate_symbol_kinds.py` ROSTER +2(`STUB_GENERIC_ADMIN_FORM_NAMES`·`STUB_GENERIC_CBV_NAMES` · emit=None) → 재소성 in-sync(종류 56).
- `findings_count_matrix` public-surface 행 `(2, 33, 4, "#358×2,#456×2,#493×9,#645×8,#646×7,#647×6,#650×1,#69×2", …)` · `checker_baseline_matrix` `(2, 33, 33, 6, False)` · `checker_cross_matrix` 3행 변화(port_adapter_pairing·transaction_boundary good 의 ⓓ#647 info 관찰 12·2 · public_surface×port-adapter #359 2→4 — 신설 good 파일) · 신규 쌍 0 · 73/73 · 348/348.
- `registry_gate.py` ⓔ2(rv3-A 시제품 그대로 · ⓓ 절·sidecar 키는 N′∪L′≠∅ 일 때만) · smoke 33/33(Q ⓓ 앵커 차분 · Q′ 위반 동반 · P0′ byte 동일 유지).
- 등재 3문서 #646/#647/#650 + 집계(`ast+` 60 · 계 550 · 읽는 법 59) · spec_lint 0.

## 온톨로지(스크립트 `scratchpad/fr3/impl/piece1_ontology.py` · gate 90/90)

- 신설 R-3451~R-3462(12) · 개정 R-3447 rev2(`@2026-09-04b` amendment) · R-3448 rev2(`@2026-09-04b` redefinition) · R-3154·R-3163·R-2715 rev2 · R-0284 rev4·R-0345 rev3(`@2026-09-04b`) · prefLabel 7 갱신 · 새 절 s094-18(`sectionNumber "18"`) · 블록 +14 · target-counts Block 2917 · Section 546 · Norm/Work 3471 · Expression 3587 · q4 골든 +12 · rulepack 재소성 · LEDGER 10행(graph 8 · baseline 1 · prose 1) · ISSUED +12.
- 렌더 7 doc · 소스 미러 4절 교체 + §18 append · corpus_mirror_sync 11/11 · codex hand 3(houserules §4·§6.1 본문 동일 검증 · Coordinator b6·b28 · implementation-django §18 행) · byte 미러(검사기·registry_gate·pregate json·rulepack) diff 0 · seal draft green.

## 검증(결과는 아래 추기)

- **무손실(`scratchpad/fr3/rv3C/lossless.sh main worktree` · `impl/lossless1.log`)**: 저장소 4사본 × 3 검사기 **12/12 OK** — 비허용 차분 0 · A∖B = ⓓ#645 nested → #647 1:1(spring 655 · d2eaafe 642 · f5ee428 661 · kkebi 55 · unmatched 0) · B∖A = {#646, #647, #650} 만 · #493 집합 동일(3,216/3,225/3,225/173) · api-error·openapi 출력 byte 동일 · `scripts-diff` 4파일(검사기·registry_gate·pregate json·rulepack = 이번 변경 전부 · 나머지 24 검사기 byte 동일).
- 픽스처: 현행 트리 기준 102 중 RED 3 = 전부 `public_surface` 레인의 **신설·정정 픽스처 파일에 옛 #493 이 낸 위반**(`admin/order/panel.py` 무주석 admin 선언 속성 7 · `stub_generic_bad.py:26` — 별칭·subscript 기저의 선언적 면제 회복이라는 #493 수리의 의도된 효과 · 저장소 4사본에서는 #493 집합 동일). **main 픽스처 트리(신설 파일 없음)로 재실행 = 9/9 OK · `VERDICT: LOSSLESS`**(`impl/lossless_fx_main.py` · `impl/lossless-fxmain/`).
- **`make verify` 6/6 green**(218초 · `impl/verify1.log`) — verify-ontology(gate 90 · shacl · hierarchy 9종 · golden) · base-core(corpus 11/11 · spec_lint 0 · fixture 104/104 · baseline 73 · count 73 · findings_smoke · rulepack --check · manifest draft · byte-copy) · base-cross(cross 348/348 · registry_gate_smoke 33/33) · backstop · regen(parity·pregate-kinds) · web.
- **registry_gate ⓔ2 실측**(`impl/gate-{spring,kkebi}.log` · 앵커=HEAD + 무해 파일 1): spring «ⓓ 신규 0 · legacy 991 · 귀속 0 · exit 0» · kkebi «ⓓ 신규 0 · legacy 1,269 · 귀속 0 · exit 0» — 기존 ⓓ 전량이 legacy 로 접히고 신규분만 절·sidecar(`candidate_lines`)에 실린다.
