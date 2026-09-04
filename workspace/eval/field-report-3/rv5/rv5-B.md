# 현장 보고 3 · ⑤-1 구현 리뷰(조각 1 커밋 `56b27e1`) — 리뷰어 B(규범 축: 온톨로지 정본·렌더 문면·미러·등재 문서) · 2026-09-04

- 대상: `56b27e1`(S-1 + S-4) 의 `ontology/**` · 렌더 md 7 doc · 소스 미러 · codex 미러(final byte 4 · SKILL hand 3) · LEDGER/ISSUED/target-counts/q4 골든/rulepack · 등재 3문서. 기준 = 계획 v2(§1·§1.11·Δ1~Δ4·Δ13) · ③ 완성 문안 `rv3/rv3-B.md` §3 · `rv1/rv1-B.md` §3.6/§3.7 · 구현 기록 `evidence/impl/piece1-summary.md` · 편집 스크립트 `piece1_ontology.py`/`ontlib.py`.
- 방법: 정본 ttl 을 rdflib 로 Work·Expression·Block·Section·wiring 단위 실확인(`$S/rv5B/struct_check.py`) · **③ 완성 문안과 ttl 텍스트 글자 단위 대조**(`$S/rv5B/text_cmp.py` · 결과 `text_cmp.txt`) · LEDGER 10행 sha 를 배포 span(strip_marker)·소스 미러 span 양쪽에서 재계산(`ledger_check.py`) · rulepack JSON 순회 · codex 미러 byte/본문 대조 · 도구 재실행(`ontology_gate` 90/90 · `ontology_render_sync` red 0 · `corpus_mirror_sync --check` 11/11 · `spec_lint` 0 · `ontology_issued_check` 0) · **§18 정본 예시 «정확 블록» mypy strict 재검증**(ttl b2 텍스트 추출 → 모델 바인딩 import 2줄만 주입 → spring `pyproject` strict 설정 · `$S/spring/mp_probe_rv5b/p18_exact.py` → `Success: no issues found`).
- 판정 값: 검증됨 / MINOR / MAJOR / BLOCKER. **BLOCKER 0 · MAJOR 0 · MINOR 5**(+사각 4). 실서고·온톨로지·md 무수정(정정은 문안).
- IRI 접두 `<https://numchida.com/ns/djr#s/dddjango/…>` 는 `…/<doc>/<sNNN>/bN` 으로 줄인다. `$S` = `scratchpad/fr3`.

Serena: skipped — 워크트리에 `.serena/project.yml` 없음(기본 도구 + rdflib).

---

## 1. 판정 표

| # | 항목 | 판정 | 한 줄 |
|---|---|---|---|
| B-1 | 신설 R-3451~R-3462 kind·prefLabel·Expression | 검증됨 | kind = Prohibition 2(R-3451·R-3459) · Obligation 10 — rv3-B §3-10 표 그대로. prefLabel @ko 1개씩 · Expression `<R-34NN@2026-09-04>` rev 1 · `currentExpression` ✓ · statesNorm 귀속 블록 = 계획(b8·b10~b15·b16·§18 b1/b3·web b10) ✓. |
| B-2 | 개정 7 Expression 노드 | 검증됨 | `@2026-09-04b` 4(R-3447 rev2 amendment · **R-3448 rev2 redefinition** · R-0284 rev4 · R-0345 rev3) · `@2026-09-04` 3(R-3154·R-3163·R-2715 rev2 amendment) · `wasRevisionOf` 사슬(R-0284: 08-22→09-01→09-04→09-04b · R-0345: 08-22→09-04→09-04b) · `currentExpression` 교체 ✓ · redefinition 은 R-3448 만 ✓. |
| B-3 | prefLabel 7 갱신 ↔ rv3-B §3-9 | 검증됨 | 6개 글자 동일. R-3448 만 «· 예외 프레임워크 콜백 미러·이벤트 컬렉션» 구절 추가 — Δ4 «ⓓ 예외 구절» 이 b7 본문에 들어갔으니 명칭(=rulepack 주입값)에 병기한 것은 정당. |
| B-4 | 블록 order·kind·리터럴 언어 | 검증됨 | s007-4 b1~b16 연속 · b9~b15 `kind-table-row` plain literal · b8/b16 `kind-norm` @ko · §18 b2·python b3 `kind-code` plain(기존 code 블록과 같은 형) · b7 statesNorm R-3447+R-3448 · b16 R-3458+R-3459 · b9 norms=[] ✓. s007-6 b1~b10 · s003-2 b10 · s007-1.5 b1~b3 · s005 b17 확장(b18 R-2893 유지) ✓. |
| B-5 | 문면 글자 대조(③ 완성 문안 ↔ ttl) | 검증됨 | **b8~b16 · b5 · §6.1 b1 · §18 b1/b2/b3 · django-skill b17 · web b10 · python b1/b3 = byte 동일.** b7 = §3-1 + Δ4 예외 구절 1문장(92자 · 위치 «#647 ⓓ 후보다» 직후) 삽입 외 동일 · b28 = §3-5 + Δ4 루트 필터 구절 삽입 외 동일 · b6 = §3-5 구절 포함 ✓. web s003-2/b10·s007-6/b9·ddd b10 code = rv1-B §3.7/§3.8 지시대로. |
| B-6 | b7 문장 귀속 경계 | 검증됨 | 문장 1~5(«…분담).» 까지 · «단 dict/Mapping 값 자리…» 는 문장 4 안) = R-3447 · 문장 6 이후(«경계 입력…» — Δ4 예외 구절·#650 문장 포함) = R-3448 — prefLabel 두 개가 각 범위만 요약한다 ✓. |
| B-7 | §18 Section 노드 | 검증됨 | `headingSnapshot "## 18. …"@ko` · `inDocument` · **`sectionNumber "18"`**(기존 60절과 같은 plain literal 형 · 문서 61/61) · `sectionOwner owner-graph` ✓ · rulepack `by_section/…/s094-18` number "18" works [R-3460, R-3461] 실재 ✓. |
| B-8 | `djr:restates` 2 | 검증됨 | §18 b1·b3 → `discipline-houserules/SKILL.md/s007-4/b16` — 대상 Block 실존 ✓. |
| B-9 | wiring 21 | 검증됨 | delegatedTo 12(houserules R-3451~3459 · django R-3460·3461 · web R-3462) · enforcedBy 9(R-3451·3452·**3453**·3455·**3457**·3458·3459 · R-3461 · **R-3448 추가**) — rv3-B §3-10 표(권고 R-3453·R-3457 포함) 와 1:1 ✓. 접촉 wiring 파일 3(조각 1 몫). |
| B-10 | ISSUED 12행 | 검증됨 | `R-NNNN\t2026-09-04\trules/<doc>.ttl` · R-3451~3459 houserules-skill · 3460·3461 django-final · 3462 web-final · `ontology_issued_check` 위반 0 ✓. |
| B-11 | 렌더 개행·표 | 검증됨 | houserules SKILL.md :85~:92 결정표 8블록이 **한 md 표** · :93 b15 뒤 빈 줄 · b16 뒤 빈 줄 → `### §4.1` ✓ · §18 은 «참고 자료» 마지막 항 바로 뒤 헤딩(빈 줄 없음 · 9ef6c4f 동형 · CommonMark 적법) · b3 말미 `\n` = EOF(Δ1 b4 생략) ✓ · web §6 b10 코드 뒤 불릿 + `## 7.` 앞 빈 줄 ✓ · python b3 펜스 뒤 빈 줄 ✓. |
| B-12 | 정본 예시 ↔ mypy 탐침 | 검증됨(이 리뷰가 보강) | 코디 탐침 `canonical_admin.py` 는 `@admin.register(ParentModel)` 없음·주석·식별자 상이(구조는 동일). **정확 b2 블록**을 재검증 → strict green(`mp_probe_rv5b/p18_exact.py` · 주입 = `ChildModel`/`ParentModel` 바인딩 import 2줄만). `readonly_fields = ("version",)`·`inlines = [ChildInline]` 무주석 · `type ParentInlineFormSet` bound · 셋째 인자 생략 · `@admin.register` 전부 통과. |
| B-13 | 규범 정합 8축 | 검증됨 | §2.4 상세 — R-3447 ↔ b16 bound ↔ §18 `Any` 0(주석 2곳만) · R-3154 rev2 ↔ R-3148 «예외 0» 틀 · R-3163 rev2 «관찰(§1 ④)» = SKILL §1:35 «④ 도구·러너(§6.1)» · R-3448 rev2 ↔ R-3443 «타입 좁히기는 값 객체 호출 전 경계 소유» · python §1.5 ↔ §12.0 b6 R-2760(strict)·b7 R-2762(ninja Schema) · 결정표 6행 «입구 밖» ↔ b7 «object 가 사는 자리는 매개변수·지역 변수뿐» · R-0284 «ⓓ 신규(N′∖L′)» ↔ `registry_gate.py:801` 문면 동일 · R-0345 «루트 필터» ↔ 검사기 docstring :54·`RULE_ROOTS` :155. §18 b1 «§1 트리 82행·§5» = houserules final.md 트리 82행 `admin/` · final §5 driven 출구 면제 «admin 은 자기 앱의 모델을 안다» ✓. |
| B-14 | 소스 미러 5 · prose 1 | 검증됨 | ddd `s041-5.5` · web `s004-2`·`s008-6` · python `s008-1.5` · django `s095-18`(append · 마커 없음) — 소스 절 span sha == LEDGER == `sha256(strip_marker(배포 span))` 전수 일치 · prose `s066-13.4` splice 일치 · 소스 절 안 `graph-owned` 마커 0 ✓. `corpus_mirror_sync --check` 11/11. |
| B-15 | codex final.md 4 byte | 검증됨 | `architecture-ddd`(codex `dddjango-architecture-ddd`) · `implementation-django-web` · `implementation-django` · `implementation-python` — `cmp` 동일 ✓. rulepack byte 동일 ✓. |
| B-16 | codex SKILL hand 3 — 본문 | 검증됨 | houserules §4·§4.1·§6.1 본문(마커 제외) byte 동일 · Coordinator b28 `scripts/` 경로 정규화 후 동일 · b6 = 플랫폼 어휘(`spawn_agent`·띄운다) 외 Δ 구절 동일 · implementation-django SKILL §18 행 ✓. |
| B-17 | codex houserules **스킬 참조명** | **MINOR-1** | codex 관례 = 충돌 4스킬(`architecture-ddd`·`discipline-cleancode`·`implementation-test`·`discipline-houserules`)만 `dddjango-` 접두 · 나머지(`implementation-python`·`implementation-django`·`implementation-django-ninja`)는 bare — 같은 파일 :17·:43 이 Claude :20·:48 bare `architecture-ddd` 를 `dddjango-architecture-ddd` 로 치환한 실례. 이번 §4 문면의 **`architecture-ddd §3.1` 3곳(:69 b7 — 09-04 오전 배치부터 bare · :71 b8 · :77 b12 행)** 이 bare. «본문 동일 True» 검증이 이 치환을 놓친다. §3-1. |
| B-18 | b16 «`RedirectView` 는 기본값이 있어 대상 밖» | **MINOR-2** | 스텁 `views/generic/base.pyi:46 class RedirectView(View)` — **비제네릭**(코디 `probe18-summary.md` 도 «비제네릭»). 규범 결과(대상 밖)는 같고 근거 문면만 틀림. §3-2. |
| B-19 | b16 예시 목록 ↔ 검사기 #646 집합 | **MINOR-3** | 검사기 forms 9 = `BaseModelForm`·`ModelForm`·`BaseModelFormSet`·`BaseInlineFormSet`·**`BaseFormSet`·`ModelChoiceField`·`ModelMultipleChoiceField`·`ModelChoiceIterator`·`ModelFormOptions`**(스텁 `ModelChoiceField(ChoiceField, Generic[_M])` default 없음 실확인) — b16 은 admin/forms 4 + CBV 6 만 열거. 레인이 `forms.ModelChoiceField` 맨몸 상속 시 #646 발화 근거를 SKILL 문면에서 못 찾는다(등재 predicates 는 «admin 5·forms 9·CBV 32»). 기준 문장 «기본값이 없는 것들» 이 덮으므로 MINOR. §3-2. |
| B-20 | b28 «세 규칙은 … 루트만» 위치 | **MINOR-4** | #647 괄호 안에 있어 «세 규칙» 의 지시 대상(#646·#647·#650)이 괄호 밖·앞뒤에 흩어진다(Δ4 문안 «신규 3규칙은» 의 «신규» 도 떨어짐). 읽기 모호 — 복원 가능. §3-3. |
| B-21 | b5 rev2 «(적으면 스텁 선언과 같아야 한다 …)» | **MINOR-5** | `inlines` 스텁 = `Sequence[type[InlineModelAdmin[Any, Any]]]` — «같게» 적으면 R-3447 «`Any` 어디에도» 와 충돌하므로 규범 결과는 «적지 않는다» 하나로 일관되나, 괄호가 `Any` 재선언을 허용하는 것처럼 읽힌다. §3-2(b16 정정과 한 번에). |
| B-22 | LEDGER 10행 | 검증됨 | graph 8 + baseline 1 + prose 1 — sha 전수 재계산 일치(B-14) · 사유 열 정확 · 조각 2 몫(command s007 2회째·ninja·api) 미기록 = 계획대로. |
| B-23 | target-counts 5수치 · q4 | 검증됨 | Block 2903→**2917**(+14 = houserules 9 · §18 3 · web 1 · python 1) · Section 546 · Norm/Work 3471(+12) · Expression 3587(+12+7) · q4 3450→3462. 계획 Δ1 의 «조각 1 +16» 은 **계획 오기**(성분 합 14 · 최종 2919 = 14+2 와 정합) — 구현이 맞다. |
| B-24 | rulepack 재소성 | 검증됨 | `works/R-3451…R-3462` label = prefLabel · 개정 7 label 갱신 · `expression` = 새 IRI(`@2026-09-04b` 4) · `by_checker/check-public-surface-annotation.py` 에 R-3447/3448/3451/3452/3453/3455/3457/3458/3459/3461 · `section_number "18"` 4건 중 implementation-django 2(나머지 2 = cleancode·tdd 기존 §18) ✓. |
| B-25 | 등재 3문서 3행 + 집계 | 검증됨 | tree-spec #646/#647/#650(`ast+`·blocker · #650 «확정 위반은 #647 소유») · predicates 3행(#650 = 후보⑴/⑵확정은 #647/물음 · 셀 `\|` 없음) · rule-owner-map 3행 — b7·R-3453·검사기 오라클과 무모순. 집계 `ast+` 57→60 · 계 547→550 · blocker `ast+` 56→59(조각 1 몫 — `ast` 291·433 은 조각 2) · «인용 이력» `:240` 불변 · **#63 행 미접촉**(hunk 4곳뿐) ✓. `spec_lint` 550·ast+ 60·위반 0. |
| B-26 | 도구 재실행 | 검증됨 | `ontology_gate` 90/90 · `ontology_render_sync` 541절 red 0 · `corpus_mirror_sync --check` 11/11 · `spec_lint` 0 · `ontology_issued_check` 0. |

---

## 2. 항목별 상세

### 2.1 정본 ttl(B-1~B-4·B-7~B-10)

- `$S/rv5B/struct_check.py` 출력 요지: Work 19개 전부 `skos:prefLabel` 1개(@ko) · Expression 은 `a djr:Expression ; prov:specializationOf ; [prov:wasRevisionOf] ; djr:revision ; [djr:revisionKind]` 관례형. 개정 7 의 이전 Expression 노드 무변(R-3447/R-3448 `@2026-09-04` rev 1 잔존 · R-0284 rev 1~3 잔존).
- `piece1_ontology.py` 의 `new_block` 이 `ontlib.new_block`(code=@ko) 을 **plain 으로 재정의**해 기존 code 블록 관례(python s007-1.5/b2 · ddd b10 · web b9/b10 전부 plain)와 맞췄다 ✓ — ontlib 원본은 code 를 @ko 로 만들므로 조각 2 에서 ontlib 의 것을 직접 쓰면 어긋난다(§4 사각 1).
- order 연속 단언(`(prev, order, n-1) in g`)과 IRI 미존재 단언이 스크립트에 있어 중간 삽입 0 이 기계적으로 보장됐다.

### 2.2 문면 글자 대조(B-5·B-6) — `$S/rv5B/text_cmp.txt`

```
[DIFF] houserules b7  insert act[1459:1551]=' — 예외는 스텁이 `object` 로 강제하는 프레임워크 콜백·오버라이드의 미러와 이벤트 컬렉션(`list[<Bc>Event]` 로 적을 수 있으면 그것이 답이다)'
[SAME] b8 b9 b10 b11 b12 b13 b14 b15 b16 b5 §6.1-b1 §18-b1 §18-b2 §18-b3 django-skill-b17 web-b10 python-b1 python-b3
[CONTAINS] command b6 구절
[DIFF] command b28  insert act[459:499]=' · 세 규칙은 `application/`·`framework/` 루트만'
```
두 삽입은 계획 Δ4 가 명시한 델타이고 위치·글자가 의도와 맞다(b28 위치는 MINOR-4).

### 2.3 §18 정본 예시(B-12)

- 코디 탐침과 정본의 차이: `@admin.register(ParentModel)` 부재 · `fields = ("mime", "order")`/`readonly_fields = ("id",)` · 주석 4곳. 탐침이 «같은 모양» 인지는 구조상 참이지만 데코레이터는 미검증이었다 → 이 리뷰가 정본 블록 그대로(`git`/ttl 텍스트 추출) 실행: `mypy --follow-imports=silent mp_probe_rv5b` → `Success: no issues found in 1 source file`(spring `pyproject` strict + django plugin + python 3.14 · `enable_error_code ignore-without-code` 포함). 스텁 `decorators.pyi:11 _ModelAdmin = TypeVar(bound=ModelAdmin[Any])` 라 `register` 도 무해.

### 2.4 규범 정합(B-13) — 근거 좌표

| 축 | 좌표 | 판정 |
|---|---|---|
| R-3447 rev2 «어디에도» ↔ b16 «bound 로 적는다» ↔ §18 `Any` 0 | §18 b2 코드에 `Any` 사용 0 · 주석 2곳(«`list[type[InlineModelAdmin[Any, Any]]]` 와 불변성 충돌» · «(`Any` 아님)») 은 스텁 설명 | 무모순 |
| R-3154 rev2 ↔ R-3148 «예외 0» | b1 «예외 0» 은 «달 수 있는 자리» 의 규범이고 b3~b5 는 «문법 부재/달면 오작동 자리» 목록 — rev2 는 그 목록에 항목 추가 · kind `djr:Exception` 유지 · enforcedBy public-surface 유지 · 검사기 `DECLARATIVE_BASE_NAMES` 에 `ModelAdmin`·`TabularInline`·`StackedInline`·`Form`·`ModelForm` 실재 | 무모순(MINOR-5 문면만) |
| R-3163 rev2 ↔ R-3134~3137 | SKILL §1:35 닫힌 목록 «④ 도구·러너(§6.1)» → b1 «관찰(§1 ④)» · «채택은 레인이 도입하지 않는다»(b16) 와 «기능 흐름이 도입하지 않는다»(§6.1) 일치 | 무모순 |
| R-3448 rev2 ↔ ddd §3.1 R-3443 | R-3443 prefLabel «값 객체 안 선언 타입 재검사·강제 변환 금지 — 타입 좁히기는 값 객체 호출 전 경계(Data Mapper·요청 Schema·폼) 소유» ↔ b7 «좁히는 자리는 architecture-ddd §3.1 의 경계 규범대로 값 객체를 부르기 전» | 무모순 |
| python §1.5 ↔ §12.0 | s072-12.0/b6 R-2760 «coercion이 잘못된 입력을 숨기면 strict mode» ↔ b1 «coercion 이 입력을 숨기면 `strict=True` — §12.0» · b7 R-2762 ninja Schema boundary ↔ «HTTP body 는 ninja `Schema`» | 무모순 |
| 결정표 6행 «입구 밖» ↔ b7 | b7 «`object` 가 사는 자리는 … **매개변수**와 … **지역 변수**뿐» ↔ 6행 «입구 밖의 자리표시 `object`(입구 매개변수·즉시 검증 지역 변수는 위 R-3448 · 반환 주석의 `object` 는 ⓓ #647)» · 렌더 md 에 R-번호 표기 선례 실존(ddd final :484~:486 `R-3442`/`R-3443` · command :96·:98) | 무모순 |
| R-0284 rev4 ↔ registry_gate 보고 절 | `registry_gate.py:757 cand_new … # ⓓ 신규(N′∖L′)` · `:801 print("== ⓓ 신규(N′∖L′) n건 · legacy n건 …")` · sidecar `candidate_lines`/`candidate_records`(:293~:294) ↔ b6 ««ⓓ 신규(N′∖L′)» 절·sidecar 레코드 … «ⓓ legacy» 는 건수로만» | 문면 동일 |
| R-0345 rev3 ↔ 검사기 docstring | `:54 #646·#647·#650 은 application/·framework/ 루트 안 파일만` · `:155 RULE_ROOTS` ↔ b28 «세 규칙은 … 루트만» | 무모순(MINOR-4 위치만) |

### 2.5 미러(B-14~B-17)

- 소스 미러 절 키가 preamble 로 서수 +1(`s041-5.5`·`s004-2`·`s008-6`·`s008-1.5`·`s095-18`·`s066-13.4`) 인 채 anchor 기준으로 span sha 일치 — `corpus_mirror_sync._excise_graph_sections` 가 찾는 값 그대로. §18 append 는 `## 18. …\n` + b1 + b2 + b3(마커 없음) · 파일 EOF 개행 1.
- codex houserules SKILL.md: `$S/rv5B` 스크립트로 `## §4`~`### §4.1`·`### §4.1`~`## §5`·`### §6.1`~`### §6.2` 본문(마커 제외) == Claude — **True**. 다만 «본문 동일» 은 codex 이름 관례(MINOR-1)를 검증하지 못하는 기준이다.
- codex Coordinator b6: Claude 와 문장 순서가 하나 다르다(codex 는 «reviewer는 각 test diff hunk…» 가 «기본은 G2 직전 1회…» 앞) — `56b27e1^` 에서도 같은 순서라 **이번 변경 아님**(§4 사각 3).

### 2.6 계수·등재(B-22~B-25)

- 계획 v2 Δ1 «조각 1 +16(houserules 9 · §18 3 · web 1 · python 1)» — 괄호 성분 합 14. 구현 2917 이 맞고 조각 2(+2 = ninja b9 · api b7 · ninja-skill B안 0) 뒤 2919 로 Δ1 최종값과 정합. 계획 문면 정정은 조각 2 계획 갱신 때 1줄.
- 등재 집계는 «조각당 증분» 으로 나눠 반영됐다(ast+ 3 / 계 3) — 조각 2 에서 `ast` 291→293 · 433→435 · 계 550→552 · #63 stale 정정을 마저 해야 한다(계획 Δ3 ⑨ 최종값과 일치 예정).

---

## 3. 정정 문안(전부 MINOR — 정정 커밋 1회에 묶는다)

### 3-1 MINOR-1 · codex `codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md` 스킬 참조명 3곳(hand)

- `:69`(b7) «— implementation-python §1.12 · 좁히는 자리는 architecture-ddd §3.1 의 경계 규범대로» → «… 좁히는 자리는 **dddjango-architecture-ddd** §3.1 의 …»
- `:71`(b8) «도메인 개념은 값 객체(architecture-ddd §3.1)» → «도메인 개념은 값 객체(**dddjango-architecture-ddd** §3.1)»
- `:77`(b12 행) «dataclass·값 객체(architecture-ddd §3.1)» → «dataclass·값 객체(**dddjango-architecture-ddd** §3.1)»
- 유지(bare 가 codex 이름): `implementation-python §1.5/§1.12/§12.0` · `implementation-django §18` · `implementation-django-ninja` §2.1. `references/final.md` 는 byte 미러라 대상 밖. 검증 기준을 «본문 동일» 에서 «본문 동일 ∧ 충돌 4스킬 이름 치환» 으로(조각 2 codex hand 4 에도 적용 — ninja SKILL 의 `architecture-api` 는 codex 도 bare).

### 3-2 MINOR-2·3·5 · `discipline-houserules-skill` s007-4/**b16**·**b5** 문면(in-place · Expression 신설 없음 — 09-04 «⑤ B … 반영(in-place)» LEDGER 선례)

b16 두 구절 교체(나머지 글자 무변):
- «`ListView`·`DetailView`·`CreateView`·`UpdateView`·`DeleteView`·`FormView` 및 그 mixin(`View`·`TemplateView`·`RedirectView` 는 기본값이 있어 대상 밖).» → «`ListView`·`DetailView`·`CreateView`·`UpdateView`·`DeleteView`·`FormView` 및 그 mixin, 그리고 `BaseFormSet`·`ModelChoiceField` 같은 폼셋·폼 필드 기저다(`View`·`TemplateView` 는 기본값이 있고 `RedirectView` 는 제네릭이 아니라 대상 밖 · 전수는 #646 집합 — django-stubs 6.1.0 기준).»

b5 괄호 교체:
- «(적으면 스텁 선언과 같아야 한다 · 선언적 클래스 본문의 메서드는 면제가 아니다)» → «(달 수 있는 자리라도 스텁 타입과 같아야 하고 그 타입에 `Any` 가 있으면(`inlines`) 달 수 없다 · 선언적 클래스 본문의 메서드는 면제가 아니다)»

절차: rdflib `set_text`(@ko 유지) → canon → `ontology_gate` → `ontology_render --apply discipline-houserules-skill` → LEDGER `discipline-houserules-skill s007-4` 재기준선 1행(사유 «⑤-1 B MINOR-2/3/5 반영(in-place)») → **`make rulepack`**(`built_from` 가 ttl sha 를 추적하므로 label 무변이어도 재소성 · codex byte) → codex houserules §4 hand(3-1 과 함께) → `corpus_mirror_sync --check`(SKILL 은 소스 미러 없음) → `make verify`. prefLabel R-3458/R-3154 는 무변(명칭 요약 범위 안).

### 3-3 MINOR-4 · `command-dddjango` s007/**b28** 구절 위치(in-place · 같은 절차 · LEDGER `command-dddjango s007` 재기준선 · codex Coordinator :150 hand)

«…`json.load(s)` 무검증 흐름은 ⓓ #650 · 세 규칙은 `application/`·`framework/` 루트만)·Thin Read 반환(#358)·계약 검증 토큰(#456).» → «…`json.load(s)` 무검증 흐름은 ⓓ #650)·Thin Read 반환(#358)·계약 검증 토큰(#456) — 신규 3규칙(#646·#647·#650)은 `application/`·`framework/` 루트만.»
(조각 2 가 같은 절 s007 을 다시 렌더하므로 조각 2 편집 스크립트에 합쳐도 된다 — 단 HEAD ttl 재로딩 · Δ13.)

---

## 4. 사각(이 리뷰가 닫지 못한 것 · 조각 2/⑥ 입력)

1. **`ontlib.new_block` 의 code 리터럴 언어**: 원본은 code 를 @ko 로 만든다(조각 1 은 `piece1_ontology.py` 가 plain 으로 재정의). 조각 2 는 code 블록 신설이 없어 무해하나, ontlib 을 재사용하는 후속 작업은 `kind in ("table-row","code")` → plain 으로 ontlib 자체를 고치는 편이 안전(scratchpad 도구 — 실서고 밖).
2. **b16 «및 그 mixin» 의 범위**: 검사기 CBV 32 는 `SingleObjectMixin`·`MultipleObjectMixin`·`FormMixin`·`ModelFormMixin`·`DeletionMixin` 과 dates 계열 14 를 포함 — 3-2 문안의 «전수는 #646 집합» 으로 덮이지만, 레인이 dates 계열(`ArchiveIndexView` 등)을 쓰는 순간 SKILL 에 이름이 없다. 실전 사용 0(⓪ 실측) 이라 이월.
3. **codex Coordinator b6 문장 순서**(§2.5) — 조각 2 codex hand 때 Claude 순서로 정렬할지 선택(내용 동일 · 의미 미러 허용 범위).
4. **web 예시 import 순서**: s003-2/b10·s007-6/b9 의 `from typing import TYPE_CHECKING, TypeAlias` 가 django import 뒤(isort 형) — §18 예시는 stdlib→django 순. 예시는 lint 대상 아님(b6) · 미관 · 레인이 복사하면 ruff I001 이 잡는다. 조각 2 밖 · 다음 web 레인 접촉 때 정정.
5. 규범 축 밖 관찰: `workspace/eval/ab/T2-0b-manifest.json`·`2026-08-20-ontology-t2-0b-design.md` MANIFEST-FACTS 가 설치본 2.17.17 기준 **draft** 로 갱신됨(`manifest_seal --write` 부수 효과 · cache_parity drift) — 릴리즈 뒤 docs(seal) 몫. `tree-revision-spec` #650 «어겼을때 blocker»(ⓓ 전용 · #644 선례) 는 spec_lint 통과. Δ15 web SKILL.md 이월은 계획대로 미접촉.

— 끝. 산출: `$S/rv5B/{struct_check.py,text_cmp.py,text_cmp.txt,ledger_check.py,diff-*.txt}` · `$S/spring/mp_probe_rv5b/p18_exact.py`(정본 §18 b2 그대로 + 바인딩 import 2줄 · mypy strict green).
