# ③ 계획 리뷰 — 리뷰어 A(기술 축 — 검사기·실행기·픽스처·매트릭스) · 현장 보고 수리 2 (2026-09-04)

독립 리뷰. 대상 = `2026-09-04-field-report-repair-2-plan.md` §1 E·G·H 의 검사기·실행기·픽스처·매트릭스 명세와 §2 순서. 저장소는 읽기만 했고, 프로토타입 패치·픽스처 초안·전 매트릭스는 `scratchpad/fr2/rv3A/` 아래에서 돌렸다 — `repo/`(rsync 사본 · 매트릭스·러너), `clone*/`(git 이력이 필요한 `registry_gate_smoke`·`rulepack_smoke`), `iso/`(조사자 격리 사본 `fr2/DE/iso/{spring,kkebi}` 재사용 · python 3.14.7), `H/`(`fr2/H/spring` 클론 재사용 · 실행 뒤 9c8814e 복원), `anyjudge/`(변종 판정표), `pregate_demo/`(`empty` 스텁 데모). 패치 원문은 `rv3A/apply_patches.py`(E 헬퍼 4 + `_check_explicit_any` · H 가드 2 · S3 문면 · fixture_matrix 삼중 등재 2행 · codex byte 미러).

## 1. 판정 표

| 항목 | 판정 | 핵심 근거 |
|---|---|---|
| E 검사기 — `_explicit_any` 설계 ↔ 코드 구조 | **MAJOR(설계는 성립 · 문장 3곳이 코드와 다름)** | 프로토타입이 픽스처·양 저장소에서 계획 기대를 정확히 낸다(아래). 그러나 ⑴ «Name 이 모듈 바인딩으로 `typing.Any`/`typing_extensions.Any` 로 해소» — `_module_bindings`(:147-183)는 값에 **원명만** 남기고 출처 모듈을 버린다(`from typing import Any as _Any` → `{"_Any": "Any"}` · `from mypkg import Any` 도 같은 값) → 그 표로는 typing 출처를 가를 수 없고 `Any: type = object` 재정의 뒤 `_resolved_name` 폴백이 `"Any"` 를 돌려줘 오탐. 별도 `_any_bindings(mod) -> (names, mods)`(같은 if/try 걷기·그림자 pop) 가 필요하다 ⑵ 자리 ①②③(`_check_signature` 211-226 · AnnAssign 265-268 · 속성 320-322)은 `out: Findings` 만 받는다 — ⓓ 를 내려면 `_scan_stmts`/`_scan_class`/`_check_signature` 3 시그니처에 `Candidates` 를 꿰거나, **별도 패스** `_check_explicit_any(mod, rel, findings, candidates)` 를 `_scan_stmts` 뒤에 한 줄 추가(프로토타입 — #493 과 구조적으로 독립·ordered stdout↔record 대조 통과) ⑶ «`self`/`cls`·dunder 는 기존 면제 그대로» — `_check_signature` 에 **dunder 면제는 없다**(수신자 skip 뿐 · `_is_dunder` 는 대입 이름·`self.x` 용). spring 8 중 6 이 `__init__(*args: Any, **kwargs: Any)` 라 dunder 를 면제하면 spring 2 가 된다 |
| E 검사기 — 변종 판정표 | **검증됨(+MINOR 3)** | 22 형상 실측(§2.2 표): TYPE_CHECKING 안 import → bare ✓ · `cast(Any, x)` → 무시 ✓ · 문자열 `"Any"`/`"Optional[Any]"` → bare ✓ · `Any \| None`·`None \| Any`·`Optional[Any]`·`Union[Any, None]` → bare ✓ · `typing_extensions.Any`·`te.Any` → bare ✓ · `from __future__ import annotations` 무영향 ✓ · `Any: type = object`·로컬 `class Any` → 그림자(무시) ✓ · `Annotated[Any, …]`·`type[Any]`·`Callable[[Any], R]`·`Callable[..., Any]`·`Union[Any, X]` → nested(ⓓ). MINOR 권고: `Annotated[Any, …]` 는 타입 체커에 투명하므로 bare 로 · `Union[Any, X]`/`Any \| X` 는 mypy 가 Any 로 흡수하므로 bare 로 · import 없는 bare `Any`(mypy name-defined 오류)는 현재 무시 — fail-closed 로 «모듈 수준 재정의로 그림자되지 않은 `Any` 이름은 Any» 권고(양 저장소 실계수 0 이라 효과 0 · c12/c13/c18 은 검출 한계로 docstring 에 기록) |
| E 검사기 — ⓓ 채널·출력 형식 | **검증됨** | `Candidates.add("#645", where, msg, 물음)` → 라인 `[ⓓ#645] …— 물음: …` + info 레코드(exit 불산입). cross matrix `INFO_ID=\[ⓓ#(\d+)\]` 관찰 열 · count matrix `_INFO_LINE` · baseline `unparsed` 열에 각각 정확히 실린다(아래 매트릭스 실측) |
| E 검사기 — #493 ↔ #645 독립 | **검증됨** | `def f(a, b: Any):` 한 줄에서 `[#493]`×2(a·반환) + `[#645]`×1(b) 동시 발화(c17) · `x: Any` 는 #493 을 내지 않는다(c01) → «주석 존재 = #493 · 주석 내용 = #645» |
| E 소급 기대치(무손실 판정식) | **MAJOR(오기)** | 패치본 격리 실행 `application/*` `[#645]` = **spring 10 · kkebi 14** = 프로덕션 8/10(① C 목록과 파일·줄 전건 동일) + **`test/factories` 2/4**(MATERIAL_DIRS 는 검사 대상 — `translations(**kwargs: Any)`·factory_boy `_create(*args: Any, **kwargs: Any)`). 계획의 «spring 8 · kkebi 10» 을 ④ 가 그대로 검증식으로 쓰면 red 다. ⓓ#645 `application` 프로덕션 = spring 112(시그니처 nested 42 + 변수 bare 37 + 변수 nested 33) · kkebi 123(26 + 61 + 36) — 계획 «변수 37/61 + nested» 와 정합 |
| E 픽스처(good 1 · bad 1) | **검증됨(+MINOR 2)** | good `admin/order/form/order_form.py`(Form `__init__(*args: object, **kwargs: object)`·`clean() -> dict[str, object]`·`TypeIs[Mapping[str, object]]`) → 자기 검사기 exit 0(패치본·현행 둘 다) · bad `any_signature.py` 6형 + `y: dict[str, Any]` → **#493 8 · #645 6 · ⓓ#645 1 · #358 2 · #456 2 · ⓓ#69 2**(계획 기대와 정확 일치·타 규칙 불변). MINOR ⑴ good 파일이 `admin/order/` 를 새로 여니 cross matrix 의 `check-layer-skeleton` 이 트리 84행 `panel.py` 부재로 #488 26→27 — **0바이트 `admin/order/panel.py` 를 함께 두면 public_surface 레인 census 5행 전부 무변**(실측) ⑵ bad 에 `Any \| None`·문자열 `"Any"` 형을 더해 언랩 경로를 픽스처로 고정 권고(6→8) |
| E 매트릭스 EXPECTED | **MAJOR(baseline 누락)** | count matrix 행 = `(2, 18, 3, "#358×2,#456×2,#493×8,#645×7,#69×2", "60828c5712368fe3", "15e0aa82b574b685", "d43ca712bb7d3484")` — 분포 문자열은 위반+info 합산이라 **`#645×7`**(위반 6 + ⓓ 1)·info 2→3 로 적힌다(계획 «+#645×6» 은 위반만). **`checker_baseline_matrix` 도 바뀐다**: `(2, 12, 12, 4, False)` → `(2, 18, 18, 5, False)`(parsed +6 · unparsed +1) — 계획의 «checker_baseline_matrix·guard-zero 무변» 중 baseline 은 거짓(guard-zero 는 무변 ✓). 14필드 oracle·ordered stdout↔record 대조는 통과 |
| E cross matrix | **검증됨(조건부)** | 27 레인 good + skeleton 에 `Any` 0(grep) → #645/ⓓ#645 신규 0 실측. 조건 = good 파일 배치에 `panel.py` 동반(위) |
| H 검사기 — 함수 경계 | **검증됨(+MINOR 1)** | `_check_port_contract`(243-278)에 든 규칙 = #219·#551·#220·#241·#212·ⓓ#485 뿐. #218(211-213)·#225·#216·#214·#64 는 `_check_capability_folder` 에, #576 은 `_check_fake`(1027-) 에 있어 유지 · usecase-dto 는 #193(343)이 가드 앞에서 서고 `_check_entry`(382-)가 #635·#211·ⓓ#194 만 가진다 · `main` 의 `_check_event_steps(entry)` 는 빈 파일에서 무발화. bypass `_query.py`·uow 는 클래스 «하나» 규칙이 없어 빈 파일에 침묵(skeleton/good_bc 의 0B `email_sender_query.py` 실측) → «예외 2건» 정확. MINOR: import 는 두 파일 다 이미 `import checker_target` + `checker_target.slot_file/skeleton_placeholder(p)` 속성 호출(port-adapter :641) — 계획의 `from checker_target import skeleton_placeholder` 대신 그 스타일 |
| H 카탈로그 3커밋 | **검증됨** | 패치본 · `fr2/H/spring` 클론 · ONLY 2검사기: `59d08c7` #219 0·#635 0(5→0 · 두 검사기 **exit 0**) · `99253ce` #218 2·#193 3·#576 2(+#488 5 는 무접촉 skeleton 검사기 → 12 불변) · `9c8814e` 0 |
| H pre-gate | **검증됨** | mini_repo 위 `empty` 6행(port 2·use case 4) 데모: 현행 실행기 귀속 4(#488×2·**#219·#635**) → 패치본 귀속 2(#488×2 만). `pregate_fixture_run.py` 패치본 **PASS**(15종+E 6단계+imports 3+enforce 7+check-report 14+유닛) |
| H 픽스처 | **검증됨** | `NEGATIVE_LANES` 삼중 `(script, fixture, sub)` = 기대 exit 0 판형 그대로 · 최소 집합: port 레인 = `application/orders/application_layer/port/{clock/clock_port.py(0B)·clock/exception.py·ledger/ledger_port.py(docstring-only)·ledger/exception.py}` 4파일(#74 가드는 `application_layer` 실존으로 무발화·domain/driven 불요) · usecase 레인 = good 사본 + `place_order_use_case.py` 0B + `cancel_order/` docstring-only 진입점·0B command/query/result. 현행 검사기 → #219×2 / #635×2 red · 패치본 → exit 0 · `fixture_matrix` **104/104** |
| H 무손실 판정식 | **MAJOR(두 곳 거짓)** | ⑴ **cross matrix 는 무변이 아니다**: `skeleton/good_bc` 는 0B `place_order_use_case.py`·`email_sender_port.py` 를 갖고 27종 전부가 그 레인을 돈다 → EXPECTED `('skeleton','check-port-adapter-pairing.py'): (2, ((219,1),), (), '최소성')`·`('skeleton','check-usecase-dto-placement.py'): (2, ((635,1),), (), '최소성')` 2행이 «기대 red 소멸» → `--emit-expected` + 사유 필수 ⑵ **`registry_gate_smoke` P0′ red**(H 단독으로 재현 · E 단독은 31/31): `_pre_repair_gate` 가 `34c74a6` 의 **`dddjango/scripts` 트리째**(검사기 포함)를 풀어 현행 게이트와 마스킹 출력 byte 대조 — good_bc 의 legacy 절에서 #219/#635 행이 사라져 diff ≠ 0. HEAD 양 저장소 `_port/_use_case` 0B 0 · 자기 레인 good/bad 무변 · count matrix 두 행 무변은 ✓ |
| G 실행기 S3 문면 | **검증됨(+MINOR 1)** | `pregate_fixture_run._enforce_unit_checks` 는 `len(BLIND_SPOTS)==9` 와 `S{i} ` 접두만 단언 · `--check-report` 정규식(`_REPORT_SECTION_RE`·`_HASH_RE`·`_ID_RE`(예보 항목 절 한정)·`_COUNT_RE` `예보 N건`·`_DEFECT_RE` `결손 N건`)은 사각 행을 보지 않는다 → 문면 병기본으로 번들 PASS. 봉인은 `design_pregate.py`(pipeline)·`check-*.py`·`checker_target.py`(scorer)·`rulepack.json`·`pregate_symbol_kinds.json`(packs)·`ontology/**`(graph)·agents/skills/commands/codex SKILL(plugin_payload) 전부 드리프트 → §2 1·2·3 뒤 **단 한 번** `--write`. MINOR: «`update` 잎의 import 는 전사 밖» 은 «실존 판정(⑴~⑶)은 받는다» 를 병기해야 S8/S9·`_parse_imports`(:497) 와 모순 없다 |
| §2 순서·검증 누락 | **MAJOR(6 단계 누락)** | Makefile `verify`(verify-ontology·base-core·base-cross·base-backstop·base-regen·web) 대조: ⑴ `gen_pregate_symbol_kinds.py` 재소성 — 소성물이 27종 `source_sha` 를 품어 검사기 1바이트 변경에도 `--check` red(실측) + codex JSON byte 미러 ⑵ `checker_baseline_matrix --emit-expected`(public-surface 행) ⑶ `checker_cross_matrix --emit-expected`(H 2행 소멸 · E good 배치) ⑷ `registry_gate_smoke` P0′ 수리 ⑸ 규칙 번호 등재는 **2문서가 아니라 3문서·6곳**: tree-revision-spec 규칙 행(7컬럼 계약 — 셀 안 `\|` 금지 · `Any \| None` 표기 불가) + **집계표 3표**(`ast+` 등급표 56→57 · 판정×어겼을때 표 · 읽는 법 «`ast+` 의 blocker» 55→56 · 계 546→547) + `2026-08-11-predicates.md` 술어 행(«확정·후보·물음» — `ast+` 면 ⑥ 필수 · #644 선례 f09434d) + rule-owner-map 행(`ast+` → ⓒ+ⓓ 모양). 셋 갖추면 spec_lint 0건 실측 ⑹ `manifest_seal --write` 위치 — 1·2·3 전부 뒤(계획 순서는 맞으나 «draft» 한 번임을 명시). 나머지(tree_mirror·reverse_coverage·checker_lint·findings_smoke·construct_drift·runtime_parity·rulepack_smoke(클론 14/14)·regen_loop·bc_registry·anchor_diff·api_error_backstop·fixture_matrix·pregate_fixture_run)는 패치본에서 green 실측 → §2 누락이어도 무해 |

## 2. 상세

### 2.1 실측 명령(재현용)

- 패치: `python3 rv3A/apply_patches.py <repo-root>` (사본에만). 문법·미러: `diff -rq dddjango/scripts codex-dddjango/skills/dddjango/scripts` = 동일.
- 격리 소급: `python3 rv3A/repo/dddjango/scripts/check-public-surface-annotation.py fr2/DE/iso/{spring,kkebi}` → `rv3A/iso/{spring,kkebi}.out`(exit 2 둘 다 — legacy 포함).
- 카탈로그: `ONLY=check-usecase-dto-placement.py,check-port-adapter-pairing.py python3 fr2/H/run_rules.py <commit>-rv3A rv3A/repo/dddjango/scripts fr2/H/spring rv3A/H` × {59d08c7, 99253ce, 9c8814e}.
- 매트릭스(사본 루트에서): `fixture_matrix.py` · `checker_baseline_matrix.py[ --emit-expected]` · `findings_count_matrix.py[ --emit-expected]` · `checker_cross_matrix.py[ --emit-expected]` · `pregate_fixture_run.py` · `spec_lint.py` · `checker_lint.py` · `reverse_coverage.py` · `gen_pregate_symbol_kinds.py --check` · `findings_smoke.py` · `construct_drift_report.py` · `runtime_parity_check.py` · `regen_loop_smoke.py` · `bc_registry_smoke.py` · `anchor_diff_smoke.py` · `api_error_backstop_matrix.py` · `manifest_seal.py --check --draft`. 클론(`rv3A/clone*`): `registry_gate_smoke.py` · `rulepack_smoke.py`.
- pre-gate 데모: `rv3A/pregate_demo/empty-slots-spec.md` 를 mini_repo 사본(git init·1커밋) 위에서 현행/패치 실행기로 `--report` 실행 → `run_{orig,patched}.out`.

### 2.2 E — 검사기 프로토타입과 변종 판정표

패치 요지(`check-public-surface-annotation.py`): docstring 헤더 #645 1문단 · 상수 `ANY_MODULES={"typing","typing_extensions"}` · `_any_bindings(mod)`(모듈 수준 ImportFrom/Import 만 · if/try 하위 걷기 · ClassDef/FunctionDef/Assign/AnnAssign 동명 재정의는 그림자) · `_is_any(node, names, mods)`(Name ∈ names · Attribute `X.Any` 이고 X ∈ mods) · `_unstring`(문자열 애너테이션 재파싱) · `_union_members`(`X | Y`·`Optional[]`·`Union[]` 평탄화) · `_explicit_any(ann) -> "bare" | "nested" | None`(루트 Any → bare · 합집합 언랩 뒤 None 제외 전 구성원 Any → bare · 하위 어딘가 Any → nested) · `_check_explicit_any(mod, rel, out, cands)`(부모 맵으로 in_class 판정 → posonly/args/kwonly/vararg/kwarg/returns · AnnAssign 전부 · lineno 정렬 방출) · `main` 의 `_scan_stmts(...)` 다음 줄에 호출 1행. exit 규약 무변.

| # | 형상 | 판정 | 비고 |
|---|---|---|---|
| c01 | `from typing import Any` · `x: Any` | bare(#645) · #493 무발화 | 기본형 |
| c02 | `if TYPE_CHECKING: from typing import Any` · `x: Any` | bare | if 하위 걷기 |
| c03 | `y: int = cast(Any, x)` | 무시 | 애너테이션 아님 |
| c04 | `Annotated[Any, "doc"]` | nested(ⓓ) | **권고 bare** — Annotated 는 투명 |
| c05 | `type[Any]` | nested(ⓓ) | |
| c06 | `Callable[[Any], int]` · `-> Callable[..., Any]` | nested ×2(ⓓ) | 데코레이터 판형 |
| c07 | `x: "Any"` · `-> "Optional[Any]"` | bare ×2 | 문자열 재파싱 |
| c08 | `from typing import Any` 뒤 `Any: type = object` | 무시 | 그림자 |
| c09 | `from __future__ import annotations` · `Any \| None` · `None \| Any` | bare ×2 | future 무영향 |
| c10 | `typing_extensions` · `te.Any` | bare ×2 | |
| c11 | `Any \| str` / `Union[Any, None]` / `Union[Any, int, None]` | nested / **bare** / nested | **권고**: 구성원 하나라도 Any → bare |
| c12 | import 없는 `x: Any`(future) | 무시 | **사각** — fail-closed 권고(실계수 0) |
| c13 | 함수 본문 안 `from typing import Any` · `y: Any = x` | 무시 | 검출 한계(docstring 기록) |
| c14 | ninja `Schema` 필드 `event_name: Any` | ⓓ(bare) | 결정 1 «후보» 그대로 |
| c15 | `self.value: Any = seed` | ⓓ(bare) | 자리 ③ |
| c16 | Form `__init__(self, *args: Any, **kwargs: Any)` | **bare ×2** | dunder 면제 없음 — spring 6 건의 본체 |
| c17 | `def f(a, b: Any):` | #493×2 + #645×1 같은 줄 | 독립 |
| c18 | `Loose: TypeAlias = Any` · `x: Loose` | 무시 | 세탁 경로(docstring 기록) |
| c19 | 지역 `y: dict[str, Any]` · `z: list[Any]` | ⓓ(nested) ×2 | |
| c20 | `async def f(x: Any, /, y: Any, *, z: Any) -> Any` | bare ×4 | posonly·kwonly·async·반환 |
| c21 | 중첩 함수·메서드·`@classmethod` | bare ×3 | `cls` 수신자 skip |
| c22 | 로컬 `class Any` 재정의 | 무시 | 그림자 |

격리 실행(패치본): spring `[#645]` 78 = application 10(프로덕션 8: fortune_record 2·promotion 2·service_policy 4 / factories 2) · framework 59 · fabfile 9 ; ⓓ#645 694(application 114 = 프로덕션 112 + 재료 2). kkebi `[#645]` 121 = application 14(프로덕션 10: identity 2·product_observability 2·saju 3·share 2·tarot 1 / billing factories 4) · web 53 · scripts 17 · fabfile 37 ; ⓓ#645 385(application 134 = 123 + 11). #493 은 spring 3,225 · kkebi 173 로 조사자 기준선과 동일(불변).

### 2.3 E — 픽스처·매트릭스

- good 초안 `public_surface/good/application/orders/driven_layer/django_orders/admin/order/form/order_form.py` — `_is_mapping(value: object) -> TypeIs[Mapping[str, object]]` + `OrderForm(forms.Form)`(선언적 본문 면제 · 메서드 검사) `__init__(*args: object, **kwargs: object) -> None` · `clean() -> dict[str, object]`(`raw: object` 즉시 좁힘 · isinstance 뒤 raise 없음이라 ⓓ#69 0). 자기 검사기 exit 0(현행·패치). cross: `admin/order/` 신설로 `check-layer-skeleton` #488 26→27(트리 84행 `panel.py`) — 0B `admin/order/panel.py` 동반 시 public_surface 레인 5행 census 무변 실측.
- bad 초안 `public_surface/bad_rules/application/orders/application_layer/order/place_order/any_signature.py` — `take_bare(x: Any)`·`give_bare() -> Any`·`take_optional(x: Optional[Any])`·`take_alias(x: _Any)`·`take_attribute(x: typing.Any)`·`take_star(**kwargs: Any)` + `hold_nested()` 안 `y: dict[str, Any] = {}` → #645×6 · ⓓ#645×1 · #493×8 불변.
- `findings_count_matrix` 신 행: `"check-public-surface-annotation.py": (2, 18, 3, "#358×2,#456×2,#493×8,#645×7,#69×2", "60828c5712368fe3", "15e0aa82b574b685", "d43ca712bb7d3484")` · port-adapter/usecase-dto 행 무변(두 bad_rules 에 placeholder 형 `_port/_use_case` 없음 — 1문장 파일은 전부 `class X: ...` 또는 `from __future__` 라 placeholder 아님). 커밋 사유 형식(docstring 규율 «검사기별 사유 전건») 예: `findings_count_matrix: check-public-surface-annotation #645 신설 — bad_rules any_signature.py 위반 6(bare 시그니처)·info 1(nested 변수) 추가 · 기존 #358/#456/#493/#69 계수 불변`.
- `checker_baseline_matrix` 신 행: `"check-public-surface-annotation.py": (2, 18, 18, 5, False)` (guard-zero 행 무변).
- `checker_cross_matrix`: `Any` 0 → #645 영향 0. good 배치 조건 위와 같음.

### 2.4 H — 검사기·카탈로그·pre-gate·픽스처·스모크

- 패치 요지: `_check_port_contract` 첫 줄 `if checker_target.skeleton_placeholder(py): return` · `_check_use_case` 의 `if entry is not None:` → `if entry is not None and not checker_target.skeleton_placeholder(entry):`. 두 파일 모두 이미 `import checker_target` 상태.
- 카탈로그(§1 표) · pre-gate 데모(`empty` 6행 → 귀속 4→2) · 픽스처 2레인(현행 red → 패치 exit 0 · `fixture_matrix` 104/104).
- `registry_gate_smoke` P0′: `_pre_repair_gate()` 가 `git archive 34c74a6 dddjango/scripts` 를 통째로 풀어 그 트리의 `registry_gate.py`(→ 그 트리의 검사기 27종 import)로 같은 good_bc 파생 저장소를 돌려 `_mask` 출력·sidecar 를 현행과 byte 대조한다. good_bc 의 0B `place_order_use_case.py`·`email_sender_port.py` 가 현행에선 legacy #219/#635 로 실리고 패치본에선 안 실려 «legacy 잔존» 절이 달라진다 → 31 중 1 불일치(H 단독 재현 · E 단독 31/31). 처방 후보: ⓐ `_pre_repair_gate` 를 «현행 scripts 트리 사본 + `34c74a6` 의 `registry_gate.py`(·`anchor_diff.py`) 만 덮어쓰기» 로 바꿔 P0′ 가 **게이트** 불변만 재게 한다(스모크 취지 = provenance 채널 도입 전후 게이트 동일성) ⓑ `_PRE_REPAIR_COMMIT` 을 H 커밋 뒤 tip 으로 올리고 docstring 에 사유 기록(취지 약화 — 비권장). 어느 쪽이든 §2 2단계에 넣고 ⑤ 에서 31/31 재확인.
- cross matrix: skeleton 레인 2행 «기대 red 소멸» → `--emit-expected` 로 두 행 제거 · 사유 «결정 2 — skeleton/good_bc 의 0B 재등장 칸은 내용 규칙 대상 아님».

### 2.5 G — S3 문면

병기 초안(패치본): «… 산문에만 적힌 경계 import(블록 미기재)는 전사되지 않아 표면 밖이다 · 전사는 add 소비자 스텁만이다(브라운필드 `update` 잎의 import 는 실존 판정만 받고 전사 밖).» — 러너 유닛(S1~S9 접두)·check-report 14단계·enforce 7 전부 PASS. 봉인 재발행 범위는 §1 표.

### 2.6 Makefile `verify` 대조표(패치본 실측)

| 타깃 | 도구 | 영향 | §2 에 있나 |
|---|---|---|---|
| verify-ontology | gate·meta-SHACL·SHACL·hierarchy(target-counts)·golden·issued·ledger·render_sync·structural·query_golden | 1단계 전부 | ✓ |
| base-core | corpus_mirror_sync·corpus_lint | 1단계 | ✓ |
| base-core | **spec_lint** | 규칙 행 + 집계표 3표 + predicates + map | △(2문서로 축소 기재) |
| base-core | checker_lint·tree_mirror_check·reverse_coverage | green 실측 | — |
| base-core | fixture_matrix | 삼중 등재 2 | ✓ |
| base-core | **checker_baseline_matrix** | public-surface 행 | ✗(«무변» 오기) |
| base-core | findings_count_matrix | public-surface 행 | ✓ |
| base-core | findings_smoke·construct_drift·anchor_diff_smoke·session_bounce·derive_path_globs·ab_score | green 실측 | — |
| base-core | ontology_rulepack --check | `make rulepack` | ✓ |
| base-core | manifest_seal --check --draft·--self-test | 1·2·3 뒤 `--write` 1회 | ✓(순서 명시 권고) |
| base-core | `diff -rq` scripts 미러 | check-*.py 3 + design_pregate + **pregate_symbol_kinds.json** | △(JSON 미러 누락) |
| base-cross | **checker_cross_matrix** | skeleton 2행 소멸(+good 배치) | ✗(«무변» 오기) |
| base-cross | **registry_gate_smoke** | P0′ | ✗ |
| base-cross | bc_registry_smoke | green | — |
| base-backstop | api_error_backstop_matrix | green(714) | — |
| base-regen | regen_loop·runtime_parity·rulepack_smoke | green(클론 14/14) | — |
| base-regen | **gen_pregate_symbol_kinds --check** | source_sha 드리프트 | ✗ |
| base-regen | pregate_fixture_run | PASS | ✓(4단계 실측에 포함) |

## 3. 수정안 목록(계획 §1 문장 단위)

1. E 검사기 «새 헬퍼 `_explicit_any(ann, bindings)` … Name 이 모듈 바인딩으로 `typing.Any`/`typing_extensions.Any` 로 해소» → **«`_module_bindings` 는 출처 모듈을 버리므로 재사용하지 않고, 같은 걷기 규칙의 `_any_bindings(mod) -> (Any 로 바인딩된 이름 집합, typing 계열 모듈 별칭 집합)` 를 신설한다(모듈 수준 동명 재정의는 그림자). `_explicit_any(ann, names, mods)` 는 문자열 재파싱 → 루트 Any = bare → `X | None`/`Optional`/`Union` 평탄화 뒤 None 제외 전 구성원 Any = bare → 하위 Any = nested»**. 권고 병기: `Annotated[Any, …]`·구성원 하나라도 Any 인 합집합은 bare · 그림자되지 않은 미해소 `Any` 이름도 Any(fail-closed) · `TypeAlias` 재별칭·함수 본문 import 는 검출 한계로 docstring 에 적는다.
2. E 검사기 «자리 ①(`_check_signature` 211~226) … 자리 ②·③» → **«별도 패스 `_check_explicit_any(mod, rel, findings, candidates)` 를 `main` 의 `_scan_stmts(...)` 다음 줄에 호출한다(#493 코드 무접촉 · 부모 맵으로 `self`/`cls` 수신자만 건너뜀 · lineno 정렬 방출)»**. 기존 3 함수에 `Candidates` 를 꿰는 안은 시그니처 3곳 변경이라 비권장.
3. E 검사기 «`self`/`cls`·dunder 는 기존 면제 그대로» → **«수신자 `self`/`cls` 만 건너뛴다 — 함수 이름 dunder 는 면제가 아니다(`__init__(*args: Any, **kwargs: Any)` 가 spring 8 중 6)»**.
4. E 소급 기대치 «격리 실행에서 application/* #645 위반 = spring 8 · kkebi 10» → **«application/* `[#645]` = spring 10 · kkebi 14 = 프로덕션 8/10(① C 목록 전건) + `test/factories` 2/4(MATERIAL_DIRS) · ⓓ#645 프로덕션 112/123(시그니처 nested 42/26 · 변수 bare 37/61 · 변수 nested 33/36) · #493 기준선 3,225/173 불변»**.
5. E 픽스처 «good 에 `boundary_narrowing.py` 1파일» → **«`driven_layer/django_orders/admin/order/form/order_form.py` + 0B `admin/order/panel.py`(트리 84행 — cross census 무변 조건)»**. bad «6형 + 변수 1» → **«8형(+`Any | None`·문자열 `"Any"`) + 변수 1 → #645×8·ⓓ#645×1»**(6형 유지 시 기대치는 실측 그대로 6/1).
6. E 매트릭스 «`findings_count_matrix.py --emit-expected`(public-surface 행: «#493×8 → +#645×6»)» → **«count 행 분포는 `#645×7`(위반 6 + info 1)·info 2→3 로 적힌다»** ; «`checker_baseline_matrix`·guard-zero 무변» → **«`checker_baseline_matrix --emit-expected`: public-surface `(2,12,12,4,False)` → `(2,18,18,5,False)` · guard-zero 무변»**. 두 갱신 모두 커밋 메시지에 검사기별 사유 1행(2.3 예문).
7. E «규칙 번호 등재: `tree-revision-spec.md`(#645 1행) · `rule-owner-map.md`(1행)» → **«3문서 6곳: spec 7컬럼 규칙 행(셀 안 `|` 금지 — `Optional[Any]`·None 합집합 등으로 표기 · 등급 `ast+` · 근거 D58+§4 · **blocker**) + spec 집계표 3표(등급표 `ast+` 56→57 · 판정×어겼을때 `ast+` 55→56/계 546→547 · 읽는 법 «`ast+` 의 blocker» 55→56) + `2026-08-11-predicates.md` 술어 행(확정·후보·물음 낱말 필수) + owner-map `| 645 | ast+ | scripts/check-public-surface-annotation.py | agents/discipline-reviewer.md | 신설 | … |`»** — 이 조합으로 spec_lint 0건 실측.
8. H 검사기 «import: `from checker_target import skeleton_placeholder`» → **«두 파일이 이미 `import checker_target` 이므로 `checker_target.skeleton_placeholder(py|entry)` 속성 호출(port-adapter :641 판형)»**.
9. H 무손실 «cross matrix 무변» → **«`checker_cross_matrix --emit-expected` 로 `('skeleton','check-port-adapter-pairing.py')`·`('skeleton','check-usecase-dto-placement.py')` 2행 제거(사유: 결정 2 — good_bc 의 0B 재등장 칸) · 그 밖 무변»**. 추가 문장: **«`registry_gate_smoke` P0′ 는 `34c74a6` scripts 트리째 대조라 good_bc legacy #219/#635 소실로 red — `_pre_repair_gate` 를 현행 트리 + 옛 `registry_gate.py` 덮어쓰기로 바꿔(게이트 불변만 측정) 31/31 복원»**.
10. G S3 «(브라운필드 `update` 잎의 import 는 전사 밖)» → **«(브라운필드 `update` 잎의 import 는 실존 판정(⑴~⑶)만 받고 스텁 전사 밖)»**.
11. §2 2단계에 **추가**: «`gen_pregate_symbol_kinds.py` 재소성(source_sha) + codex `pregate_symbol_kinds.json` byte 미러 · `checker_baseline_matrix --emit-expected` · `checker_cross_matrix --emit-expected` · `registry_gate_smoke` P0′ 수리 · 규칙 등재 3문서(7항)». §2 3단계 «`manifest_seal.py --write`(draft)» → «1·2·3 의 모든 파일 변경 뒤 마지막에 1회».
12. §2 4단계 검증식을 4·9항의 수치로 교체(«8/10» → «10/14 (프로덕션 8/10)» · cross 2행 · 스모크 31/31 · symbol_kinds `--check` green).

## 4. 미확인

- `#645 ↔ R-3447` 조인: `ontology/wiring/aliases.ttl`(28 항목)에 #644 도 없어 신규 번호는 alias 불요로 보이나, `enforcedBy` 배선과 rulepack(C암 팩·`rulepack_smoke` G 단언)이 #645 를 어떻게 싣는지는 B 축(그래프) 판정 — 여기서는 `make rulepack` 재생성 필요만 확인.
- `manifest_seal` 외부 부속서 `memory_state(project_keys)` 에 dddjango 프로젝트 메모리가 포함되는지(§2 5단계 메모리 갱신이 `--check --draft` 를 흔드는지) — 부속서 키 목록 미열람.
- E good 파일의 Form 오버라이드가 django-stubs strict 에서 `object` 로 통과함은 ① A 프로브 재료(spring `.venv`) 기준 — 픽스처 자체는 실행하지 않는다.
- `Union[Any, X]`·`Annotated[Any, …]` 를 bare 로 올릴 때의 양 저장소 소급 증가분(현재 nested 로 세어 42/26 안에 포함) — 채택 시 재집계 필요.
- `registry_gate_smoke` P0′ 처방 ⓐ(옛 게이트 + 현행 검사기)가 옛 `registry_gate.py` 의 import 계약(`findings.py`·`anchor_diff.py` 시그니처)과 맞는지는 실제 덮어쓰기로 재확인 필요(여기서는 원인 분리까지만 실측).
- `check-report` filtered 처분이 S3 를 «번호로» 인용하는 실전 리포트(카탈로그·리딩)의 재판정 — 문면 변경은 번호 불변이라 무영향으로 추정, 실전 리포트 재실행은 안 했다.
