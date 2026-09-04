# ⓪ 지도 — «누구를 고치는가» 온톨로지·검사기·배선 좌표 (코디 직접 확인 · 2026-09-04)

도구: `.venv/bin/python` + rdflib(`scratchpad/fr3/map/blocks.py` — 섹션/블록 덤프). 좌표는 `ontology/rules/<doc_key>.ttl` 기준. 채번 계획은 ②에서 확정(여기는 «빈 자리» 확인).

## 채번·전제

- ISSUED 마지막 = R-3450 → 신설은 **R-3451부터**. 검사기 규칙 최대 = #645 → **#646(S-1)·#647(S-4)·#648~#650(S-5 ⓐⓑⓒ)** 후보(등재 3문서 충돌은 ②에서 spec_lint로 확인).
- 섹션을 문서 **말미**에 추가한 선례: 9ef6c4f(houserules-final s018-5 «§5 driven 출구 면제» · 밀림 0) — Section 노드(`headingSnapshot`·`inDocument`·`sectionOwner`) + 블록 + wiring 2줄 + ISSUED + LEDGER + `workspace/eval/fixtures/ontology_gate/target-counts.json` + `fixtures/rulepack/query-golden.json` + rulepack + 소스/codex 미러. 중간 삽입 선례는 여전히 없음(블록 확장 또는 말미 추가만).
- 블록 IRI는 `…/s0NN-<번호>/bN` · `djr:order` 1..n 연속 · 새 블록 = 말미 append 또는 기존 블록 text 확장.

## S-1 — django-stubs 제네릭 기저

| 무엇 | 좌표 | 조치 | 읽는 이(wiring 선례) | 집행 |
|---|---|---|---|---|
| 규칙 문장(모델 타입 인자 필수 · monkeypatch 전제 · 별칭 대안 · `# type: ignore[type-arg]` 금지) | `discipline-houserules-skill` s007-4(§4 타입 어노테이션 · b1~b7 · b7=R-3447/R-3448) → **새 b8**(신설 R-3451) | 블록 append | §4 규범은 전부 `agent-discipline-reviewer`(71) · 일부 `agent-coder`(6) → 새 R은 discipline-reviewer + coder | `#646`(`enforcedBy c/check-public-surface-annotation.py`) |
| 셋업 조건(«표준 도구가 없으면 셋업» 옆 · `django-stubs-ext` 운영 의존성 + settings `monkeypatch()` 는 발주측/Phase 0 전제 · 레인 허용 경로 밖) | `discipline-houserules-skill` s011-6.1/b1(R-3163) | b1 text 확장(R-3163 amendment) 또는 §4 b8 안 한 문장으로 갈음(②에서 택일) | 같음 | — |
| admin 예시 1벌(별칭 4 + inline·admin · 직접 표기/별칭 두 형태) | `implementation-django-final` — admin 절 **없음**(s003-1 … s079-16.5 · «admin» 언급은 산문 주석 1줄뿐) → **말미 새 섹션 s080-17 «Django admin 타이핑»**(선례 9ef6c4f) 또는 s038-7 «폼과 유효성 검증»(b1 웹 폼 위임 + b2 `---`)에 블록 append | 신설 섹션(권장 — 절 제목이 내용과 맞음) | implementation-django 규범은 전부 `agent-discipline-reviewer`(220) — coder는 스킬을 직접 로드 | — |
| django-web 맨몸 예시 정정 | `implementation-django-web-final` **s007-6/b9**(kind-code · `class ArticleForm(forms.ModelForm):`) | 코드 블록 text 수정(norm 없음 · LEDGER 재기준선) | — | — |
| R-12 발주 가이드 | 로드맵 R-12 행(문서 미착수) | 반영 문구 추기(S-3와 같은 방식) | 발주자 | — |

## S-4 — 딕셔너리-레코드 금지

| 무엇 | 좌표 | 조치 | 읽는 이 | 집행 |
|---|---|---|---|---|
| R-3447 개정(«JSON 문서는 `Mapping[str, object]`» 삭제·대체) | `discipline-houserules-skill` s007-4/b7(R-3447 rev1 `@2026-09-04`, R-3448) | b7 text 수정 + R-3447 **rev2**(같은 날짜 충돌 → Expression IRI `@2026-09-04b`? ②에서 확인: 같은 날 두 번째 개정 선례 유무) | discipline-reviewer | `#647` |
| 한 줄 규칙 + 붙임 2·예외 1 + 결정표 6행 | s007-4 **새 b9**(신설 R-3452 · 결정표는 kind-table-row 블록 6개 또는 한 블록 안 표 — ②에서 형식 확인: 표는 SKILL.md에 선례 있는가) | 블록 append | discipline-reviewer + coder + design-architect(houserules 로드) | `#647` · `json.load` ⓓ 후보 |
| «어떻게»(TypedDict·`TypeAdapter`·`JsonValue`·`Literal` 판별 union) | `implementation-python-final` **s007-1.5**(b1=R-2715 «TypedDict를 사용하라» 권고 · b2 code) → b1 text 확장(R-2715 amendment) + **새 b3 code**(예시) | 블록 확장·append | discipline-reviewer(80) | — |
| architecture-ddd 예시 정정 `values: dict[str, Any]` | `architecture-ddd-final` **s040-5.5/b10**(kind-code · Knowledge Level 예시) | 코드 블록 text 수정(LEDGER) | design-review-ddd(113) | — |
| ⓓ 후보 배선 | `command-dddjango` s007/b6(R-0284 rev3 `@2026-09-04` — 감사 입력 «ⓓ 후보» 목록) → **rev4**(json.load 후보 추가) · s007/b28(R-0345 rev2 — registry #11 줄 «#645» 언급) → **rev3**(#646·#647 추가) | 두 블록 text 수정 + 개정 2 | Coordinator | — |

## S-5 — ninja `Status`·base 뭉뚱그림·`Schema`+`RootModel`

| 무엇 | 좌표 | 조치 | 읽는 이 | 집행 |
|---|---|---|---|---|
| 문장 1(반환 주석은 `Status` 하나 · `Status[A] \| Status[B]` 금지) | `implementation-django-ninja-final` **s009-2.2**(Operation 선언 · b1~b18 · b13=R-0687 «반환 타입을 명시한다 — `-> object` 금지» · b14=R-0688/R-0689 «성공은 Schema 또는 `Status`» · b18 code `-> Status[OrderOut \| …]`) → b13 text 확장(R-0687 amendment) 또는 새 b19(신설 R) — ②에서 택일 | 블록 확장/append | design-review-api(33)·discipline-reviewer(132) | ninja 검사기 ⓐ |
| 문장 2(성공 union 응답 = `RootModel` 단독 · `Schema` 병행 금지 · 익명 union 금지) | 같은 s009-2.2 새 블록(신설 R) + 예시 code 블록 | append | 같음 | ninja 검사기 ⓒ |
| base 뭉뚱그림 기존 규범 | s009-2.2/b9(R-0681/R-0682) · s023-6.2/b34(R-0086~R-0090) — **문면 변경 없음** · 검사기 ⓑ가 집행만 추가 | wiring `enforcedBy` 추가 | — | ninja 검사기 ⓑ |
| 계약 문면(성공이 두 모양이면 discriminated 컴포넌트 · 익명 anyOf 금지) | `architecture-api-final` **s022-5.2 «응답 계약»**(b1~b6 · R-1967~R-1972) — discriminator/oneOf/anyOf 언급 **0** → 새 b7(신설 R) | append | design-review-api(146) | — |

## 검사기·등재·미러(공통)

- `dddjango/scripts/check-public-surface-annotation.py`(#493·#645) ← #646·#647 (+ ⓓ 후보 `json.load`) · `check-api-error-controller-contract.py`(#120~#132·#571…) ← ⓐⓑⓒ 3규칙. 둘 다 `codex-dddjango/skills/dddjango/scripts/` byte 미러.
- 등재 3문서: `workspace/design/2026-08-08-tree-revision-spec.md`(7열 행 + 집계 `ast+` 57→? · 계 547→?) · `2026-08-11-predicates.md`(3열 · 셀 안 `|` 금지) · `workspace/plan/2026-08-11-rule-owner-map.md`. `spec_lint.py` 0.
- 픽스처: `workspace/eval/fixtures/public_surface/{good,bad_rules}` · `api_error_controller*` · 삼중 등재 `fixture_matrix.py` · `findings_count_matrix.py`/`checker_baseline_matrix.py`/`checker_cross_matrix.py` `--emit-expected` · `registry_gate_smoke.py` P0′ · `gen_pregate_symbol_kinds.py --check` · `manifest_seal.py --write` · `make verify` 6/6.
- 온톨로지: `ontology_render --apply <doc_key>`(houserules-skill · implementation-django-final · django-web-final · python-final · ddd-final · ninja-final · api-final · command-dddjango = **8 doc**) · LEDGER · ISSUED · target-counts · `query_golden_check --emit` · `make rulepack` · 소스 미러 span 교체 + `corpus_mirror_sync --write` · codex hand 미러 3(SKILL.md 계열).

## 지도에서 ②가 정할 것(택일)

1. S-1 admin 예시: 새 섹션 s080-17 vs s038-7 블록 append.
2. S-1 셋업 조건: §6.1 b1 확장 vs §4 b8 안 한 문장.
3. S-4 결정표 형식: table-row 블록 6개 vs 한 블록 안 표(SKILL.md 표 선례 확인).
4. R-3447 같은 날 2차 개정의 Expression IRI 규칙.
5. S-5 문장 1: R-0687 확장 vs 신설 R.
