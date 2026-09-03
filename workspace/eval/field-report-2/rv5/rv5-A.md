# ⑤ 구현 리뷰 — 리뷰어 A(기술 축 — 검사기·픽스처·매트릭스·실행기·미러) · 현장 보고 수리 2 (2026-09-04)

독립 리뷰. 대상 = `fix/field-report-2` 의 35fc29b(규범)·95a95cc(검사기)·421782e(문서) 중 기술 축 파일 전부와 계획 v2 Δ5~Δ7·Δ9·Δ10·Δ12·Δ14 · ④ 기록 수치. 저장소는 읽기·조회만 했다. 실행은 전부 `scratchpad/fr2/rv5A/` 아래에서 — `repo/`(rsync 사본 · 픽스처·프로브·격리 소급) · `repo_nopanel/`(0B `panel.py` 제거 대조본) · `clone/`(git clone · make 타깃·스모크) · `old_scripts/`(35fc29b 의 `dddjango/scripts` — 옛 검사기) · `alt_scripts/`(Δ5 문면 그대로 구현한 대안 검사기 — 소급 증분 측정용) · `probes/`(48 형상) · `iso/`(격리 사본 `fr2/DE/iso/{spring,kkebi}` 실행 산출 — sink 는 `DJR_FINDINGS_JSON` 으로 우회 · 사이드카 85/494 전후 불변) · `H/`(`fr2/H/spring` 3커밋 detach 재실행 · 종료 후 9c8814e detach 복원) · `pregate_demo/`(rv3A 의 `empty` 스텁 mini_repo 사본).

## 1. 판정 표

| 항목 | 판정 | 핵심 근거 |
|---|---|---|
| #645 구현 ↔ Δ5 — 구조(`_any_bindings`·`_unstring`·`_union_members`·별도 패스·`main` 호출 자리·수신자 self/cls 만·dunder 면제 없음·lineno 정렬·docstring 등재) | **검증됨** | 48 프로브(§2.2) — if/try 걷기·그림자 3형·`t.Any`/`typing_extensions`·TYPE_CHECKING 양 분기·문자열 4형·`**kwargs: "Any"`·중첩 함수·프로퍼티·`@overload`·posonly/kwonly/async·`__init__(*args: Any, **kwargs: Any)` 전부 기대대로. `_check_explicit_any` 는 `main` 의 `_scan_stmts` 다음 줄(:644) · #493 코드 무접촉 · p22 에서 `[#493]`×2 + `[#645]`×1 같은 줄(독립 실증) |
| #645 구현 ↔ Δ5 — **판정 의미론 3절** | **MAJOR** | Δ5 문면 ⑴ «None 제외 구성원에 Any **있으면** bare» → 코드 `:446` 은 `all(...)`(전 구성원) — `Any \| str`·`Union[Any, int]` 가 ⓓ(p10b·p10c) ⑵ «`Annotated[Any, …]` bare» → nested ⓓ(p07 · docstring `:437` 이 Annotated 를 nested 로 명기) ⑶ «미해소 `Any` 이름도 Any(fail-closed)» → `_is_any` 가 `names` 소속만 인정 + `:462` 조기 return — import 없는 `x: Any`(p13)·`from typing import *`(p01)·클래스 본문 import(p05)·`with` 블록 import(p33) 전부 **무시**(fail-open). 코드·docstring·`predicates.md:244`(«None 을 뺀 구성원이 **전부** Any») 3자는 서로 일치하나 Δ5 와 다르고 ④ 기록은 편차를 고지하지 않는다. **소급 영향 0**: Δ5 문면대로 만든 `alt_scripts` 로 양 저장소 재실행 → `[#645]` 78/121·application 10/14·ⓓ 694/385 **전건 동일**(증분 0) — 어느 쪽으로 정리해도 매트릭스·Δ7 수치 재기준선 불요 |
| #645 사각·오탐(MINOR 묶음) | **MINOR ×4** | ⓐ `@staticmethod def f(self: Any, y: Any)` → `self` 건너뜀(p18 · `:475` 가 데코레이터를 안 봄 — #493 `:218` 과 같은 휴리스틱이라 짝 유지) ⓑ `Literal["Any"]` → ⓓ nested 오탐(p27 · `:451` 문자열 재파싱이 Literal 안까지 본다) ⓒ Δ5 «검출 한계(`TypeAlias` 재별칭·함수 본문 import·`cast`)는 docstring 에» — 함수·클래스 본문 import 만 적혀 있고(`:352`) `TypeAlias`(p28)·`cast`(p32)·`with` 블록(p33) 미기재 ⓓ `Annotated[int, "Any"]`(p27b) 는 HEAD 무발화·alt ⓓ — 메타데이터 문자열 사각(무해) |
| 픽스처 — good/bad | **검증됨(+MINOR 기록 오기)** | good exit 0 · 검사기 «파일 **18개**»(35fc29b 트리 16 + `order_form.py` + 0B `panel.py`) — ④ 기록 «17파일» 은 오기. bad exit 2 · `[#645]`×8(:8·12·16·20·24·28·32·36 — 8형 전건 bare) · `[ⓓ#645]`×1(:41 `y` nested) · #493×8·#358×2·#456×2·ⓓ#69×2 불변. skeleton_placeholder 서브 2 → exit 0/0 |
| 0B `panel.py` 필요성 | **검증됨** | `repo_nopanel` 에서 `checker_cross_matrix` → «public_surface × check-layer-skeleton exit 2→2 vio ((488,26))→((488,27)) · 차이 1건 · exit 2» · count/baseline 은 무변(73/73) — panel.py 는 cross census 무변 조건으로 실제 필요(트리 84행) |
| 매트릭스 EXPECTED | **검증됨** | 클론 `make verify-base-core`(venv 단계는 원본 `.venv` 파이썬으로 수동 완주): fixture 104/104 · baseline 73/73(public-surface `(2,20,20,5)`) · count 73/73(`#645×9`·info 3 · 해시 3 일치) · spec_lint 규칙 547·위반 0 · `verify-base-cross`: cross 348/348 차이 0 · registry_gate_smoke 31/31 · bc_registry ✓ · `verify-base-regen` PASS · backstop 714 |
| cross 2행 제거 사유 | **검증됨** | `skeleton/good_bc` 의 0B 재등장 칸 = `application_layer/order/place_order/place_order_use_case.py`(트리 41행) · `application_layer/port/email_sender/email_sender_port.py`(47행) — 결정 2(내용 없는 골격 파일은 내용 규칙 대상 아님)에 정확히 해당 · 두 행 모두 «기대 red 소멸» 이므로 EXPECTED 에서 빠지는 것이 판형(green 레인은 미등재)에 맞다 |
| H 가드 — 침묵/유지 규칙 집합 | **검증됨** | `_check_port_contract`(:243-281) 안 = #219(:249)·#551(:252)·#220(:256)·#241(:261)·**#212(:269 — «구현이 있다 — port 에는 선언만» · 이 함수 소속 확인)**·#485(위반 :273 · 후보 :277) — 전부 내용 규칙. 존재·짝 규칙은 다른 함수: #218(:213)·#225·#216·#214·#64 = `_check_capability_folder` · #576 = `_check_fake`(:1048) · usecase #193(:343)은 가드(:376) 앞 · `_check_entry`(:383-) = #635·#211·ⓓ#194 만 · `main:681` `_check_event_steps(entry)` 는 빈 파일 무발화 |
| H — `skeleton_placeholder` 정의 ↔ 결정 2 | **검증됨** | 0바이트·공백-only·주석-only·docstring-only → 건너뜀 / `pass` 만·`"""doc"""` + `pass` → #219/#635 발화(passprobe 실측). 사용자 문면은 «빈 파일 무검사» 이고 결정 2 규범화 문구는 «내용 없는 골격 파일(0바이트·docstring/주석뿐)» — `pass` 는 문장(내용)이라 빈 파일이 아니다. fail-closed 가 취지에 맞다(빈 파일 실현 정본형은 #488 «빈 파일» 이고 `pass` 는 정본형 밖) |
| H 카탈로그 3커밋 | **검증됨** | ONLY 2검사기 · HEAD scripts: `59d08c7` #219 0·#635 0(옛 2/3 · **5→0**) 두 검사기 exit 0 · `99253ce` #218 2·#193 3·#576 2(옛과 동일 · **7 불변**) exit 2 · `9c8814e` 0(옛 2/3) exit 0 — ④ 기록과 동일 |
| H HEAD 무손실 | **검증됨** | 격리 사본 옛/새 두 검사기: spring port 0/0·usecase 0/0 · kkebi port 0/0·usecase **43/43 차분 0** · placeholder 형 `_port/_use_case` 양쪽 0 · pre-gate `empty` 6행 데모 귀속 옛 4(#488×2·#219·#635) → HEAD **2**(#488×2) — Δ9 «4→2» 재현 |
| registry_gate_smoke P0′ | **검증됨(+MINOR 1)** | 옛 게이트(34c74a6)가 쓰는 계약 = `anchor_diff.{load_debt·AnchorDiffUsage·is_git_worktree·run_git·snapshot_anchor·debt_match}` · `findings.{ENV_VAR·ENV_DIR·ENV_GIT_ROOT·ENV_EXPERIMENT·line_of_record}` · `checker_target.bc_shaped_target_reason` · `checker_registry.{REGISTRY·checker_argv}` — 현행 모듈에 전부 실존 → 클론 31/31. «게이트 불변만 측정» 은 docstring(:236-240)에 명시 · 검사기 회귀는 baseline/count/cross 가 덮으므로 취지 손실 없음. `shutil.copytree`(:242)는 `__pycache__` 37 pyc 를 mtime·size 보존 복사 → 타임스탬프 검증으로 동일 소스에만 유효하고 덮어쓴 `registry_gate.py` 는 `__main__` 으로 실행돼 pyc 를 안 쓴다 — 스테일 혼입 경로 없음(위생상 `ignore` 권고) |
| 실행기 S3 문면·미러·봉인 | **검증됨(+문면 드리프트 메모)** | `pregate_fixture_run.py:841` 은 `len==9`·`S{i} ` 접두만 단언 · `--check-report` 정규식(:1690-1695)은 절 헤더·해시·id·«예보 N건»·«결손 N건» 만 · 픽스처 골든에 S3 본문 0건 → regen PASS. `diff -rq` scripts 미러 0 · `pregate_symbol_kinds.json --check` in-sync(종류 56·27종·양 미러) · `manifest_seal --check --draft` green(258 파일·draft) · `--self-test` 9/0. Δ12 문면 «실존 판정(⑴~⑶)만 받고 **스텁** 전사 밖» 이 구현에선 «실존 판정만 받고 전사 밖» — ⑴~⑶ 은 BLIND_SPOTS 문맥에 지시 대상이 없어 빼는 편이 낫다(무해) |
| 소급 실측 재현 | **검증됨** | 격리 사본·HEAD 검사기: `[#645]` spring **78**(application **10** — fortune_record 2·promotion 2·service_policy 4·factories 2)·kkebi **121**(application **14** — identity 2·product_observability 2·saju 3·share 2·tarot 1·billing factories 4) · ⓓ#645 application 114/134 · #493 3,225/173 불변 · #645 외 규칙 옛/새 차분 **0**(A∖B = 0) |

## 2. 상세

### 2.1 실측 명령(재현용 · 전부 `scratchpad/fr2/rv5A/`)

- 픽스처: `python3 repo/dddjango/scripts/check-public-surface-annotation.py repo/workspace/eval/fixtures/public_surface/{good,bad_rules}` · `check-port-adapter-pairing.py …/port_adapter_pairing/skeleton_placeholder` · `check-usecase-dto-placement.py …/usecase_dto/skeleton_placeholder`.
- 프로브: `python3 gen_probes.py probes` → `check-public-surface-annotation.py probes` → `probes.out` · 대안: `alt_scripts/check-public-surface-annotation.py probes` → `probes_alt.out`(패치 = `all→any` · Annotated 루트 bare · 비-import 재정의로 그림자되지 않은 `Any` 이름 fail-closed · `:462` 조기 return 제거).
- 매트릭스·make: `clone/` 에서 `make verify-base-{core,cross,regen,backstop}`(core 는 `.venv` 부재로 `derive_path_globs --check` 에서 중단 → `derive_path_globs --check`·`ontology_rulepack --check` 는 원본 `.venv/bin/python` 으로, `manifest_seal --check --draft`·`--self-test`·`ab_score --self-test`·`diff -rq`·`gen_pregate_symbol_kinds --check` 는 python3 로 수동 완주 — 전부 exit 0). `repo`·`repo_nopanel` 에서 `checker_cross_matrix.py`·`findings_count_matrix.py`·`checker_baseline_matrix.py`.
- 격리 소급: `DJR_FINDINGS_JSON=iso/sink.jsonl` + `DJR_VIOLATIONS_DIR` 해제 · {repo, alt_scripts, old_scripts} × {public-surface} 와 {repo, old_scripts} × {port-adapter, usecase-dto} × {spring, kkebi} → `iso/<repo>.<변종>.out`.
- 카탈로그: `ONLY=check-usecase-dto-placement.py,check-port-adapter-pairing.py python3 fr2/H/run_rules.py <c>-rv5A-{new,old} {repo,old_scripts}/dddjango/scripts fr2/H/spring H` × {59d08c7, 99253ce, 9c8814e} → 9c8814e detach 복원.
- pre-gate 데모: `design_pregate.py empty-slots-spec.md pregate_demo/repo --base HEAD`(HEAD 실행기·검사기) / `old_scripts/…/design_pregate.py … repo2`(옛 트리).

### 2.2 #645 프로브 판정표(HEAD 검사기 · alt 열은 Δ5 문면 그대로 구현했을 때)

| # | 형상 | HEAD | alt(Δ5) | Δ5 문면 기대 | 비고 |
|---|---|---|---|---|---|
| p01 | `from typing import *` · `x: Any` | 무시 | bare | bare(fail-closed) | **편차 ⑶** |
| p02 | `import typing as t` · `t.Any` 인자·반환 | bare ×2 | 동일 | bare | |
| p03 | `typing_extensions as te` `te.Any` · `from typing_extensions import Any` | bare ×2 | 동일 | bare | |
| p04/b/c | `Any = object` · `class Any` · `Any: type = object` 재정의 | 무시 ×3 | 동일 | 그림자 | |
| p05 | 클래스 본문 안 `from typing import Any` | 무시 | bare | (검출 한계 문서화) | docstring `:352` 에 기재됨 |
| p06/b | `if TYPE_CHECKING:` import · `else:` 분기 import | bare ×2 | 동일 | bare | |
| p07 | `Annotated[Any, 'doc']` | **nested ⓓ** | bare | **bare** | **편차 ⑵** |
| p08 | `type[Any]` | nested ⓓ | 동일 | nested | |
| p09 | `Callable[[Any], int]` · `-> Callable[..., Any]` | nested ×2 | 동일 | nested | |
| p10 | `Union[Any, None]` | bare | 동일 | bare | |
| p10b | `Union[Any, int]` | **nested ⓓ** | bare | **bare** | **편차 ⑴** |
| p10c | `Any \| str` | **nested ⓓ** | bare | **bare** | **편차 ⑴** |
| p10d | `None \| Any` | bare | 동일 | bare | |
| p10e | `Optional[Union[Any, None]]` · `-> Union[Any]` | bare ×2 | 동일 | bare | 재귀 평탄화 ✓ |
| p11 | `'Optional[Any]'` · `-> 'Any'` | bare ×2 | 동일 | bare | |
| p11b | `Optional['Any']` · `dict[str, 'Any']` · `-> 'dict[str, Any]'` | bare · nested · nested | 동일 | 동일 | 내부 문자열 ✓ |
| p11c | `'Any \| None'` | bare | 동일 | bare | |
| p12 | `**kwargs: 'Any'` | bare | 동일 | bare | |
| p13 | import 없이 `x: Any -> Any` | 무시 | bare ×2 | bare(fail-closed) | **편차 ⑶** |
| p14 | 람다 | 무발화 | 동일 | N/A | 애너테이션 문법 없음 |
| p15 | 중첩 함수 `inner(self: Any, x: Any) -> Any` | bare ×3 | 동일 | bare(수신자 아님) | 부모가 ClassDef 아니면 첫 인자도 검사 ✓ |
| p16 | `@property … -> Any` | bare | 동일 | bare | |
| p17 | `@overload` 2벌 중 `Any` 벌 | bare ×2 | 동일 | bare | |
| p18 | `@staticmethod def f(self: Any, y: Any)` | `y` 만 bare | 동일 | (수신자만 제외) | MINOR ⓐ — `self` 건너뜀 |
| p18b | 모듈 함수 `f(cls: Any)`·`g(self: Any)` | bare ×2 | 동일 | bare | |
| p18c | 메서드 `m(cls: Any, x: Any)`(classmethod 아님) | `x` 만 | 동일 | 휴리스틱 허용 | #493 `:218` 과 동일 |
| p19 | 함수 안 중첩 클래스 메서드 `m(self, x: Any)` | bare | 동일 | bare | |
| p20 | 기본값 `= Any` | 무시 | 동일 | 무시 | |
| p21 | 모듈 `X: Any` · 클래스 `y: Any` · `self.z: Any` · 지역 `w: dict[str, Any]` | ⓓ ×4(bare·bare·bare·nested) | 동일 | ⓓ | |
| p22 | `def f(a, b: Any):` | #493×2 + #645×1 | 동일 | 독립 | |
| p23 | `try: from typing import Any except: from typing_extensions import Any` | bare | 동일 | bare | |
| p24 | `import typing` · `typing.Any` · `-> typing.Optional[typing.Any]` | bare ×2 | 동일 | bare | `_name_of` Attribute ✓ |
| p25 | `def Any()` 재정의 | 무시 | 동일 | 그림자 | |
| p26 | `Any = object` 뒤 import | bare | 동일 | bare | 순서 ✓ |
| p27 | `Literal['Any']` | **nested ⓓ(오탐)** | 동일 | 무시 | MINOR ⓑ |
| p27b | `Annotated[int, 'Any']`(Any 미import) | 무발화 | ⓓ | — | 조기 return 효과 |
| p28 | `Loose: TypeAlias = Any` · `x: Loose` | 무시 | 동일 | 한계 문서화 | docstring 미기재(MINOR ⓒ) |
| p29 | `__init__(self, *args: Any, **kwargs: Any)` | bare ×2 | 동일 | bare(dunder 면제 없음) | |
| p30 | `async def f(x: Any, /, y: int, *, z: Any) -> Any` | bare ×3 | 동일 | bare | |
| p31 | `dict[str, Any] \| None` | nested | 동일 | nested | |
| p32 | `cast(Any, x)` | 무시 | 동일 | 무시(한계) | docstring 미기재(MINOR ⓒ) |
| p33 | `with suppress(ImportError): from typing import Any` | 무시 | bare | (fail-closed 면 bare) | `_module_bindings` 와 같은 걷기(if/try 만) |
| p34 | `from typing import Any as Any` | bare | 동일 | bare | |
| p35 | 클래스 본문 `Any = 1` 뒤 메서드 `x: Any` | bare | 동일 | (모듈 수준만 그림자) | |
| p36 | `x: 'Any['`(파싱 불능 문자열) | 무시 | 동일 | 무시 | |

격리 소급(HEAD vs alt): spring `[#645]` 78→78 · application 10→10 · ⓓ 694→694 / kkebi 121→121 · 14→14 · 385→385 — **증분 0**(양 저장소에 p01·p05·p07·p10b·p10c·p13·p33 형상이 시그니처에 없다).

### 2.3 H — 함수 경계·정의·카탈로그

- `_check_port_contract` 첫 줄 가드(:245)가 침묵시키는 집합 = {#219, #551, #220, #241, #212, #485(위반+후보)}. #212 는 이 함수의 메서드 루프(:269) 소속 — Δ9 열거와 일치. 유지 = #218·#225·#216·#214·#64(`_check_capability_folder`)·#576(`_check_fake`)·#193(`_check_use_case` :343)·#488(skeleton 검사기 무접촉).
- `skeleton_placeholder`(checker_target :32-50) = «docstring 밖 문장 0개 · 읽기/파싱 불능은 False». 실측: `pass` → #219 · `# placeholder` → 침묵 · 공백만 → 침묵 · `"""doc"""` + `pass` → #219 · usecase `pass` → #635.
- 카탈로그·HEAD·pre-gate 수치는 §1 표.

### 2.4 매트릭스·스모크·봉인 실측값

- `fixture_matrix` 케이스 104·일치 104 · `checker_baseline_matrix` 73/73(public-surface `| 2 | 20 | 20 | 5 |`) · `findings_count_matrix` 73/73(`exit 2 · violation 20 · info 3 · 12b30d52c8b79fbf · 1287a398542206ab · b3a43dfbe6863ef4`) · `checker_cross_matrix` census 348 = EXPECTED 348 · 차이 0 · `registry_gate_smoke` 31/31 · `bc_registry_smoke` A/B/C ✓ · `spec_lint` 규칙 547·ast+ 57·위반 0 · `derive_path_globs --check` 정합 · `ontology_rulepack --check` 정합(양 런타임 미러 동일) · `manifest_seal --check --draft` green(그룹 10·파일 258·18런·draft) · `pregate_fixture_run` PASS · `api_error_backstop_matrix` 714/0.
- 95a95cc 의 `workspace/eval/ab/T2-0b-manifest.json` +67/−55 = 봉인 draft 재발행(검사기 2·final.md 5·codex 미러 추가) — 계획 Δ14 «마지막 1회» 에 부합.

## 3. 수정안(파일·줄)

1. **[MAJOR] Δ5 ↔ 코드 의미론 3절 정리 — 두 길 중 하나를 코디가 확정(소급 증분 0 이라 어느 쪽도 매트릭스·Δ7 재기준선 불요)**
   - ⓐ 코드를 Δ5 에 맞춘다(권장 — 「`Any` 가 든 합집합은 무엇이든 받는다」·`Annotated` 는 투명·미해소 `Any` 는 star-import/`with`/클래스 본문 import 사각을 닫는다): `dddjango/scripts/check-public-surface-annotation.py` `:446` `all(` → `any(` · `:440` 다음에 `Annotated` 루트(첫 원소 `_unstring` 후 `_is_any`) → `"bare"` · `_any_bindings` 에 비-import 재정의 집합(`:375`·Assign·AnnAssign 분기)을 따로 모아 `:392` 앞에 «`"Any"` 가 names 에도 그 집합에도 없으면 `names.add("Any")`» · `:462-463` 조기 return 삭제 · docstring `:436-437` «전 구성원이 Any» → «구성원 하나라도 Any» · «Annotated» 를 nested 목록에서 bare 로 이동 · `workspace/design/2026-08-11-predicates.md:244` «None 을 뺀 구성원이 전부 `Any`» → «하나라도 `Any`» + «`Annotated[Any, …]`·모듈에서 재정의되지 않은 미해소 `Any` 이름 포함» · `2026-08-08-tree-revision-spec.md:1174` 괄호 보강(선택) · codex byte 미러 · `gen_pregate_symbol_kinds.py` 재소성 + JSON 미러 · `manifest_seal --write`(draft) · bad 픽스처에 `Any | str` 1형 추가 시 count/baseline `--emit-expected`(선택 — 추가하지 않으면 매트릭스 무변). 프로브 `probes_alt.out` 이 기대 출력.
   - ⓑ 계획을 코드에 맞춘다: 계획 v2 Δ5 에 정정 추기(«전 구성원 Any 만 bare · Annotated 는 nested · 미해소 이름은 무시(검출 한계)» + 사유) · ④ 기록에 편차 고지 · docstring 에 한계 3항(아래 6) 추가.
2. **[MINOR] ④ 기록 오기**: `2026-09-04-field-report-repair-2-rubric.md:134` «good exit 0(17파일)» → «18파일»(35fc29b 트리 16 + 2).
3. **[MINOR] staticmethod 수신자**: `:475` 조건에 `and not any(_name_of(d) == "staticmethod" for d in node.decorator_list)` — #493 `:218` 도 같은 휴리스틱이므로 **둘 다 고치거나 둘 다 두거나**(짝 유지 · 단독 수정 금지).
4. **[MINOR] `Literal[...]` 오탐**: `_explicit_any` 의 `ast.walk` 문자열 재파싱(`:451`)에서 부모가 `Literal` Subscript 인 Constant 는 건너뛴다(부모 맵은 `_check_explicit_any` 가 이미 만든다 — 인자로 넘기거나 `Literal` 서브트리를 사전에 제외).
5. **[MINOR] 스모크 위생**: `workspace/tools/registry_gate_smoke.py:242` `shutil.copytree(GATE.parent, …, ignore=shutil.ignore_patterns("__pycache__"))`.
6. **[MINOR] 검출 한계 docstring**: `check-public-surface-annotation.py` #645 헤더(`:21-23`) 또는 `_any_bindings` docstring(`:349-352`)에 «`TypeAlias`/`type X = Any` 재별칭·`cast(Any, …)`·`with`/`for` 블록 안 import 는 보지 않는다» 1행(Δ5 요구).
7. **[메모 · 조치 불요] Δ12 문면 드리프트**: `design_pregate.py:1528-1529` 가 «실존 판정(⑴~⑶)만 … 스텁 전사 밖» 대신 «실존 판정만 … 전사 밖» — BLIND_SPOTS 문맥에 ⑴~⑶ 지시 대상이 없어 현행이 낫다. 계획 Δ12 에 «(⑴~⑶) 생략» 만 추기.

## 4. 미확인

- ⓐ 채택 시 프로덕션 코드 밖(framework·scripts·fabfile) 의 증분도 0 인 것은 격리 사본 전체 실행으로 확인했으나, 두 저장소 밖의 다른 발주처 코드에서 `Any | X` 시그니처가 얼마나 흔한지는 표본이 없다.
- `manifest_seal` 부속서가 dddjango 프로젝트 메모리(`~/.claude/projects/…/memory`)를 품는지 — 클론에서 green 이었으므로 이번 리뷰 범위에선 흔들리지 않았다(부속서 키 목록 미열람 — rv3-A 와 같은 미확인).
- E good 픽스처의 Form 오버라이드(`*args: object, **kwargs: object`)가 django-stubs strict 에서 통과함은 ① A 프로브 재료 기준 — 여기서 재실행하지 않았다.
- `verify-ontology`(그래프 게이트 10단)는 B 축 소관이라 돌리지 않았다(클론 `.venv` 부재).
- ④ 기록 «kkebi 43/43» 의 43 은 usecase-dto 검사기 몫 — 재현했으나 43 의 내역(어느 규칙)은 이 리뷰의 판정에 불필요해 분해하지 않았다.

Serena: skipped — `.serena/project.yml` 부재(기본 도구·프로브·격리 실행으로 충분).
