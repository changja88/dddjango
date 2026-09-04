# 현장 보고 3 · ⑤-2 구현 리뷰(조각 2 커밋 `d701df8` + 정정 `cad221b`) — 리뷰어 B(규범 축: 온톨로지 정본·렌더 문면·미러·등재 문서) · 2026-09-04

대상: `d701df8`(S-5 + ⓔ1 + ⑤-1 정정) 의 `ontology/`·렌더 md 5 doc·소스 미러·codex hand 3·등재 문서·계수 픽스처 + `cad221b`(봉인 재발행·정직 기록). 기준 문안 = rv1-B §3.10~§3.13 · rv3-B §3-5·§3-7·§3-8(B안)·§3-9·§3-10·§3-12 · rv5-B §3(MINOR-1~5) · 계획 v2 §1.7~§1.10·Δ4·Δ13.
실측 도구(`$S/rv5B2/`): `struct_check2.py`(Work 7·블록·restates·wiring·ISSUED) · `ledger_check2.py`(LEDGER 6행 sha 직접 계산 + 소스/codex span) · `text_cmp2.py`(리뷰 문안 ↔ ttl ↔ 렌더 md ↔ 미러 글자 대조) · rdflib `blocks.py` 조회 · `corpus_mirror_sync --check`·`ontology_render_sync`·`cmp` 재실행(이 리뷰 시점 HEAD `b541870`). 실서고 무수정 · 커밋 없음.

**총평: BLOCKER 0 · MAJOR 1 · MINOR 5.** 정본 ttl(신설 5·개정 2)·문면·wiring·ISSUED·LEDGER·계수·미러는 ③ 완성 문안과 글자 단위로 동일하고 rv5-B MINOR-1~5 도 전부 in-place 로 반영됐다. 결손은 «등재 3문서» 중 `2026-08-11-predicates.md` 에 #648/#649 행이 없는 것(MAJOR-1 — 계획 §3 명시 · `ast` 행 선례 #627·#630~#636 실존 · spec_lint ⑥ 이 ast+ 만 강제해 red 가 안 났다) 하나이고, 나머지는 문면 정밀도(api b7 의 «§6 에러 프로필» 앵커 — rv1-B §3.12 내 문안의 오류 · #63 행 span 관례 · #648 셀 표기)와 회신 3 표현이다.

---

## 1. 판정 표

| # | 항목 | 판정 | 근거(요약) |
|---|---|---|---|
| B-1 | 신설 R-3463~R-3467 kind·prefLabel·Expression rev1 | **검증됨** | Prohibition R-3463·R-3465 / Obligation R-3464·R-3466·R-3467(rv3-B §3-10 표와 일치) · prefLabel 1개 @ko · `<R@2026-09-04>` a Expression · revision 1 · currentExpression 정합(`struct_check2`) |
| B-2 | 개정 R-0349 rev2 · R-0331 rev2 | **검증됨** | `@2026-09-04` 무접미(Δ4) · revisionKind amendment · wasRevisionOf `@2026-08-22` · revision 2 · prefLabel = rv3-B §3-9(R-0349 는 «#120~#132·#474·#62 ·» 보충 — 더 완전) · wiring 무변(R-0349 enforcedBy api-error-controller · R-0331 delegatedTo command-dddjango) |
| B-3 | ninja-final b13·b1·s012-3.1 새 b9 | **검증됨** | b13 statesNorm [R-0687, R-3463] · 문면 = rv1-B §3.10 전문 SAME · 말미 `\n` / b1 statesNorm [R-0671, R-0672, R-3465] · 말미 문장 = rv1-B §3.11 2b(경질 개행 접합 뒤 SAME) · 말미 `\n\n` / b9 order 9(b8 뒤 · 연속 1~9) · R-3464 · = rv1-B §3.11 b9 SAME · 말미 `\n\n` |
| B-4 | ninja-skill b12(B안) | **검증됨** | 텍스트 = rv3-B §3-8 B안 SAME · statesNorm [R-2944, R-2945, R-3466] · restates 기존 2 + s009-2.2/b1 + s012-3.1/b9(대상 4 실존) · 블록 수 17 불변 |
| B-5 | api-final s022-5.2 b6·b7 | **검증됨 + MINOR-1** | b6 말미 `\n\n`→`\n` · b7 order 7 · R-3467 · = rv1-B §3.12 SAME · 말미 `\n\n` — 단 b7 의 «(§6 에러 프로필)» 은 §5.4 를 가리켜야 한다(§6 = «RFC 9457 에러 응답 형식») · «고정 `code`» 는 §5.4 «그 필드명은 고정하지 않는다» 와 어긋남 |
| B-6 | command b32·b16 | **검증됨** | b32 = rv3-B §3-5 SAME(#648·#649 삽입 위치 «#62·#648 … — 프로필 무관 선행») · b16 = rv3-B §3-5 SAME(굵은 문장 · 말미 `\n\n`) · statesNorm 무변 [R-0331, R-0332, R-0333]/[R-0349] |
| B-7 | wiring 9 | **검증됨** | R-3463 delegatedTo discipline-reviewer + enforcedBy api-error-controller · R-3464 delegatedTo design-review-api + enforcedBy api-error-controller · R-3465 delegatedTo design-review-api·discipline-reviewer · R-3466 동 2 · R-3467 delegatedTo design-review-api = rv3-B §3-10 표 · rulepack `by_checker[api-error-controller]` = [R-0349, R-3463, R-3464] |
| B-8 | ISSUED 5 | **검증됨** | R-3463~R-3467 · 2026-09-04 · 파일 3 · 총 3467 · 연속 |
| B-9 | ⑤-1 B 정정 반영(MINOR-1~5) | **검증됨** | houserules b16·b5 · command b28 — 새 구절 CONTAINS · 옛 구절 잔존 0 · Expression 무신설(R-3458/R-3154/R-0345 currentExpression 무변) · LEDGER `discipline-houserules-skill s007-4`·`command-dddjango s007` 재기준선 · codex houserules 이름 치환 3(`dddjango-architecture-ddd §3.1` 3 · bare 0) + 본문 동일(전 파일 diff = 충돌 4스킬 이름·frontmatter 뿐) |
| B-10 | 렌더 md 글자 대조(Claude) | **검증됨** | ttl 블록 텍스트 10개(ninja b13·b1·b9 · SKILL b12 · api b6+b7 · Coordinator b16·b28·b32 · houserules b5·b16)가 배포 md 에 그대로 존재 · `ontology_render_sync` red 0 · 좌표 = ninja final :110~112·:141·:367 · SKILL :34 · api :208 · Coordinator :119·:133·:137 · houserules :72·:89 |
| B-11 | 미러(소스 3절 · codex final byte · codex hand 3) | **검증됨** | 소스 미러 ninja s010-2.2·s013-3.1 · api s023-5.2 span == LEDGER sha · codex ninja/api final byte 동일 · codex Coordinator :136·:150·:154 = Claude(`scripts/` 경로만) · codex ninja SKILL :30 = Claude :34 · `corpus_mirror_sync --check` 11/11 · 검사기 3·registry_gate·pregate json·rulepack `cmp` 동일 |
| B-12 | 규범 정합(R-3463↔R-0687 · R-3465↔R-0681 · R-3464↔b7 · R-0331 rev2↔R-0332/R-0333·agents) | **검증됨** | 아래 §2.4 |
| B-13 | R-0349↔검사기 docstring · 등재 3문서 #648/#649 · #63 08-25 | **MAJOR-1 + MINOR-2 + MINOR-3** | docstring #648/#649 문면 = R-3463/R-3464 취지 일치 · tree-revision-spec :1177~1178 · rule-owner-map :561~562 등재 — **predicates.md 행 0**(계획 §3 «행 5» 중 2 누락) · #63 행 08-25 개정이 span 이 아니라 규칙 문장 안에 인라인 · #648 셀 «`Status[Out, Err 의 union]`» 오독 소지 |
| B-14 | LEDGER 6행 sha | **검증됨** | 6행 전부 `sha256(strip_marker(렌더 span))` 직접 계산과 일치 · 같은 (doc,sec) 마지막 행 = 이번 행 |
| B-15 | target-counts · q4 · rulepack · corpus · byte | **검증됨** | Block 2917→2919(+2 = ninja b9·api b7 · B안 0) · Expression 3587→3594(+5+2) · Norm/Work 3471→3476 · Section 546 — Δ1 최종값 · q4 3462→3467 · rulepack label 7종 갱신(`built_from` 재소성) |
| B-16 | 정직 기록(d701df8 «verify 6/6» → cad221b) | **검증됨 + MINOR-5** | 기록·루브릭 정정 문면 정확 · `verify4.log` 6/6 실기록 · manifest `sealed_commit`=d701df8(HEAD 봉인 관례) — 절차 결함이 `docs/DEVELOPMENT.md`·메모리 레시피에 아직 없음 · 루브릭에 정정 커밋 해시 미기재 |
| B-17 | 회신 3 초안 규범 표현 | **MINOR-4** | «앵커 격리(N∖L)» 라벨 뒤집힘 · ⑥ «code-json 프로필로 돌린다» 과결정 · N-1 R-3443 주어 · «결정표 6행 R-3451~R-3457» 수 불일치 |

---

## 2. 항목별 상세

### 2.1 정본 ttl(B-1·B-2·B-7·B-8)

- Work 7 의 구조(`$S/rv5B2/struct_check2.txt`): 신설 5 는 `djr:Expression` 1개(rev 1) · 개정 2 는 Expression 2개(rev 1 `@2026-08-22` → rev 2 `@2026-09-04` amendment · wasRevisionOf 정합). 같은 날 접미 `b` 는 없다(Δ4 — 조각 1 의 `@2026-09-04b` 는 R-3447/R-3448/R-0284/R-0345 뿐).
- R-3464 를 Obligation 으로 둔 것은 문장 주어(«선언한다»)가 의무이고 «함께 상속하지 않는다» 는 그 방법의 단서라 적법(rv3-B §3-10 결정 그대로).
- wiring 9 triple 은 `piece2_ontology.py` §5 와 파일 실물이 같다. R-3465·R-3466·R-3467 은 enforcedBy 없음(기계 판정 없음 — 검사기가 `response=` 값 union 의 성공 status 를 안 본다 · rv1-B §3.11 배선 그대로).

### 2.2 문면 글자 대조(B-3~B-6·B-10·B-11) — `$S/rv5B2/text_cmp2.txt`

- A 절(리뷰 문안 ↔ ttl): SAME 7(b13 · b9 · b1 말미 · api b7 · SKILL b12 · command b32 · b16) + CONTAINS 3(b28 · houserules b16 · b5, 옛 구절 잔존 False).
- b1 경질 개행: 줄 길이 [66, 66, 69, 67, 88] — 마지막 줄 88자가 원문 폭(≈67)을 넘는다. rv3-B §3-7 «렌더 byte 는 블록 리터럴이 정본이라 자유» 로 적법 · 미관(§4 ①).
- B 절(ttl ↔ Claude md) 10/10 OK · C 절(미러) 전부 True.

### 2.3 등재 문서(B-13)

- `2026-08-08-tree-revision-spec.md` :1177~1178 #648(`ast`·blocker)·#649(`ast`·blocker) · 「값」표 `ast` 291→293 · 판정×어겼을때 281/293 · 계 500/552 · 읽는 법 435 — 조각 1 증분(498/550)과 합쳐 Δ3 ⑨ 최종값과 일치(rv5-B §2.6 예정 그대로). `rule-owner-map.md` :561~562 + :61 #63 비고. `spec_lint` 0.
- **`2026-08-11-predicates.md` 에 #648/#649 행이 없다.** 계획 v2 §3 «등재 3문서: … `2026-08-11-predicates.md` 행 5(셀 `|` 금지 · ⓓ 행은 «후보·물음»)» 가 명시했고, 조각 1 은 #646/#647/#650 을 :245~247 에 넣었다. 이 문서는 `ast` 행도 싣는다(72행 — 직전 배치 #627·#630~#636 전부 `ast` 확정 술어만). `spec_lint.check_predicates` 는 «predicates 의 #N 생존·등급 일치» 와 «`ast+` 는 항목 필수» 만 보므로(`workspace/tools/spec_lint.py:255~276`) `ast` 신설 행 누락은 red 가 나지 않는다 — 그래서 `piece2-summary.md` «등재: tree-revision-spec … · rule-owner-map … · spec_lint 0» 이 두 문서만 적고도 green 이었다. 술어 문서는 «6번(플러그인 개발)이 그대로 받는 재료» 라 검사기 술어의 정본 등재가 빠진 셈 → **MAJOR-1**(§3-1 문안).
- #63 행(:387): rv1-B §3.14 «08-25 개정 span 추가» 였는데, 구현은 규칙 문장 자체를 `response={status: 그 status 에서 실제 반환하는 오류 타입 그대로(concrete·Union·명시값 base — base 뭉뚱그림 금지 · 2026-08-25 R-0681 rev2/R-0087 rev2)}` 로 바꿨다. 이 표의 이력 관례는 «원문 유지 + `<span>날짜 · **제목** — …</span>` 추기»(:365 #33 · :526 #197 · :677 #365 · :866 #543 — 08-25 span 4건 · span 총 65)이고 같은 행의 09-01 개정도 span 이다. 규칙 열 안의 괄호 인라인은 원문·개정의 경계를 지운다 → **MINOR-2**.
- #648 행(:1177) «성공·오류 union 을 한 `Status[…]` 안에 넣거나(`Status[Out, Err 의 union]`)» — 셀 파이프 회피 표기가 두 인자 `Status[Out, Err]`(존재하지 않는 형태 · «two-argument `Status`» 호출과 혼동)로 읽힌다 → **MINOR-3**.

### 2.4 규범 정합(B-12) — 근거 좌표

- **R-3463 ↔ R-0687**(ninja b13): 한 블록 두 Work · 경계 = 굵은 선두 «**반환 주석의 `Status` 상자는 하나다**» 앞뒤. R-0687 «BC `ErrorSchema`/`Status` 를 실제 흐름에 맞게» 가 base 주석을 허용하고, R-3463 은 «값 변수를 base 로 주석해 통과시킨 형태도 같은 금지» 를 «상자 둘» 에만 건다 — 충돌 없음(good 픽스처 `-> PaymentOut | Status[OrdersErrorSchema]` 가 그 허용면).
- **R-3465 ↔ R-0681**(b1 ↔ b9): R-0681 은 오류 status 의 `response=` 값을 «concrete 하나면 그 concrete, 둘 이상이면 `Union`» 으로 요구하고, R-3465 는 «성공 본문» 의 익명 union 만 금지한다. 비대칭의 근거는 b1 이 가리키는 `architecture-api` §5.2 b7 «오류 본문의 union 은 각 오류 schema 가 … 자기 판별되므로 대상이 아니다» 로 설명된다 — 단 b7 의 앵커·어휘가 §5.4 와 어긋난다(MINOR-1 · §3-2).
- **R-3464 ↔ s012-3.1 b7**: «위 발행 봉투 불릿» = b7(R-0742~R-0748 · «discriminator 는 1종째부터 domain `StrEnum` 파생») — b9 가 b8(산문) 뒤에 오지만 «위» 참조는 같은 절 안이라 성립. 판별 키 규율 인용(`Literal` 파생)과 예시 `Field(discriminator="kind")`·`TarotCardOut(… "type")` 정합.
- **R-0331 rev2 ↔ R-0332/R-0333**: b16 의 새 문장은 «무관» 의 판정 기준을 정의하고(R-0331 소유 — scope 분할의 주어), R-0332(«무관 G2 는 auto 명시»)·R-0333(«auto 는 12-slot 증거 아님») 문장은 무변. `design-architect.md:39` «Ninja endpoint/error contract/response Schema 를 새로 만들거나 바꾸는 scope 라면 아래 계약(12-slot)을 적용한다» · :41~44 «모든 scope 의 명세에 12 slot … slot 이 빠지면 STOP · G1 미완료» · :48 slot 3 «error profile … 중 하나와 선택 근거» · `acceptance-tester.md:41` «12-slot/profile 이 빠지거나 모순되면 설계로 반송» — b16 의 «G1 반송(STOP — error profile 미결정 · design-architect 12-slot 의 적용 조건)» 과 정합. 관찰: :39 는 «오류 status 선언» 보다 넓은 트리거(새 Ninja endpoint 전부)라 R-0331 rev2 의 auto 금지 조건은 그 부분집합이다 — 모순 아님 · §4 ②.
- **R-0349 rev2 ↔ 검사기 docstring**(`check-api-error-controller-contract.py:18~26`): «표준 트리 슬라이스(모든 프로필) 코드 형상 규칙 2 · #648 origin `ninja.Status`/`ninja.responses.Status` · #649 `ninja.Schema`∧`pydantic.RootModel` · api/** + OHS `*_service.py` · overlap 비대상» — label «표준 트리 슬라이스(… #648 Status 상자 하나·#649 Schema+RootModel 동시 상속 금지)» 와 일치. 좌표 #648 def 줄(:7241) · #649 class 줄(:7234).

### 2.5 미러·계수(B-9·B-11·B-14·B-15)

- LEDGER 6행: `ledger_check2` 전 행 OK(graph = strip_marker span sha) · 소스 미러 3절 == ledger · codex final == ledger(strip). houserules-skill s007-4 행이 조각 1 행을 대체(마지막 행 기준).
- codex houserules SKILL 전 파일 diff(마커 제거 뒤): frontmatter `name` · `dddjango-discipline-cleancode`·`dddjango-architecture-ddd`·`dddjango-implementation-test` 치환뿐 — codex 스킬 디렉터리 실명과 일치(`architecture-api`·`discipline-tdd`·`implementation-*` 는 codex 도 bare · rv5-B §3-1 기준).
- target-counts 5수치·q4·rulepack label(R-3463~R-3467 신설 · R-0349/R-0331 갱신 · `expression` `@2026-09-04`) · corpus 11/11 · byte 6파일 `cmp` 동일 — 이 리뷰 시점 재실행.

### 2.6 정직 기록(B-16)

- `cad221b`: `piece2-summary.md` 2차 verify «base-core RED 1 = 봉인 후 골든 갱신 · 봉인 재발행 순서 착오 · d701df8 «verify 6/6» 거짓» + 3차 6/6(`verify4.log` 12줄 실기록) · 루브릭 4단계 문단 «정직 기록» · manifest `sealed_commit` 06fef51→d701df8(봉인 시점 HEAD 관례 유지 · status draft). 사실 서술은 정확하고 은폐 없음 — 커밋 메시지 자체는 이력 보존상 못 고치므로 기록·루브릭·회신(«정정 cad221b»)으로 봉합한 방식이 맞다.
- 부족한 것 둘: ① 루브릭 문단은 «정정 커밋 = 이 문단의 커밋» 이라 해시가 없다(회신 3 초안에만 `cad221b`) — 추적표·루브릭에 해시 1줄. ② 절차 결함(«봉인은 마지막 · verify 수치는 마지막 로그의 것») 이 `docs/DEVELOPMENT.md` §4 «봉인 파일을 고치면 봉인 재발행이 필요하다»(:81) 한 줄에 그치고 순서·기록 규칙이 없다. 메모리 레시피(`ontology-revision-recipe.md` 8행)도 «byte 미러 rsync → manifest_seal --write → make verify» 순서라 RED 뒤 골든 재생성 경로가 없다 → **MINOR-5**(§3-5 문안).

### 2.7 회신 3 초안(B-17) — 정본 대조

- 맞는 것: S-5 행의 R 번호·조항(R-3463 §2.2 · R-3465 · R-3464 §3.1 · R-3466 · R-3467 §5.2 · R-0331 rev2 «무관 = 승인 12-slot 유무 · 12-slot 없이 … auto 금지·G1 반송») · S-1/S-4 행 R 번호 · ⑤ «루트 필터로 대상 밖 · 기존 #493/#645 무변» = b28 «신규 3규칙은 `application/`·`framework/` 루트만» · ③ R-3154 rev2(«적지 않는다 · `inlines` 달면 red») · ⑧ #649.
- 어긋난 것(MINOR-4):
  - :5·:24·:28·:34 «앵커 격리(N∖L)» — `registry_gate.py:13` «귀속 = N ∖ L» · :19 «legacy 잔존(L∩N)은 exit 에 안 들어가되 항상 보고». legacy 를 설명하는 자리에 귀속 산식을 붙여 라벨이 뒤집혔다.
  - :32 «오류 응답을 `response=` 에 선언한 컨트롤러의 G2 는 `dddjango-code-json` 프로필로 돌린다» — 정본은 «승인 12-slot 의 profile(code-json | preserve-established)로 돌린다 · 12-slot 없이는 auto 금지·G1 반송»(b16 · design-architect :48). spring 신규 표면이면 결과적으로 code-json 이지만 규범 문장으로는 과결정.
  - :16 «기존 규범(R-3443)의 admin 변종» — R-3443 prefLabel «값 객체 안 선언 타입 재검사·강제 변환 금지 — 타입 좁히기는 값 객체 호출 전 경계 소유»(주어 = 값 객체). admin display 메서드는 그 규범의 대상이 아니라 «취지의 변종» 이다(추적표 :18 도 «보고자: A/R-3443 의 admin 변종»).
  - :12 «결정표 6행 R-3451~R-3457» — R-3451 은 b8 선두 문장, 결정표 6행은 R-3452~R-3457(rv3-B §3-10).

---

## 3. 정정 문안

### 3-1 MAJOR-1 · `workspace/design/2026-08-11-predicates.md` #648·#649 행 2(:247 #650 행 뒤 · `ast` 는 확정 술어만 · 셀 안 파이프 0)

```
| 648 | ast | 확정 ⑴표준 트리 슬라이스 대상(api/** 전 파일 + OHS `*_service.py` · 프로필 무관) 함수의 반환 애너테이션을 평탄화(파이프 union·`Optional`·`Union`·문자열 주석 재파싱)한 구성원 중 `Status[…]`(origin `ninja.Status`/`ninja.responses.Status` — 모듈 import 바인딩으로 dotted 해소)가 2개 이상이면 위반 — `check-api-error-controller-contract` 가 def 줄 좌표로 방출(overlap 억제 비대상 · `-> Status[Out 과 Err 의 union]` 또는 `-> Out 과 Status[Err] 의 union` 은 통과) |
| 649 | ast | 확정 ⑴ClassDef 기저에 ninja `Schema`(origin `ninja.Schema`/`ninja.schema.Schema`)와 pydantic `RootModel`(`pydantic.RootModel`/`pydantic.root_model.RootModel`)이 함께 있으면 위반 — 파일 한정 없음(트리 슬라이스 대상 파일 전부) · class 줄 좌표 · `RootModel[Annotated[…, Field(discriminator=…)]]` 단독 상속은 통과 |
```
절차: md 직접(산문 문서 · 온톨로지 밖) → `spec_lint` 0(⑥ 등급 `ast` 일치 · 참조 #N 생존) → `make verify`(base-core). `piece2-summary.md` 등재 항목에 «predicates #648·#649» 추기.

### 3-2 MINOR-1 · `architecture-api-final` s022-5.2/**b7** 앵커·어휘(in-place · Expression 무신설 — ⑤-1 B 선례 · 출처는 rv1-B §3.12 초안이라 B 축 자기 정정)

«… 오류 본문의 union 은 각 오류 schema 가 고정 `code` 로 자기 판별되므로 이 요구의 대상이 아니다(§6 에러 프로필)\n\n» →
«… 오류 본문의 union 은 각 오류 schema 가 고정 공개 식별자(code 프로필의 `<Bc>ErrorCode` 값 · RFC 9457 의 `type`)로 자기 판별되므로 이 요구의 대상이 아니다(§5.4 에러 프로필)\n\n»

근거: `architecture-api/references/final.md:230` «### 5.4 에러 프로필 선택» · :259 «## 6. RFC 9457 에러 응답 형식» · §5.4 code-json 절 «승인 shape 의 한 공통 필드를 BC `ErrorCode(StrEnum)` 으로 좁혀 … 그 필드명은 고정하지 않는다». prefLabel R-3467 «오류 union 은 고정 code 로 자기 판별» 은 요약 범위 안이라 무변 가능(원하면 «고정 공개 식별자» 로 같이).
절차: rdflib `set_text`(@ko) → canon → gate → `ontology_render --apply architecture-api-final` → LEDGER `architecture-api-final s022-5.2` 재기준선 → 소스 미러 span 교체 → `corpus_mirror_sync --write`(codex byte) → `make rulepack` → verify. ninja b1 의 «(`architecture-api` §5.2)» 는 그대로(b7 이 §5.2 에 있다).

### 3-3 MINOR-2 · `2026-08-08-tree-revision-spec.md:387` #63 행 — 규칙 문장 원복 + 08-25 span(09-01 span 앞)

규칙 열 «오류 응답은 operation 이 response={status: <Bc>ErrorSchema} 로 직접 선언하고 openapi_extra 보충·… 사후 변형하지 않는다.» 로 되돌리고 바로 뒤에:
```
<span>2026-08-25 · **base 뭉뚱그림 금지** — `response=` 값은 그 status 에서 실제 반환하는 오류 타입 그대로(concrete 하나=그 concrete · 둘 이상=`Union` · 명시값 base=base)다(R-0681 rev2·R-0087 rev2 · 검사기 docstring·조치 문면은 09-04 S-5 에서 정합).</span>
```
(기존 09-01 span 유지.) `rule-owner-map.md:61` 비고는 이미 span 형식이라 무변.

### 3-4 MINOR-3 · 같은 문서 :1177 #648 셀

«(`Status[Out, Err 의 union]`)» → «(`Status[…]` 하나 안에 `Out` 과 `Err` 의 union)». `Out` 과 `Status[Err]` 의 union 쪽은 그대로.

### 3-5 MINOR-5 · 절차 성문(정직 기록 후속 · 규범 축 제안)

- `docs/DEVELOPMENT.md:81` 뒤에 1문장:
  «**봉인은 커밋 직전 마지막 단계다** — `make verify` 가 RED 여서 봉인 대상(측정 도구·byte 골든 EXPECTED·매트릭스)을 다시 고쳤으면 `manifest_seal.py --write` 를 다시 발행하고 `make verify` 를 처음부터 다시 돈다. 커밋 메시지·기록의 verify 수치는 **마지막 실행 로그**(evidence 경로 병기)의 것만 적는다 — 중간 실행의 green 을 옮겨 적지 않는다(2026-09-04 `d701df8` «verify 6/6» 거짓 표기 · 정정 `cad221b`).»
- 메모리 `ontology-revision-recipe.md` 8행: «검사기 수정 시 codex byte 미러 rsync → 매트릭스·byte 골든 `--emit-expected` → **마지막에** `manifest_seal.py --write` → `make verify` · RED 로 봉인 대상을 다시 고쳤으면 봉인 재발행 → verify 재실행 · 커밋 메시지 verify 수치는 마지막 로그의 것만(09-04 d701df8/cad221b 선례)» — 사용자 메모리라 코디가 반영.
- 루브릭 4단계 조각 2 문단 «정정 커밋 = 이 문단의 커밋» → «정정 커밋 = `cad221b`» (⑤-2 결과 커밋에서 1줄).

### 3-6 MINOR-4 · 회신 3 초안(`2026-09-04-field-report-reply-3.md`)

- :5 «앵커 격리 전 전량» → «registry_gate 앵커 차분 전 전량» · :24·:34 «앵커 격리(N∖L)라 손대기 전까진 exit 에 안 들어가고» → «registry_gate 앵커 차분에서 legacy(L∩N · exit 불산입·보고만)라 손대기 전까진 exit 에 안 들어가고, 손대면 그 자리가 귀속(N∖L)된다» · :28 «전부 앵커 격리 — 새 레인 산출물만 막힌다» → «전부 legacy(앵커 차분 · exit 불산입) — 새 레인 산출물만 막힌다».
- :32 첫 문장 → «**오류 응답을 `response=` 에 선언한 컨트롤러의 G2 는 승인 12-slot 의 profile 로 돌린다**(spring 신규 Ninja 표면이면 `dddjango-code-json`) — `auto` 는 #63·#125 를 재운다(…). Coordinator 문면(R-0331 rev2)이 이제 «승인 12-slot 없이 오류 status 를 선언했으면 auto 금지 · G1 반송(error profile 미결정)» 으로 못 박았다.»
- :16 N-1 판정 열 → «R-3443(값 객체 안 선언 타입 재검사 금지) 취지의 admin 변종 — 규범 확장 없음 · 새 항목 아님».
- :12 «결정표 6행 R-3451~R-3457» → «§4 레코드 규범 R-3451 + 결정표 6행 R-3452~R-3457».
- ③ «1288e4a 에서 붙인 주석은 허용(스텁 타입과 같으면)이되 필수가 아니다» → «… 허용(스텁 타입과 같고 그 타입에 `Any` 가 없을 때 — `inlines` 는 달 수 없다)이되 필수가 아니다»(b5 rev 문면 그대로).

---

## 4. 사각(이 리뷰가 닫지 못한 것 · ⑥ 입력)

1. **b1 경질 개행 폭**: ninja final :112 가 88자(문단 폭 ≈67). 정본은 블록 리터럴이라 적법 — 다음 ninja 접촉 때 3줄로 재접합(LEDGER 재기준선 동반) 여부는 코디 선택.
2. **R-0331 rev2 트리거의 부분집합성**: design-architect :39 는 «새 Ninja endpoint 전부» 에 12-slot 을 요구하나 Coordinator 의 auto 금지는 «오류 status 를 `response=` 에 선언한 컨트롤러» 에만 건다. 오류 선언 없는 새 Ninja 표면이 12-slot 없이 «무관» 으로 흐르면 G1 결함(architect 몫)이지 G2 판정식의 구멍은 아니다 — 기계 봉합(#63 auto 사각) 이월과 함께 회신 §4 에 이미 있다.
3. **성공 200 의 nullable 본문**(`A | None`): R-3465/R-3467 «둘 이상의 모양» 에 None 이 «모양» 인지 문면이 안 가른다. 실전 발화 0 — 이월 1줄 후보.
4. **predicates 헤더 «전수는 ast 281 · ast+ 55»**(:16)는 08-11 시점 수치라 stale — MAJOR-1 정정 때 건드리지 않는다(이력 문장).
5. `spec_lint` ⑥ 이 `ast` 신설 행 부재를 못 잡는다(ast+ 만 강제) — «신설 규칙(직전 배치 이후 번호)은 등급 무관 predicates 행 필수» 로 린트 강화는 도구 축(A) 몫 · 이번 범위 밖.
6. 규범 축 밖 관찰: `T2-0b-manifest.json` 이 cad221b 로 draft 재봉인(sealed_commit d701df8) — 릴리즈 뒤 docs(seal) 몫(rv5-B §4-5 와 같음).

— 끝. 산출: `$S/rv5B2/{struct_check2.py,struct_check2.txt,ledger_check2.py,ledger_check2.txt,text_cmp2.py,text_cmp2.txt,diff-ontology2.txt,diff-md2.txt,gate.log,tools.log}`.
