# 현장 보고 3 · ③ 계획 리뷰 — 리뷰어 B(규범 축: 온톨로지 정본·문안·배선·소유) · 2026-09-04

- 대상: `2026-09-04-field-report-repair-3-plan.md` §0~§7(중심 §1·§1.11·§3·§6·§7) · 문안 정본 `rv1/rv1-B.md` §3.1~§3.15·§5 · 루브릭 «1단계 결과»·«3·5단계 3축».
- 방법: 정본 ttl 을 rdflib 로 블록·Expression 단위 덤프(`$S/map/blocks.py` · `$S/rv3B/*.txt`)해 IRI·order·statesNorm·현행 날짜·kind 를 실확인 · wiring 전수 grep · 선례 커밋 9ef6c4f(새 절)·수리 2 계획 Δ 판형·LEDGER/ISSUED 형식·`corpus_mirror_sync`/`ontology_render`/`ontology_census`/`query_golden_check` 코드 대조 · **격리 사본에서 mypy strict 탐침 5파일**(`$S/rv3B/probe/` · 실행은 `$S/spring/mp_probe_rv3b/` · spring venv mypy 2.3.1 · pydantic 2.13.4 · Python 3.14 — 실서고 무접촉) + pydantic 런타임 탐침 1.
- 판정 값: 검증됨 / MINOR / MAJOR / BLOCKER. **BLOCKER 0 · MAJOR 6 · MINOR 13**. 
- IRI 접두: `<https://numchida.com/ns/djr#s/dddjango/…>` 는 `…/<doc>/<sNNN>/bN` 으로 줄인다. `$S` = `scratchpad/fr3`.

Serena: skipped — 워크트리에 `.serena/project.yml` 없음(기본 도구 + rdflib).

---

## 1. 판정 표

| # | 항목(계획 절) | 판정 | 한 줄 |
|---|---|---|---|
| B-1 | §1.3 django-skill s005 «새 b18» | **MAJOR-1** | **b18 이 이미 있다** — `implementation-django-skill s005/b18`(kind-norm · R-2893 «각 절은 references/final.md 에서 필요한 항목만 읽는다» · 렌더 `SKILL.md:57`). 새 행을 b18 로 넣으면 IRI 재명명(중간 삽입 — 계획 자신의 «중간 삽입 0» 위반·수리 2 Δ1 BLOCKER 선례)이고, b19 로 append 하면 표가 산문 뒤에 붙어 표가 끊긴다. rv1-B §2.2·§3.5 «b17 뒤 b18» 도 같은 착오. Δ = **b17 텍스트를 2행으로 확장**(한 블록 여러 행 선례: django-web s003-2/b3 머리+구분행). |
| B-2 | §1.2 b2 정본 예시 strict 통과(§7-1) | **MAJOR-2** | 탐침 red 1: `_ChildFormSetBase = BaseInlineFormSet[ChildModel, ParentModel, "ChildInlineForm"]` → `class ChildInline: formset = ChildInlineFormSet` 이 `[assignment]`(스텁 `InlineModelAdmin.formset: type[BaseInlineFormSet[_C, _P, ModelForm[_C]]]` — 셋째 매개변수 불변). **셋째 인자를 생략**(기본값 `ModelForm[_M]`)하면 green(변형 ① 실증) — 전방 참조 문자열도 함께 사라진다. 그 밖 전부 green: 무주석 `readonly_fields`·`inlines`·`model`/`form`/`formset`/`extra` · `type ParentInlineFormSet = …[Model, Parent, ModelForm[Model]]` bound · `save_model`/`save_related`. b3 문면은 «생략할 수 있다»가 아니라 **«적지 않는다 — 구체 폼을 적으면 formset 자리와 충돌»**로. |
| B-3 | §1.11 절차 순서·LEDGER 산식·새 절 시드 | **MAJOR-3** | (a) LEDGER 행의 sha 산식이 계획에 없다 — 실측: graph 절의 baseline/rebaseline sha = **`sha256(strip_marker(렌더 span))` = 소스 미러 절 span**(9ef6c4f `s018-5` = `8f4da3f8…` = src span · dep span 은 `a1008450…`). `corpus_mirror_sync._excise_graph_sections` 가 **이 sha 로 소스 절을 찾으므로**(:168~171) 배포 span sha 를 적으면 exit 3(STRUCTURE). (b) 새 절은 `ontology_render --apply` 전에 **md 헤딩+마커 시드**가 있어야 한다(`apply_to_corpus:96` «현재 분할에 절 없음») — §1.2 에는 있고 §1.11 단계 목록에는 없다. (c) 소스 미러 append 는 **마커 없이** `## 18. …\n` + 블록 본문(9ef6c4f 동형). (d) prose §13.4 md 직접 수정과 그 LEDGER prose 행(sha = 배포 span)의 시점이 §1.11 에 없다. |
| B-4 | §1.1 b7 델타 «#650» 문면 ↔ §2.1 오라클 | **MAJOR-4** | 계획 델타 «`json.load(s)` 결과가 `Any`/`dict[str, Any]` 주석·반환·컴프리헨션으로 흐른 자리는 ⓓ #650» 는 검사기 오라클(§2.1: 주석≠`object` · 반환 주석≠`object` 함수의 Return · 컴프리헨션 · 직접 첨자/속성 · 리터럴 컨테이너 요소 · 후보 아님 = `x: object` · 호출 인자)보다 **좁다** — `payload: dict[str, str] = json.loads(raw)` 는 검사기 후보지만 문면 밖이라 감수자가 물음의 근거를 잃는다. R-0284 rev4(§3.9 b6)의 #650 구절도 같은 축약. Δ = 오라클 정합 문안(§3-1 최종형). |
| B-5 | §1 prefLabel 갱신 전수 | **MAJOR-5** | 계획은 R-3447/R-3448 만 «prefLabel 갱신». 개정 9 전부 prefLabel 이 바뀌어야 한다 — **rulepack 이 레인에 주입하는 «명칭» = `skos:prefLabel`**(`ontology_rulepack.py:10·134` · 동결 개정 8 «번호·명칭») 이라 stale 명칭이 곧 stale 주입이다. 특히 R-0345(registry #11 — #646·#647·#650 부재)·R-0349(#648·#649)·R-0284·R-3154·R-3163·R-2715·R-0331. 문안 §3-9. |
| B-6 | §1.2 Section 노드 필드 | **MAJOR-6** | `implementation-django-final` 의 번호 절 60/60 이 `djr:sectionNumber` 를 가진다(`s079-16.5` → `"16.5"`). **q3-section-bundle.rq 가 `djr:sectionNumber` 로 FILTER**(`:15·:21`)하고 rulepack `section_number`(`:137`)·`derive_path_globs`(`:82`)가 이 키를 쓴다 — 계획의 «headingSnapshot·inDocument·sectionOwner» 만으로는 §18 이 q3 에서 보이지 않는다. 9ef6c4f(houserules-final s018-5)도 빠뜨렸으나 그 문서는 anchor 절 3/… 만 보유하는 예외. Δ = `djr:sectionNumber "18"`(xsd:string). |
| B-7 | §1 신설 17 kind | MINOR-1 | kind 가 적힌 것은 4(R-3458·R-3459·R-3463·R-3465)뿐. 문안 기준 표 §3-10 — Prohibition 4(R-3451·R-3459·R-3463·R-3465) · Obligation 13. 선례: 표 행 R-2267~R-2271(Obligation 4 · «몰아넣지 않는다» 행만 Prohibition) · api R-1967~ Obligation · SKILL 불릿 R-2945 Obligation. |
| B-8 | §1 ISSUED 행 | MINOR-2 | 형식 `R-NNNN\tYYYY-MM-DD\trules/<doc>.ttl`(`ontology_issued_check` ROW_RE · 연속 증가·결번 금지 · 파일에 Work IRI 실재). 계획은 «ISSUED append» 만 — 파일 열 전수 §3-11(조각 1 = R-3451~R-3462 · 조각 2 = R-3463~R-3467 — 조각 순서와 연속성 정합). |
| B-9 | §1.1 «b7 말미 개행 조정» | MINOR-3 | **불필요·위험** — b7 은 지금도 `\n\n` 으로 끝나고(문단 뒤 빈 줄 = 선행 블록 소유 · authoring §13) b8 이 문단이라 그대로 둔다. `\n` 으로 «조정»하면 b7·b8 이 한 문단으로 렌더된다. 개행 소유 전수: b7 `\n\n` 유지 · b9 머리 2행 `\n` · b10~b14 `\n` · **b15 `\n\n`**(표 뒤 빈 줄) · **b16 `\n\n`**(§4.1 헤딩 앞). 선두 `\n` 유지 대상: s011-6.1/b1 · python s007-1.5/b1 · **§18 b1(선두 `\n` — 마커 뒤 빈 줄)**. |
| B-10 | §1.9 ninja-skill s004 새 불릿 | MINOR-4 | 누락 3: b17(현 마지막 · `\n\n`) → `\n` 이관 · R-3466 wiring(delegatedTo design-review-api·discipline-reviewer — rv1-B §3.15) · kind. 위치 권고: 새 b18 은 «라우팅 결정 전 …(§11)» 뒤라 주제가 멀다 — **b12(«반환 타입을 명시한다(`object` 금지) (§2.2)» · restates final b12·b13) 확장** + `statesNorm += R-3466` + `restates += s009-2.2/b1, s012-3.1/b9` 가 주제 인접·블록 수 불변. 둘 다 적법 — §3-8 A/B. |
| B-11 | §1.7 R-0284 rev4 ⓔ2 델타 | MINOR-5 | b6 에 «해당 범위 실행분» 이 **2곳**(registry #4 ⓓ · #11 ⓓ)이고 ⓔ2 는 ⓓ 라인 전부(`[ⓓ#\d+]` — findings.py:273 형식 · 검사기 무관)를 N′∖L′ 로 가르므로 한 곳만 바꾸면 #4 채널이 옛 범위로 남는다. Δ = 두 채널을 한 구절로 묶은 문안(§3-5) + §2.4 가 보고 절 이름을 «ⓓ 신규(N′∖L′)»·«ⓓ legacy n건» 으로 고정해 b6 이 그 이름을 인용. |
| B-12 | §1.7 R-0331 rev2(ⓔ1) 정합·소급 | MINOR-6 | Work 귀속은 R-0331 이 맞다 — 반송은 Coordinator 행위라 delegatedTo command-dddjango(R-0331 현행 배선) · R-0332 는 enforcedBy 5검사기 · R-0333 «auto 는 증거 아님» 과 방향 일치. 정합 근거 좌표 정정: rv1-B «design-architect :63» 은 **API 스택** 항목이다 — 맞는 앵커는 **:39**(«Ninja endpoint/error contract/response Schema 를 새로 만들거나 바꾸는 scope 라면 12-slot 적용») · **:41·:48**(slot 3 `error profile`) · acceptance-tester **:41**(«12-slot/profile 이 빠지면 설계로 반송»). 소급 없음: 문면이 «이번 산출물의 컨트롤러» 한정 → 리딩 refactor-scope 의 과거 auto 실행은 대상 밖 · brownfield update 잎이 오류 선언 컨트롤러를 손대면 :39 «바꾸는 scope» 라 반송이 맞다. 날짜 접미: R-0331 현행 `@2026-08-22` rev1 → rev2 는 **`@2026-09-04`(무접미)**. |
| B-13 | §1.4 web §6 새 b10 «코드 뒤 규범» | 검증됨(+MINOR-7) | 허용 — 선례 실존: `implementation-django-final s087`(b1 code → b2 prose → **b3 norm** ⚠ 불릿 → b4 prose). ninja 에서 b18(code) 뒤 append 를 기각한 이유는 «같은 주제 블록(b1 R-0671/R-0672 `response=` 선언)이 실존」이었지 코드 뒤 금지가 아니다 — web §6 은 `ModelForm` 기저 선언을 소유한 불릿이 없다(b4 `Meta.fields` 는 필드 목록). 일관성 문장을 §1.4 에 한 줄 남기고, b10 문면은 s087/b3 처럼 **«위 `ArticleForm` 의 `_ArticleFormBase` …» 지시형**으로(§3-4). s003-2/b10 정정은 FBV·`StaffRequiredMixin` 과 무충돌(비제네릭) · **탐침 green**(`ListView[Article]`·`CreateView[Article, ArticleForm]`·`UpdateView[Article, ArticleForm]`·`ModelForm[Article]` 별칭 4). |
| B-14 | §1.8 ninja b13 확장·b9 위치·b1 확장 | 검증됨(+MINOR-8) | b13 «한 블록 두 Work» = 수리 2 Δ1(s025-5.5/b24 + R-3450) 선례 ✓ · R-0687(Obligation·enforcedBy public-surface) 와 R-3463(Prohibition·enforcedBy api-error-controller) 동거 ✓ · b13 말미 `\n` 유지(b14 뒤따름). s012-3.1 새 b9: b8 은 **문단**(validator 입장 심사)이라 그 뒤 불릿 b9 는 고아 불릿 — 렌더는 적법(문단 뒤 새 목록) · 선택: 굵은 선두 **문단형**으로 써서 b8 과 같은 꼴(§3-7). b1 확장은 경질 개행 관례(ninja) 유지 · `\n\n` 유지. |
| B-15 | §1 wiring 전수 | MINOR-9 | 계획과 rv1-B §3.15 일치(houserules R-3451~3459 · django R-3460·3461 · web R-3462 · ninja R-3463~3465 · api R-3467) — **R-3466 누락**(B-10). 정합 권고: 결정표 2행 R-3453(#650 ⓓ)·6행 R-3457(#647 반환 `object` ⓓ)에도 `enforcedBy public-surface` — R-3448 에 «부분 집행(후보 채널)» 근거로 enforcedBy 를 추가하는 계획 자신의 기준과 같다. 접촉 wiring 파일은 **6**(houserules-skill·django-final·web-final·ninja-final·ninja-skill·api-final) — «10» 은 rules 수. `aliases.ttl` 은 무접촉(#645·#493 도 대장 밖 — AliasEntryShape 30 불변). |
| B-16 | §1.11 target-counts·q4 | MINOR-10 | 수치 확정(계획 그대로): BlockShape 2903→**2922**(+19 = houserules 9 · §18 4 · django-skill 1 · web 1 · python 1 · ninja 1 · ninja-skill 1 · api 1) · SectionShape 545→**546** · NormShape/WorkShape 3459→**3476** · ExpressionShape 3568→**3594**(+17 신설 +9 개정). Δ 반영 시(B-1 b17 확장 −1 · B-19 b4 생략 −1 · B-10 B안 −1) BlockShape **2919**. 조각별: 조각 1 = Norm +12 · Expr +19(12+7: R-3447·3448·3154·3163·2715·0284·0345) · Block +14~16 · Section +1 / 조각 2 = Norm +5 · Expr +7(5+2: R-0349·R-0331) · Block +2~3. q4 `distinct_works`/`rows` **+17**(3450→3467 — 현 골든 값은 `--emit` 결과로). |
| B-17 | §1.11 LEDGER 행 수 | MINOR-11 | **15행**: graph 재기준선 13(houserules-skill s007-4 · s011-6.1 · django-skill s005 · web s003-2 · s007-6 · python s007-1.5 · ddd s040-5.5 · command s007 ×2(조각 1·2) · ninja-final s009-2.2 · s012-3.1 · ninja-skill s004 · api s022-5.2) + baseline 1(django-final s094-18) + prose 1(django-final s065-13.4 — 현행 sha `9b88f235…` 로 부식 검사가 잡으므로 md 수정 즉시 append). |
| B-18 | §3 미러 전수·회신 3 | 검증됨(+MINOR-12) | SKILL hand 4 좌표: codex houserules = **`codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md`**(§4 :57 · b5 :65 · b7 :69 · 새 블록 9 · **§6.1 :81** — 계획은 «§4» 만 언급) · Coordinator `dddjango/SKILL.md` :125(step 5)·**:136(scope별 실행 — 계획 누락)**·:150(registry 11)·:154(registry 15) · `implementation-django/SKILL.md` :50 · `implementation-django-ninja/SKILL.md` :30/:35. final byte 6·검사기 byte 3·rulepack 2·소스 미러(prose §13.4 는 `--write` 가 splice) ✓. 회신 3 항목 8(rv1-B §5-13) ✓ §4-5. **R-12 문구(rv1-B §3.15)가 계획에 없다** — 9a258bf 선례대로 로드맵 R-12 행 «반영 문구» 추기를 §4-5 에. |
| B-19 | §1.2 b4 `---` | MINOR-13 | 문서 말미 절이라 `---` 가 EOF 에 매달린다(현 파일은 `…/)\n` 으로 끝나며 «참고 자료» 뒤 구분선 없음 · 9ef6c4f 도 없음). 권고: b4 생략 · b3 말미 `\n`(EOF 개행 1). 유지해도 적법. |
| B-20 | §1.1 b5 R-3154 rev2 · b1 R-3163 rev2 정합 | 검증됨 | R-3154 는 `djr:Exception`(enforcedBy public-surface — 유지) · R-3148 «예외 0»/R-3151 «문법 없는 자리뿐» 틀과 무모순 — 기존 3항(모델 필드·Meta·enum)도 문법상 달 수 있는 자리를 «달면 오작동» 으로 묶은 것이고 rev2 도 «재선언이 불변성 red» 로 같은 틀 · 검사기 `DECLARATIVE_BASE_NAMES`(`ModelAdmin`·`TabularInline`·`StackedInline`·`Form`·`ModelForm`)와 문면 일치 · R-3155(`x: T` 필수 = pydantic·Schema·dataclass — admin 아님) 무충돌 · 탐침 A 가 «무주석이 green」 실증. R-3163 rev2 는 R-3134 닫힌 목록 «④ 도구·러너(§6.1)» 의 문면 그대로(«관찰(§1 ④)») — R-3135~3137 과 정합. 둘 다 `@2026-08-22` rev1 → rev2 `@2026-09-04`(무접미) · amendment. |
| B-21 | §1 개정 9 revisionKind·날짜 | 검증됨 | 현행 실확인: R-3447·R-3448·R-0284(rev3)·R-0345(rev2) = `@2026-09-04` → 오늘 개정이면 **`@2026-09-04b`**(선례 `@2026-09-03b` R-3427 rev3) · R-0349·R-0331·R-3154·R-3163·R-2715 = `@2026-08-22` rev1 → `@2026-09-04`(무접미). revisionKind: R-3448 만 redefinition(JSON 처방 교체 — 어휘 실존·선례 R-0086/R-0087) · 나머지 amendment ✓. Expression 노드 = `a djr:Expression ; prov:specializationOf ; prov:wasRevisionOf <이전> ; djr:revision n+1 ; djr:revisionKind`(ExpressionShape 는 revision·specializationOf 만 요구 — 나머지는 관례). §7-5 그대로: 커밋일이 넘어가면 그날 첫 개정이라 전부 무접미. |

---

## 2. 항목별 상세

### 2.1 B-1 — django-skill s005 b18 실존 (MAJOR-1)

- rdflib: `implementation-django-skill s005/b17 = "| Django 5.x 새 기능 | §17 |\n\n"` · **`s005/b18` order=18 kind-norm statesNorm R-2893 `"각 절은 [references/final.md](…)에서 필요한 항목만 읽는다(전체 로드 불필요).\n"`** · 렌더 `dddjango/skills/implementation-django/SKILL.md:55·:57` · codex `:50·:52`.
- 대안 셋: ① b18 삽입 + 기존 b18→b19 재명명 — IRI 재명명 선례 0·계획 §1 «중간 삽입 0» 자기 위반 · ② b19 append — 표(b3~b17) 뒤에 산문(b18)이 있고 그 뒤에 표 행이 오면 markdown 이 새 표를 시작(머리행 없음 → 표로 렌더되지 않음) · ③ **b17 확장**(2행 1블록 · kind-table-row xsd:string · norms=[]) — 선례 django-web s003-2/b3(머리+구분행 2줄 1블록) · 수리 2 Δ1(2불릿 1블록). ③ 채택. b17 의 `\n\n` 은 그대로 마지막 행 뒤에 남는다(b18 산문 앞 빈 줄).
- 계수: BlockShape 증분에서 −1.

### 2.2 B-2 — §18 b2 정본 예시 (MAJOR-2 · 탐침 `$S/rv3B/mypy_rv3b_probe.txt`)

- 실행: `cd $S/spring && <spring venv>/mypy mp_probe_rv3b/`(pyproject strict + django plugin + `python_version=3.14`). 결과 **1 error / 5 files**:
  `p18_admin.py:44: error: Incompatible types in assignment (expression has type "type[ChildInlineFormSet]", base class "InlineModelAdmin" defined the type as "type[BaseInlineFormSet[MediaModel, CharacterModel, ModelForm[MediaModel]]]")  [assignment]`
- 뿌리: 스텁 `contrib/admin/options.pyi` `InlineModelAdmin[_ChildModelT, _ParentModelT].formset: type[BaseInlineFormSet[_ChildModelT, _ParentModelT, ModelForm[_ChildModelT]]]` — `BaseInlineFormSet` 의 셋째 매개변수(`_ModelFormT`)는 불변이라 `ChildInlineForm`(하위) 으로 특수화한 formset 은 대입 불가. rv1-B §3.5 b2 의 `BaseInlineFormSet[ChildModel, ParentModel, "ChildInlineForm"]` 는 «정확 타입」 의욕이 과했다. 변형 ① `_ChildFormSetBase2 = BaseInlineFormSet[ChildModel, ParentModel]`(셋째 생략) 은 green.
- 따라서 b2 는 **셋째 인자 생략 + 전방 참조 문자열 삭제 + 주석 1줄(«셋째 인자는 적지 않는다 — 기본값 ModelForm[ChildModel] 만 admin.formset(불변)과 맞는다»)**, b3 는 «생략할 수 있다» → «적지 않는다 — 적으면 `formset = …` 이 `[assignment]`». 이 배움은 레인이 가장 자연스럽게 저지를 모양(구체 폼을 적는 것)이라 예시 본문에 남긴다.
- 나머지 green 실증(계획 §7-1 의 세 우려 전부 해소): `readonly_fields = ("id",)` 무주석(스텁 `ClassVar[_ListOrTuple[str]]`) · `inlines = [ChildInline]` · `model`/`form`/`formset`/`extra` 무주석 · `type ParentInlineFormSet = BaseInlineFormSet[Model, ParentModel, ModelForm[Model]]` · `save_model(form: ModelForm[ParentModel])` · `save_related(formsets: Sequence[ParentInlineFormSet])`.
- 같은 탐침에서 green: **python §1.5 b3**(PEP 695 alias + `TypeAdapter[Coordinate]` + 재귀 `JsonValue` + `to_json_value` 브리지 · `warn_unreachable` 포함) · **web CBV 별칭 4** · **ddd `FieldValue`**(`value not in definition.choices` strict-equality 무경고). 런타임(`runtime_rv3b_probe.txt`): pydantic 2.13.4 가 `type` 문 union 을 `TypeAdapter` 로 받아 `validate_json(strict=True)` 성공·문자열 `"1"` 거부·TypedDict → 브리지 통과. 음성 탐침(`mypy_rv3b_neg.txt`): TypedDict → `JsonValue` red · → `dict[str, object]` red · → `Mapping[str, object]` **green** — R-2715 rev2 의 «`JsonValue`·`dict[str, object]` 자리에 못 들어간다」 문면은 정확(`Mapping[str, object]` 를 거기 넣으면 틀린다 — 그대로 둔다).

### 2.3 B-3 — §1.11 절차 (MAJOR-3)

실측 산식(`$S`/이 리뷰 스크립트 · LEDGER 마지막 유효 행 기준):
- `discipline-houserules-final s018-5`(9ef6c4f 신설) — ledger `8f4da3f8…` = **src span**(`## §5 …\n\n` + 본문 · 마커 없음) · dep span(마커 포함) = `a1008450…`.
- `architecture-ddd-final s023-3.6`(09-04 재기준선) — ledger `7c24f09e…` = src `s024-3.6`(preamble 로 서수 1 밀림) span · dep ≠.
- `implementation-django-final s065-13.4`(prose) — ledger = dep span = src `s066-13.4` span(마커 없으니 동일).
- 그리고 `corpus_mirror_sync.write_skill` 은 그래프 절을 **소스 원문 스팬으로 되치환·보존**(:240~:247)하므로 `--write` 가 소스 절을 갱신하지 않는다 — 소스 절 교체는 수동(메모리 «ontology-revision-recipe» 5 와 일치). 순서 확정(§4 Δ B-3):

  0. **md 시드**: `dddjango/skills/implementation-django/references/final.md` 말미에 `## 18. Django admin·폼 타이핑 — django-stubs 제네릭 기저\n` + 마커 1행(직전 행 `…/)\n` 뒤 · 빈 줄 없이 — 9ef6c4f 동형).
  1. rdflib 편집 → canon roundtrip → `ontology_gate` → `ontology_render --apply <doc…>`.
  2. **prose §13.4** md 직접 수정(:1328 판형) — 그래프 절과 같은 파일이므로 렌더 뒤·미러 전.
  3. **소스 미러 수동 교체/append**: graph 절마다 `workspace/reference/<skill>/reference/final.md` 의 옛 절 span(HEAD 에서 추출)을 `strip_marker(렌더 span)` 으로 교체 · §18 은 append(마커 없음).
  4. **LEDGER**: graph 재기준선 13행 + baseline 1행 = `sha256(strip_marker(렌더 span))`(= 3 의 src span 과 byte 동일이어야 함 — 스크립트로 양쪽 계산·대조) · prose 1행 = `sha256(배포 span)`.
  5. ISSUED append → target-counts → `query_golden_check --emit` → `make rulepack`.
  6. `corpus_mirror_sync --check` 0 → `--write`(codex final byte 6) → codex hand 4 → `spec_lint` 0 → `make verify`.
- 계획의 «LEDGER → … → 소스 미러 span 교체» 순서는 sha 를 `strip_marker(렌더 span)` 으로 계산하면 결과가 같아 치명적이지 않지만, **산식이 계획 문면에 없다** — 배포 span 으로 적으면 6 에서 STRUCTURE exit 3.

### 2.4 B-4 — b7 델타 #650 문면 (MAJOR-4)

- §2.1 #650 오라클: «`json.load|loads` 결과가 AnnAssign 주석≠`object` / 반환 주석≠`object` 함수의 Return / 컴프리헨션 요소 / 직접 Subscript·Attribute 접근 / 리터럴 컨테이너 요소로 흐르면 후보 · 비후보 = `x: object = …` · 호출 인자 · 무주석 Assign(#493 몫)». 물음 «`TypeAdapter(<TypedDict>)`로 검증하며 받았거나 `x: object` 로 받아 즉시 좁혔는가».
- 계획 §1.1 델타 «`Any`/`dict[str, Any]` 주석·반환·컴프리헨션» 는 (i) `dict[str, Any]` 주석은 #647 이 차단하는 자리라 #650 의 대표 형상으로 부적절(#647·#650 이중 발화는 술어가 달라 적법하나 문면이 #650 을 #647 의 그림자로 만든다) (ii) 직접 접근·리터럴 컨테이너·«`object` 아닌 구체 주석」 형상이 빠진다. 규범 문면이 검사기보다 좁으면 감수자가 후보 절반을 «문면에 없는 물음」으로 받는다(spring 41 중 `dict[str, Any]` 주석 아닌 형상이 몇인지는 A/C 실측 몫).
- R-0284 rev4(§3.9 b6)의 «#6NN — `json.load(s)` 결과가 `Any`/`dict[str, Any]` 주석·반환·컴프리헨션으로 흐른 자리」 도 같은 문면 — registry 행은 요약이라 «무검증 흐름」 한 구로 족하다(R-0345 rev3 이 이미 그렇게 씀). 최종형 §3-1·§3-5.

### 2.5 B-5 — prefLabel 9 (MAJOR-5)

rulepack 이 주입하는 `<rules>` 항목은 «번호·명칭」이고 명칭 = `skos:prefLabel`(`ontology_rulepack.py:10 «명칭(skos:prefLabel — E5 가 «명칭만»으로 못박은 필드)»` · `:134 "label"`). 개정 9 중 문면이 늘어난 것은 전부 명칭이 바뀌어야 레인이 주입에서 새 규칙(예: registry #11 에 #646·#647·#650)을 본다. 문안 §3-9. 길이는 현행 R-3448 prefLabel(2줄) 수준까지 허용된 선례.

### 2.6 B-6 — sectionNumber (MAJOR-6)

`ontology_migrate.py:148` 은 census anchor 가 있는 절마다 `sectionNumber` 를 부여했고 django-final 은 60/60(«## N.»·«### N.M»)이 가진다. `q3-section-bundle.rq:15` 는 `?section djr:sectionNumber ?sectionNumber` 를 **필수 패턴**으로 두므로 없는 절은 q3 에서 0행. `derive_path_globs.py:82` 도 이 키로 절을 찾는다. §18 은 anchor «18」 절이므로 `djr:sectionNumber "18"` 을 Section 노드에 둔다(xsd:string · SectionShape maxCount 1). 9ef6c4f 가 빠뜨린 것은 그 문서(houserules-final) 절 대부분이 무번호라 눈에 띄지 않았을 뿐 — 선례로 삼지 않는다.

### 2.7 B-9·B-13·B-14·B-19 — 블록 경계·위치

- authoring §13: «블록 간 구분자는 선행 블록의 후행 스팬에 귀속 · 절 선두 구분자는 첫 블록 선두 스팬」. 렌더 = 헤딩 + `\n` + 마커 + `\n` + 블록 연결(`ontology_render.py:79`) → 마커 뒤 빈 줄은 첫 블록의 선두 `\n`. 현행: s007-4/b1 `\n**모든…` · b7 `…object]`.\n\n` · s011-6.1/b1 `\n표준 도구셋…\n\n` · python s007-1.5/b1 `\n외부 API…\n\n` · api s022-5.2/b6 `…포함한다\n\n` · ninja-skill s004/b17 `…먼저 (§11)\n\n` · web s007-6/b9 code `…```\n\n`.
- «코드 뒤 규범」 선례: django-final s087(b1 code · b3 norm R-1366/R-1367 «⚠ 위 `OrderItem` 은 …») — web §6 b10 은 정확히 이 꼴(«위 `ArticleForm` 의 별칭은 …»). ninja s009-2.2 는 b1 이 `response=` 선언을 소유하므로 그 확장이 «한 주제 한 자리」 — 둘은 모순이 아니라 «소유 블록이 있으면 확장, 없으면 코드 뒤 주석형 규범」 이라는 같은 기준이다. 계획 §1.4 에 이 한 줄을 남긴다.
- s012-3.1: b7(불릿·`\n\n`) → b8(문단·`\n\n`) → 새 b9. 불릿이면 문단 뒤 새 목록 1개짜리 — 적법·선례(ninja s009-2.2 b15 문단 뒤 b16 불릿). 문단형으로 쓰면 b8 과 같은 꼴 — 선택.

### 2.8 B-11·B-12 — Coordinator

- registry_gate 현행: `_FINDING_RE = ^\s*(\[#\d+\].*)$`(:94) · ⓓ 라인은 `[ⓓ{rule}] {where}: {msg} — 물음: {q}`(findings.py:273) → 계획 §2.4 `_CANDIDATE_RE = ^\s*(\[ⓓ#\d+\].*)$` 가 맞다. 보고 어휘는 «귀속 = N∖L · legacy 잔존(L∩N)」 이므로 ⓓ 는 «ⓓ 신규(N′∖L′) · ⓓ legacy(L′∩N′)」 로 이름을 고정하고 b6 이 그 이름을 쓴다. registry #4(check-layer-skeleton)의 ⓓ 도 같은 파서를 타므로 b6 의 «해당 범위 실행분」 두 곳을 한 구절로 묶는다.
- R-0331 rev2: b16 현행 = R-0331(scope별 실행) · R-0332(무관 G2 auto 명시 — enforcedBy 5검사기) · R-0333(auto 는 증거 아님). 새 문장은 «무관」 판정식 + G1 반송 — 반송은 Coordinator 행위 → delegatedTo command-dddjango 인 R-0331 이 귀속·배선 무변으로 맞다(R-0332 rev2 로 하면 enforcedBy-only Work 에 Coordinator 행위가 붙어 배선 개정이 따른다). prefLabel 갱신 필수(B-5).

---

## 3. 완성 문안 (② v2 가 그대로 가져갈 최종 텍스트 — 리터럴 경계·개행 포함)

### 3-1 `discipline-houserules-skill` s007-4/**b7** 최종형 (R-3447 rev2 amendment `@2026-09-04b` + R-3448 rev2 redefinition `@2026-09-04b`)

text(`@ko`) — 선두 없음 · 말미 `\n\n`:
```
**`Any` 는 타입이 아니라 검사 포기다 — 어디에도 쓰지 않는다.** 함수 시그니처(인자·`*args/**kwargs`·반환)·변수·클래스 속성·제네릭 인자(`dict[str, Any]`) 전부다 — 별표 인자 면제(ruff `allow-star-arg-any`) 관례와 다른 선택이다. 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 쪽 선언은 `object`(또는 정확 타입)로 쓴다 — mypy 는 이를 호환으로 본다. 시그니처의 `Any` 는 #645 가 차단하고, 변수·제네릭 안의 `Any` 는 ⓓ 후보(#645)로 표시된다 — 단 `dict`/`Mapping`/`MutableMapping` 의 **값 자리** `Any`(`dict[str, Any]` — 매개변수·반환·변수·속성 어디든)는 #647 이 차단하며 그 자리는 #645 후보로 남지 않는다. 후보는 감수자가 집행한다(§4.1 «시그니처만 강제하므로 나머지는 백스톱과 감수자» 와 같은 분담). 경계 입력(폼 `cleaned_data`·`request.user`·무스텁 서드파티·`json.loads` 결과)은 `object` 또는 프레임워크가 주는 정확한 타입으로 받아 **받는 즉시** 좁힌다(`TypeIs`·`isinstance`·`type() is` — implementation-python §1.12 · 좁히는 자리는 architecture-ddd §3.1 의 경계 규범대로 값 객체를 부르기 전). **JSON 문서는 `pydantic.TypeAdapter(그TypedDict).validate_python`/`validate_json` 으로 검증하며 받는다** — 대상은 파일·타 시스템·`json.loads` 결과이고 우리가 만든 JSON 도 파싱했으면 같다(strict `no-any-return`); HTTP body 는 ninja `Schema` 가 그 검증이다(implementation-python §12.0). 어떻게는 implementation-python §1.5, 무엇을 고르는지는 아래 결정표다. `object` 가 사는 자리는 좁히기·검증 도우미의 **매개변수**와 즉시 검증되는 **지역 변수**뿐이다(그 자리의 `dict/Mapping[…, object]` 는 #647 ⓓ 후보 — 감수자가 즉시 좁힘을 확인한다). **반환값·클래스 속성**에 `dict/Mapping[…, object]` 가 남으면 좁히지 않은 누수라 #647 이 차단한다. 면제는 둘 — 스텁이 강제하는 `forms.Form` 하위 `clean() -> dict[str, object]`(`ModelForm.clean` 은 `None` 이라 대상 아님)와 `TypeIs`/`TypeGuard[...]` 반환. `dict/Mapping` 값 자리가 아닌 반환 주석의 `object`(`-> object` 루트 · `tuple`/`list`/`Sequence` 원소)도 입구 밖 자리표시라 #647 ⓓ 후보다. `json.load(s)` 결과를 `TypeAdapter` 검증 없이 `object` 아닌 주석의 변수·`object` 아닌 반환·컴프리헨션·직접 첨자/속성 접근·리터럴 컨테이너 요소로 흘린 자리는 ⓓ #650 이다 — `x: object = json.loads(…)` 뒤 즉시 검증과 파서 직접 인자는 후보가 아니다.

```
- 귀속(한 블록 두 Work — 문장 경계 명확): 문장 1~5(«… 후보는 감수자가 집행한다(… 분담).» 까지) = **R-3447** · 문장 6 이후(«경계 입력 …» 부터 끝까지 — 델타 2문장 포함) = **R-3448**. 델타 2문장은 둘 다 `object`/JSON 처방이라 R-3448 귀속이 자명하다.
- Expression: `<djr#R-3447@2026-09-04b>`(rev 2 · amendment · wasRevisionOf `@2026-09-04`) · `<djr#R-3448@2026-09-04b>`(rev 2 · **redefinition** · wasRevisionOf `@2026-09-04`).

### 3-2 s007-4 **새 b8~b16** (조각 1 · order 8~16 · 중간 삽입 0)

b8(kind-norm `@ko` · statesNorm **R-3451** Prohibition):
```
**키가 정해진 값 묶음(레코드)은 딕셔너리로 들고 다니지 않는다** — 우리 코드가 리터럴로 만든 값은 `TypedDict`, 파싱한 JSON 은 `TypeAdapter(그TypedDict)` 검증 파싱, 도메인 개념은 값 객체(architecture-ddd §3.1). `dict/Mapping[str, object|Any]` 주석은 그 자체가 «구조를 안 정했다»는 신호다(#647). 레인이 바로 고르는 결정표:

```
b9(kind-table-row · xsd:string · norms=[]): `| 값의 모양 | 어디서 왔나 | 쓰는 도구 | 금지 |\n|---|---|---|---|\n`
b10~b15(kind-table-row · xsd:string · 행마다 statesNorm 1 — b10 R-3452 · b11 R-3453 · b12 R-3454 · b13 R-3455 · b14 R-3456 · b15 R-3457):
```
| 키가 정해진 값 묶음(레코드) | 우리 코드가 리터럴로 만든 내부 데이터 | `TypedDict`(종류가 여럿이면 `kind: Literal[…]` 판별 키로 union) | `dict/Mapping[str, object\|Any]` |
| 키가 정해진 값 묶음 | 파싱한 JSON(파일 `json.load`·타 시스템·`json.loads` — 우리가 쓴 파일도 같다) | `TypeAdapter(그TypedDict).validate_python/validate_json` 로 검증 파싱(HTTP body 는 ninja `Schema` 가 이미 검증) · 파싱 전 값 사용 금지 | 검증 없는 `-> TypedDict` 반환(strict `no-any-return`) · `Any`/`object` 로 흘리기(ⓓ #650) |
| 도메인 개념 | 도메인 계층 | dataclass·값 객체(architecture-ddd §3.1) | 딕셔너리 |
| 키가 데이터인 모음(조회표) | 어디든 | `dict[K, V]` 에 K·V 구체 타입(V 가 레코드면 `TypedDict`) | 값 타입 `object`·`Any` |
| 구조를 모르는 임의 JSON 통과 | 직렬화·저장 경계 | 재귀 별칭 `JsonValue`(implementation-python §1.5 — arm 은 공변 `Sequence`/`Mapping`) | `dict[str, object]`·`Any` |
| 타입이 이미 있는 값 | 함수 반환·매개변수·속성 | 실제 클래스(`BuildPlan` 등) | **입구 밖**의 자리표시 `object`(입구 매개변수·즉시 검증 지역 변수는 위 R-3448 · 반환 주석의 `object` 는 ⓓ #647) |
```
- b10~b14 말미 `\n` · **b15 말미 `\n\n`**. 셀 안 `|` 는 `\|` 이스케이프(rv1-B 원안 유지).

b16(kind-norm `@ko` · statesNorm **R-3458** Obligation + **R-3459** Prohibition · 말미 `\n\n` — §4.1 헤딩 앞):
```
**django-stubs 가 제네릭으로 선언했지만 런타임은 subscript 못 하는 Django 기저는 모델 타입 인자를 적는다** — 타입 매개변수에 기본값이 없는 것들이다: `ModelForm`·`BaseInlineFormSet`·`ModelAdmin`·`InlineModelAdmin`(`TabularInline`/`StackedInline`)과 `ListView`·`DetailView`·`CreateView`·`UpdateView`·`DeleteView`·`FormView` 및 그 mixin(`View`·`TemplateView`·`RedirectView` 는 기본값이 있어 대상 밖). 맨몸 상속은 mypy strict `[type-arg]` 빚이고, `# type: ignore[type-arg]` 는 통과가 아니라 은폐라 붙이지 않는다 — 둘 다 #646 이 차단한다. 표기는 **`if TYPE_CHECKING:` 별칭이 기본**이다: `_ModelAdminBase: TypeAlias = admin.ModelAdmin[Parent]  # noqa: UP040` / `else: _ModelAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin` — 기저에 직접 `X[Model]` 을 쓰면 import 시 `TypeError` 다(주석에만 쓰는 별칭은 `type` 문 — 지연 평가). 프로젝트가 `django_stubs_ext.monkeypatch()` 를 채택했으면(§6.1 의 관찰) 별칭 없이 `X[Model]` 직접 표기 — 채택은 레인이 도입하지 않는다. 스텁이 `ClassVar` 로 타입을 소유한 admin 선언 속성(`inlines` 등)은 재선언하지 않고(위 프레임워크 선언 면제), 프레임워크가 열어 둔 타입 매개변수는 bound(`Model`·`ModelForm[Model]`)로 적는다 — 예시는 implementation-django §18.

```
- 귀속: R-3458 = 문장 1·3·4·5(타입 인자·별칭/직접 표기·bound) · R-3459 = 문장 2 후반(`# type: ignore[type-arg]` 금지). 두 Work 가 한 블록 — «둘 다 #646 이 차단한다」 문장이 경계.

### 3-3 s007-4/**b5** R-3154 rev2(amendment `@2026-09-04`) · s011-6.1/**b1** R-3163 rev2(amendment `@2026-09-04`)

b5(말미 `\n\n` 유지):
```
- 프레임워크 선언: Django 모델 필드(`name = models.CharField(...)`)·폼 필드 · `class Meta` 옵션 · enum 멤버(`RED = 1`) — 달면 프레임워크 의미가 오작동한다 · admin 패널 클래스 본문의 Django 선언 속성(`model`·`inlines`·`list_display`·`readonly_fields` …) — 타입은 스텁의 `ClassVar` 가 소유하고 `inlines` 처럼 재선언이 불변성 red 가 되는 자리가 있어 적지 않는다(적으면 스텁 선언과 같아야 한다 · 선언적 클래스 본문의 메서드는 면제가 아니다)

```
b1(§6.1 · **선두 `\n` 유지** · 말미 `\n\n`):
```

표준 도구셋(패키지 매니저 uv·ruff·mypy strict·django-stubs·pydantic·pytest)은 기능 추가 흐름이 **직접 다룬다** — 기존 프로젝트의 도구·패키지 매니저를 감지해 존중하고(§1.1), 기능에 필요한 표준 도구가 없으면 `implementation-django-ninja` §2.1 버전-핀 규율로 셋업한다(임의 글로벌 설치 금지). `django-stubs-ext` 의 `monkeypatch()`(운영 의존성 + settings 최상단 1줄)는 프로젝트 전역 런타임 패치라 기능 흐름이 도입하지 않는다 — 채택 여부는 관찰(§1 ④)해 §4 의 기저 타입 인자 표기(별칭 / 직접)를 고른다.

```

### 3-4 `implementation-django-final` **s094-18** (Section + b1~b3 · b4 생략 권고)

Section 노드:
```
<…/implementation-django/references/final.md/s094-18> a djr:Section ;
    djr:headingSnapshot "## 18. Django admin·폼 타이핑 — django-stubs 제네릭 기저"@ko ;
    djr:inDocument <…/implementation-django/references/final.md> ;
    djr:sectionNumber "18" ;
    djr:sectionOwner djr:owner-graph .
```
b1(kind-norm · R-3460 Obligation · **선두 `\n`** · 말미 `\n\n` · `djr:restates` → houserules-skill `s007-4/b16`):
```

admin 저작 화면(`driven_layer/django_<bc>/admin/` — 배치·import 방향은 `discipline-houserules` §1 트리 82행·§5)의 `ModelForm`·`BaseInlineFormSet`·`ModelAdmin`·`TabularInline`/`StackedInline` 은 django-stubs 가 제네릭으로 선언하지만 런타임 클래스는 subscript 를 못 한다 — 규칙(타입 인자 필수 · `# type: ignore[type-arg]` 금지 · 별칭 기본 / monkeypatch 채택 시 직접)은 houserules §4·§6.1 이 소유하고, 이 절은 그 «어떻게»를 한 벌로 보인다. 웹 폼의 `ModelForm` 도 같은 표기다(`implementation-django-web` §6).

```
b2(kind-code · xsd:string · 펜스 전체 · 말미 `\n\n` · **탐침 green 형**):
```python
from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, TypeAlias

from django import forms
from django.contrib import admin
from django.db.models import Model
from django.forms import BaseInlineFormSet, ModelForm
from django.http import HttpRequest

if TYPE_CHECKING:  # django-stubs 전용 — 런타임 클래스는 subscript 불가
    _ChildFormBase: TypeAlias = forms.ModelForm[ChildModel]  # noqa: UP040 -- 기저로 쓰는 별칭이라 `type` 문이 될 수 없다
    _ChildFormSetBase: TypeAlias = BaseInlineFormSet[ChildModel, ParentModel]  # noqa: UP040 -- 셋째 인자(폼)는 적지 않는다: 기본값 ModelForm[ChildModel] 만 admin `formset` 자리(불변)와 맞는다
    _ChildInlineBase: TypeAlias = admin.TabularInline[ChildModel, ParentModel]  # noqa: UP040
    _ParentAdminBase: TypeAlias = admin.ModelAdmin[ParentModel]  # noqa: UP040
else:
    _ChildFormBase: type[forms.ModelForm] = forms.ModelForm
    _ChildFormSetBase: type[BaseInlineFormSet] = BaseInlineFormSet
    _ChildInlineBase: type[admin.TabularInline] = admin.TabularInline
    _ParentAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin

# 주석 전용 별칭은 `type` 문(지연 평가) — 자식 모델이 여럿이면 bound 로 적는다(`Any` 아님)
type ParentInlineFormSet = BaseInlineFormSet[Model, ParentModel, ModelForm[Model]]


class ChildInlineForm(_ChildFormBase):
    class Meta:
        model = ChildModel
        fields = ("field_a", "field_b")


class ChildInlineFormSet(_ChildFormSetBase):
    def clean(self) -> None: ...


class ChildInline(_ChildInlineBase):
    model = ChildModel            # admin 선언 속성 — 스텁 ClassVar 가 타입을 소유(houserules §4 면제)
    form = ChildInlineForm
    formset = ChildInlineFormSet
    extra = 0


@admin.register(ParentModel)
class ParentAdmin(_ParentAdminBase):
    readonly_fields = ("version",)  # 무주석 — 스텁 `ClassVar[_ListOrTuple[str]]` 가 타입을 소유
    inlines = [ChildInline]         # 재선언하면 `list[type[InlineModelAdmin[Any, Any]]]` 와 불변성 충돌 — 적지 않는다

    def save_model(self, request: HttpRequest, obj: ParentModel, form: ModelForm[ParentModel], change: bool) -> None: ...

    def save_related(self, request: HttpRequest, form: ModelForm[ParentModel], formsets: Sequence[ParentInlineFormSet], change: bool) -> None: ...
```
b3(kind-norm · R-3461 Obligation · `djr:restates` → houserules-skill `s007-4/b16` · 말미 = 문서 끝이면 `\n`(b4 생략) / b4 두면 `\n\n`):
```
프로젝트가 `django_stubs_ext.monkeypatch()` 를 채택했으면(houserules §6.1 관찰) `if TYPE_CHECKING:` 블록 없이 `class ParentAdmin(admin.ModelAdmin[ParentModel])` 로 직접 적는다 — 그 밖은 위 별칭이다. `BaseInlineFormSet` 의 세 번째 인자(폼 타입)는 적지 않는다 — 기본값 `ModelForm[_M]` 이 스텁 `InlineModelAdmin.formset`(`type[BaseInlineFormSet[_C, _P, ModelForm[_C]]]` · 불변)과 맞는 유일한 값이라 구체 폼 클래스를 적으면 `formset = …` 대입이 `[assignment]` 로 막힌다. `# type: ignore[type-arg]` 로 맨몸을 덮지 않는다(#646).
```
- md 시드: 파일 끝 `…django-anti-patterns-signals/)\n` 바로 뒤에 `## 18. Django admin·폼 타이핑 — django-stubs 제네릭 기저\n<!-- graph-owned: … -->\n`(빈 줄 없음 · 9ef6c4f 동형). 센서스 키: ordinal 94(LEDGER 마지막 s093 «### 커뮤니티 가이드») · ANCHOR_RE `^§?([0-9]+…)[.)]?` → «18» → **`s094-18`** ✓.
- 소스 미러 append(마커 없음): `## 18. …\n` + b1 + b2 + b3 → 그 span 의 sha256 = LEDGER baseline.

### 3-5 `command-dddjango` s007 (b6 R-0284 rev4 · b28 R-0345 rev3 — `@2026-09-04b` / b32 R-0349 rev2 · b16 R-0331 rev2 — `@2026-09-04`)

b6 해당 구절(나머지 문장 무변):
```
… 감사 호출 입력에 `check-layer-skeleton`(registry #4)의 ⓓ 후보 채널 출력(행위 칸 200행 초과 신호·페이로드)과 `check-public-surface-annotation`(registry #11)의 ⓓ 후보(#645 — 변수·제네릭 안의 명시 `Any` · #647 — 입구 매개변수·즉시 검증 지역 변수의 `dict/Mapping[…, object]` 와 반환 주석의 자리표시 `object` · #650 — `json.load(s)` 결과의 무검증 흐름)를 동봉한다 — 두 채널 모두 동봉 범위는 registry_gate 가 앵커 차분으로 가른 **«ⓓ 신규(N′∖L′)»** 절·sidecar 레코드이고, 앵커에도 있던 «ⓓ legacy» 는 게이트 보고의 건수로만 적는다. …
```
b28:
```
   11. `${CLAUDE_PLUGIN_ROOT}/scripts/check-public-surface-annotation.py` — 타입 전면(#493 — 시그니처·지역·속성·모듈/클래스 «모든 이름 첫 대입», 문법 없는 자리만 면제)·명시 `Any`(#645 — 시그니처는 차단·변수/제네릭 안은 ⓓ 후보 · dict/Mapping 값 자리는 #647 소유)·django-stubs 제네릭 기저(#646 — 맨몸·`type: ignore[type-arg]` 차단 · subscript/`TYPE_CHECKING` 별칭 통과)·딕셔너리-레코드(#647 — `dict/Mapping[…, Any]` 전 자리와 `[…, object]` 반환/속성 차단 · 입구 매개변수·즉시 검증 지역 변수의 `object` 와 반환 주석의 자리표시 `object` 는 ⓓ 후보 · `json.load(s)` 무검증 흐름은 ⓓ #650)·Thin Read 반환(#358)·계약 검증 토큰(#456).
```
b32(rv1-B §3.9 그대로):
```
   15. `${CLAUDE_PLUGIN_ROOT}/scripts/check-api-error-controller-contract.py` — narrow one-call `try`, concrete same-BC catch, direct no-arg concrete/event-specific BC-base `ErrorSchema`, two-argument `Status`, managed helper/handler/factory/serializer/mapping 금지 + 표준 트리 슬라이스(#120~#132·#474·#62·#648 반환 주석 `Status` 상자 하나·#649 `Schema`+`RootModel` 동시 상속 금지 — 프로필 무관 선행).
```
b16(말미 `\n\n` 유지 · 굵은 문장 = R-0331 rev2 귀속):
```
   - **scope별 실행**: Error response G2는 승인된 code/preserve scope마다 위 command를 각각 렌더해 실행한다. Error response와 무관한 G2는 네 API-error-aware checker와 registry #16에 positional target 및 `--error-profile auto`를 명시해 기존 positional 동작(auto 프로필)을 유지하고, `auto` 결과는 `Error response contract 12-slot` 증거가 아니라고 보고한다. **«무관»의 판정은 코드 모양이 아니라 승인 12-slot 유무다 — 단 승인 12-slot 없이 이번 산출물의 컨트롤러가 BC 오류 status 를 `response=` 에 선언했으면 `auto` 로 돌리지 않고 G1 반송(`STOP_FOR_USER_APPROVAL` — error profile 미결정 · design-architect «Error response contract 12-slot» 의 적용 조건)이다: `auto` 는 #63·#125 등 code-profile 규칙을 재우므로 오류 응답을 선언한 표면의 G2 증거가 될 수 없다.**

```
- codex `codex-dddjango/skills/dddjango/SKILL.md` hand: :125(b6) · **:136(b16)** · :150(b28 — `scripts/` 경로 표기) · :154(b32).

### 3-6 `implementation-django-skill` s005/**b17** 확장 (kind-table-row · xsd:string · norms=[] — B-1)
```
| Django 5.x 새 기능 | §17 |
| Django admin·폼 타이핑(django-stubs 제네릭 기저) | §18 |

```
(말미 `\n\n` 그대로 — b18 산문 앞 빈 줄.) codex `implementation-django/SKILL.md:50` 뒤 1행 hand.

### 3-7 ninja (s009-2.2/b13 · b1 · s012-3.1 새 b9) — rv1-B §3.10·§3.11 채택, 경계만 명시

- b13(말미 `\n` 유지 · statesNorm R-0687, **R-3463**): rv1-B §3.10 전문 그대로.
- b1(경질 개행 관례 유지 · 말미 `\n\n` · statesNorm R-0671, R-0672, **R-3465**): 마지막 줄 `가능한 경우 \`response={status: Schema}\` 형태로 성공/오류 schema를 분리한다.` 뒤에 ` 한 status 의 성공 본문이 둘 이상의 모양이면 \`response={200: A | B}\` 익명 union 을 적지 않는다 — 이름 붙은 컴포넌트와 discriminator 를 잃어 계약이 바뀐다(\`architecture-api\` §5.2) · §3.1 의 \`RootModel\` 하나를 선언한다.` 를 이어 쓴다(같은 문단 — 경질 개행은 원문 폭에 맞춰 1~2회 · 렌더 byte 는 블록 리터럴이 정본이라 자유).
- s012-3.1 **b9**(order 9 · b8 뒤 · 말미 `\n\n` · statesNorm **R-3464**): rv1-B §3.11 b9 전문. 선택(문단형): 선두 `- ` 를 빼고 굵은 선두 문장으로 시작 — b8 과 같은 꼴. 불릿 유지도 적법.

### 3-8 `implementation-django-ninja-skill` s004 — R-3466 (Obligation)

A안(계획 §1.9): b17 말미 `\n\n` → `\n` · 새 **b18**(order 18 · `\n\n` · statesNorm R-3466 · `djr:restates` → final `s009-2.2/b13`, `s009-2.2/b1`, `s012-3.1/b9`):
```
- 반환 주석의 `Status` 는 하나(`-> Status[Out | Err]`) · 성공 union 은 이름 붙은 `RootModel` 하나(`Schema` 병행 금지 · `response={200: A | B}` 금지) (§2.2·§3.1)

```
B안(권고 — 주제 인접·블록 수 불변): **b12** 텍스트 확장 + `statesNorm += R-3466` + `restates += s009-2.2/b1, s012-3.1/b9`(기존 b12·b13 유지) · 말미 `\n` 유지:
```
- operation은 `summary`·`description`·`tags`로 문서화하고 반환 타입을 명시한다(`object` 금지) — 반환 주석의 `Status` 는 하나(`-> Status[Out | Err]`) · 성공 union 은 이름 붙은 `RootModel` 하나(`Schema` 병행·`response={200: A | B}` 금지) (§2.2·§3.1)
```
- wiring(둘 다): `djr:R-3466 djr:delegatedTo <a/agent-design-review-api>, <a/agent-discipline-reviewer> .` · codex `implementation-django-ninja/SKILL.md` :30(B안) / :35 뒤(A안) hand.

### 3-9 prefLabel 9 (B-5)

| Work | 새 prefLabel(@ko) |
|---|---|
| R-3447 | `Any 금지 — 시그니처(별표 인자 포함)·변수·클래스 속성·제네릭 인자 전부 · 프레임워크 오버라이드도 object/정확 타입 · 시그니처는 #645 차단·그 밖은 ⓓ 후보(#645) · dict/Mapping 값 자리 Any 는 #647 차단` |
| R-3448 | `경계 입력은 object/정확 타입으로 받아 받는 즉시 좁힘(TypeIs·isinstance·type() is · 자리는 architecture-ddd §3.1) · JSON 은 TypeAdapter(TypedDict) 검증 파싱 · object 는 입구 매개변수·즉시 검증 지역 변수만(반환/속성 누수 #647 차단 · 반환 자리표시 object·json.load 무검증 흐름은 ⓓ #647/#650) · 면제 Form.clean·TypeIs` |
| R-3154 | `문법 부재 자리 ③ 프레임워크 선언(모델 필드·폼 필드·class Meta·enum 멤버·admin 패널 선언 속성 — 스텁 ClassVar 소유)` |
| R-3163 | `표준 도구셋은 기능 추가 흐름이 직접 다룬다 — 기존 도구 감지·존중, 부재 시 §2.1 버전-핀 규율 셋업(임의 글로벌 설치 금지) · django-stubs-ext monkeypatch 는 전역 패치라 미도입 — 채택 관찰(§1 ④)로 §4 표기(별칭/직접) 결정` |
| R-2715 | `레코드는 TypedDict(판별 키 union) · 파싱한 JSON 은 TypeAdapter 검증 파싱(no-any-return) · 조회표는 dict[K, 구체 V] · 통과 값은 공변 JsonValue · TypedDict→직렬화는 object 입구 브리지` |
| R-0284 | `필수 입력 5종(코드+테스트·승인 입장 표·역할별 최소 조정 보고·test diff·실행 결과·슬라이스 목록) + ⓓ 후보 동봉(registry #4 200행 신호 · #11 #645/#647/#650) — 동봉 범위는 registry_gate 앵커 차분 ⓓ 신규분` |
| R-0345 | `registry #11 — 타입 전면(#493)·명시 Any(#645 — 시그니처 차단·변수/제네릭 안 ⓓ 후보)·django-stubs 제네릭 기저(#646)·딕셔너리-레코드(#647 · json.load ⓓ #650)·Thin Read 반환(#358)·계약 검증 토큰(#456)` |
| R-0349 | `registry #15 — narrow try·concrete same-BC catch·direct BC-base ErrorSchema·two-argument Status + 표준 트리 슬라이스(#648 Status 상자 하나·#649 Schema+RootModel 동시 상속 금지)` |
| R-0331 | `Error response G2 는 승인된 code/preserve scope 마다 command 를 각각 렌더·실행 · «무관» = 승인 12-slot 유무 — 12-slot 없이 BC 오류 status 를 선언한 산출물은 auto 금지·G1 반송` |

### 3-10 신설 17 kind·문안 출처·wiring (B-7·B-15)

| R | doc · 블록 | kind | 문안 | delegatedTo | enforcedBy |
|---|---|---|---|---|---|
| R-3451 | houserules-skill s007-4/b8 | **Prohibition** | §3-2 b8 | discipline-reviewer | public-surface(#647) |
| R-3452 | s007-4/b10(1행) | Obligation | §3-2 | discipline-reviewer | public-surface(#647) |
| R-3453 | s007-4/b11(2행) | Obligation | §3-2 | discipline-reviewer | **public-surface(#650 ⓓ — 권고)** |
| R-3454 | s007-4/b12(3행) | Obligation | §3-2 | discipline-reviewer | — |
| R-3455 | s007-4/b13(4행) | Obligation | §3-2 | discipline-reviewer | public-surface(#647) |
| R-3456 | s007-4/b14(5행) | Obligation | §3-2 | discipline-reviewer | — |
| R-3457 | s007-4/b15(6행) | Obligation | §3-2 | discipline-reviewer | **public-surface(#647 반환 object ⓓ — 권고)** |
| R-3458 | s007-4/b16 | Obligation | §3-2 b16 | discipline-reviewer | public-surface(#646) |
| R-3459 | s007-4/b16 | **Prohibition** | §3-2 b16 | discipline-reviewer | public-surface(#646) |
| R-3460 | django-final s094-18/b1 | Obligation | §3-4 b1 | discipline-reviewer | — |
| R-3461 | s094-18/b3 | Obligation | §3-4 b3 | discipline-reviewer | public-surface(#646) |
| R-3462 | web-final s007-6/b10 | Obligation | §3-11 | discipline-reviewer | — |
| R-3463 | ninja-final s009-2.2/b13 | **Prohibition** | rv1-B §3.10 | discipline-reviewer | api-error-controller(#648) |
| R-3464 | s012-3.1/b9 | Obligation | rv1-B §3.11 b9 | design-review-api | api-error-controller(#649) |
| R-3465 | s009-2.2/b1 | **Prohibition** | §3-7 | design-review-api · discipline-reviewer | — |
| R-3466 | ninja-skill s004/b18(A) 또는 b12(B) | Obligation | §3-8 | design-review-api · discipline-reviewer | — |
| R-3467 | api-final s022-5.2/b7 | Obligation | rv1-B §3.12 | design-review-api | — |

개정 배선 변경: **R-3448 `enforcedBy <c/check-public-surface-annotation.py>` 추가**(delegatedTo 유지) — 그 밖 8 개정은 배선 무변. 접촉 wiring 파일 6.

### 3-11 `implementation-django-web-final` s007-6 **새 b10**(R-3462 · 말미 `\n\n` · b9 code 뒤)
```
- `ModelForm` 기저는 django-stubs 제네릭이라 모델 타입 인자를 적는다 — 위 `ArticleForm` 의 `_ArticleFormBase`(`if TYPE_CHECKING:` 별칭 = `forms.ModelForm[Article]` · 런타임은 `forms.ModelForm`)가 그 표기이고, monkeypatch 채택 시 직접 표기와 `# type: ignore[type-arg]` 금지는 `discipline-houserules` §4 소유 · admin 쪽 한 벌은 `implementation-django` §18.

```
- s003-2/b10 code 정정(선두 import 뒤 `if TYPE_CHECKING:` 블록 — 탐침 green 형): `from typing import TYPE_CHECKING, TypeAlias` 추가 → `if TYPE_CHECKING:  # Generic CBV 기저는 django-stubs 제네릭 — 표기는 houserules §4(별칭 기본 · monkeypatch 채택 시 ListView[Article] 직접)` / `    _ArticleListBase: TypeAlias = ListView[Article]  # noqa: UP040` / `    _ArticleCreateBase: TypeAlias = CreateView[Article, ArticleForm]  # noqa: UP040` / `else:` / `    _ArticleListBase: type[ListView] = ListView` / `    _ArticleCreateBase: type[CreateView] = CreateView` → `class ArticleListView(_ArticleListBase):` · `class ArticleCreateView(LoginRequiredMixin, _ArticleCreateBase):`. `StaffRequiredMixin`·FBV 무변.
- s007-6/b9 code: `from typing import TYPE_CHECKING, TypeAlias` + `RegistrationForm` 뒤에 `if TYPE_CHECKING: _ArticleFormBase: TypeAlias = forms.ModelForm[Article]  # noqa: UP040 / else: _ArticleFormBase: type[forms.ModelForm] = forms.ModelForm` → `class ArticleForm(_ArticleFormBase):`.
- prose §13.4(:1328): `class EditArticleView(LoginRequiredMixin, PermissionRequiredMixin, _EditArticleBase):` + 직전 주석 `# _EditArticleBase: TYPE_CHECKING 별칭 = UpdateView[Article, ArticleForm] (houserules §4 · §18)` — 탐침 green 형(`UpdateView[Article, ArticleForm]`).

### 3-12 ISSUED 17행 (커밋일 `D`)
```
R-3451	D	rules/discipline-houserules-skill.ttl   … R-3459 동일
R-3460	D	rules/implementation-django-final.ttl · R-3461 동일
R-3462	D	rules/implementation-django-web-final.ttl
R-3463	D	rules/implementation-django-ninja-final.ttl · R-3464 · R-3465 동일
R-3466	D	rules/implementation-django-ninja-skill.ttl
R-3467	D	rules/architecture-api-final.ttl
```
(조각 1 커밋에 R-3451~R-3462 · 조각 2 커밋에 R-3463~R-3467 — `ontology_issued_check` «연속 증가·결번 금지」 를 조각 경계에서 만족.)

---

## 4. Δ 목록 (계획 v2 델타)

- **ΔB-1(MAJOR-1) §1.3**: «새 b18» → **b17 텍스트 2행 확장**(§3-6) · 계수 BlockShape −1 · codex `implementation-django/SKILL.md:50` 뒤 1행. rv1-B §5-1 «새 b18」 문구 정정 각주.
- **ΔB-2(MAJOR-2) §1.2 b2·b3**: `_ChildFormSetBase` 셋째 인자 생략(전방 참조 문자열 삭제) + 주석 · b3 «생략할 수 있다」 → «적지 않는다 — 구체 폼이면 `formset` 대입 `[assignment]`」(§3-4). §7-1 → «해소(rv3-B 탐침 · ④ 재확인만)». §1.2 «④ 착수 시 mypy 1회」 는 유지하되 대상에 web CBV 별칭 3·python b3·ddd 도 포함(탐침 파일 `$S/rv3B/probe/` 재사용).
- **ΔB-3(MAJOR-3) §1.11**: 단계 재작성 — 0 md 시드 → 1 rdflib·gate·render → 2 prose §13.4 md → 3 소스 미러 수동 교체/append(마커 없음) → 4 LEDGER(graph = `sha256(strip_marker(렌더 span))` ≡ 소스 절 span · prose = 배포 span) → 5 ISSUED·target-counts·q4 emit·rulepack → 6 corpus_mirror_sync --check 0 → --write → codex hand 4 → spec_lint → verify. §1.2 «LEDGER baseline 행」 에 산식 병기.
- **ΔB-4(MAJOR-4) §1.1 b7 델타·§1.7 b6**: #650 문면을 §2.1 오라클과 일치(§3-1 마지막 문장 · §3-5 b6 «무검증 흐름」).
- **ΔB-5(MAJOR-5) §1**: «개정 9 전부 prefLabel 갱신」 + 문안 §3-9.
- **ΔB-6(MAJOR-6) §1.2**: Section 노드에 `djr:sectionNumber "18"`.
- **ΔB-7(MINOR-1) §1**: kind 표 §3-10(Prohibition 4 · Obligation 13).
- **ΔB-8(MINOR-2) §1**: ISSUED 17행 파일 열(§3-12).
- **ΔB-9(MINOR-3) §1.1**: «b7 의 말미 개행 조정」 삭제 → «b7 `\n\n` 유지 · b15·b16 `\n\n` · b9~b14 `\n`」. §1.5·§1.2·§1.1(§6.1) 에 «선두 `\n` 유지」.
- **ΔB-10(MINOR-4) §1.9**: b17 `\n\n`→`\n`(A안) 또는 **b12 확장(B안 권고)** · R-3466 wiring(design-review-api·discipline-reviewer) · restates 3 · kind Obligation.
- **ΔB-11(MINOR-5) §1.7·§2.4**: b6 «해당 범위 실행분」 2곳을 한 구절로(§3-5) · §2.4 보고 절 이름 «ⓓ 신규(N′∖L′)»·«ⓓ legacy n건」 고정.
- **ΔB-12(MINOR-6) §1.7·§7-4**: R-0331 rev2 = `@2026-09-04`(무접미 확정) · 근거 좌표 «design-architect :39·:41·:48 · acceptance-tester :41」 · §7-4 → «검증됨(이번 산출물 한정 · brownfield update 잎의 반송은 :39 «바꾸는 scope」 정합)».
- **ΔB-13(MINOR-7) §1.4**: b10 문면 지시형(§3-11) + 일관성 각주 «소유 블록이 있으면 확장(ninja b1) · 없으면 코드 뒤 주석형 규범(선례 django-final s087/b3)」.
- **ΔB-14(MINOR-8) §1.8**: s012-3.1 b9 «불릿 또는 문단형 — 문단 b8 뒤」 명시(선택).
- **ΔB-15(MINOR-9) §1.1 wiring**: R-3453·R-3457 `enforcedBy public-surface` 추가(권고 · 부분 집행 근거 = R-3448 과 동일 기준) · «wiring 10파일」 → «wiring 6파일(rules 10)」.
- **ΔB-16(MINOR-10) §1.11**: target-counts 수치 확정(Block 2922 또는 Δ 반영 2919~2920 · Section 546 · Norm/Work 3476 · Expr 3594) · q4 +17 · 조각별 증분 표.
- **ΔB-17(MINOR-11) §1.11**: LEDGER 15행 열거(command s007 2회 · prose 1 은 md 수정 즉시).
- **ΔB-18(MINOR-12) §3·§4-5**: codex 좌표 전수(§1 표) · houserules hand 범위 «§4 + §6.1」 · Coordinator :136 추가 · **R-12 로드맵 행 «반영 문구」(rv1-B §3.15) 를 §4-5 에 추가**(9a258bf 판형).
- **ΔB-19(MINOR-13) §1.2**: b4 `---` 생략 권고(b3 말미 `\n` · EOF 개행 1) — 유지 시 b4 `---\n`.

---

## 5. 사각 (④·⑤ 에서 볼 것 — 이 리뷰가 닫지 못한 것)

1. **탐침 범위**: `$S/rv3B/probe/` 는 spring 모델(CharacterModel/MediaModel)로 치환한 형이라 정본 예시의 `ChildModel`/`ParentModel` 이름·`fields = ("field_a", "field_b")` 는 미검증(플러그인 예시 관례상 자유 식별자). 「무주석 `readonly_fields`」 는 spring 의 `id` 로 검증 — `"version"` 존재 여부는 예시 자유. 파일 단위 `mypy` 라 `@admin.register(ParentModel)` 중복 등록 런타임은 밖(타입 검사 무관).
2. **#493 회복 전제**: §18 b2 의 무주석 admin 속성이 green 인 것은 mypy 얘기고, 검사기 #493 은 «별칭 기저 → `_alias_values` 해소 → 선언적 면제」 수리(§2.1) 뒤에만 조용하다 — 픽스처 `stub_generic_panel.py` 가 §18 b2 와 **같은 모양**(셋째 인자 생략 포함)이어야 한다(A 축).
3. **`json.load` ⓓ #650 ↔ #647 이중 발화**: `payload: dict[str, Any] = json.loads(raw)` 는 #647 차단 + #650 ⓓ 둘 다 — 술어가 다르니 적법이나 predicates.md 의 «1행 1술어」 문면에서 #650 행의 «후보 술어」 가 #647 과 겹치지 않게(«호출 흐름」 술어로) 쓰는 것은 A/② 몫.
4. **등재 3문서 집계**: ast 63→65 · ast+ 57→60 · 계 547→552 는 맞다(#646·#647·#650 ast+ · #648·#649 ast). 판정×어겼을때 표(spec :277 `ast+` blocker 56·검사기 1)에서 **ⓓ 전용 #650 의 «어겼을때」 열**(#69·#644 선례 값) 은 이 리뷰가 확인하지 못했다 — spec_lint ⑦ 이 잡는다.
5. **rulepack 의 절 번호**: §18 신설로 `section_number "18"` 항목이 팩에 처음 생긴다 — `regen_core`/selector 골든에 절 번호 목록 스냅숏이 있으면 갱신(verify-mutation 은 rulepack 접촉 커밋에 필수 — DEVELOPMENT §5).
6. **codex houserules SKILL.md 의 절 번호 표기**: codex 미러는 스킬 참조를 codex 이름(`dddjango-implementation-django` 등)으로 쓴다 — b16 «예시는 implementation-django §18」·§18 b1 «`implementation-django-web` §6」 의 codex 판 치환 문자열은 손 미러 때 대응 이름으로(메모리 recipe 6).
7. **web SKILL.md(doc_key 11 후보)**: `implementation-django-web/SKILL.md:29` «web form … 경로를 모두 처리 (§6)」 불릿에 `ModelForm` 타입 인자 언급 0 — SKILL 만 읽는 web 레인은 R-3462 를 못 본다. 선택(rv1-B MINOR-7 과 같은 부류) — 이번 배치 밖이면 회신·추적표에 «이월」 1줄.
8. **두 조각·같은 절 두 번**: command s007 은 조각 1(b6·b28)·조각 2(b16·b32) 두 번 렌더·LEDGER·codex hand — 조각 2 에서 조각 1 의 문안을 되돌리지 않도록 조각 2 rdflib 스크립트는 HEAD ttl 을 다시 읽는다(스크립트 입력을 조각 1 이전 사본으로 고정하지 말 것).

— 끝. 산출: `$S/rv3B/probe/{p18_admin,p15_python,pweb_cbv,pddd_fieldvalue,pneg_typeddict}.py` · `mypy_rv3b_probe.txt`(1 error = MAJOR-2 형) · `mypy_rv3b_neg.txt`(2 error = 기대 red) · `runtime_rv3b_probe.txt`.
