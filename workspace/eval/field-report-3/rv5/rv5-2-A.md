# rv5-2-A — ⑤-2 구현 리뷰 · 조각 2(`d701df8` S-5 + ⓔ1 + ⑤-1 정정) + 정정 커밋 `cad221b` · 리뷰어 A(기술 축 — 검사기·게이트·픽스처·매트릭스 정독 + 재실행) · 2026-09-04

- 대상: `d701df8` 의 `dddjango/scripts/{check-api-error-controller-contract,check-openapi-error-declaration,check-public-surface-annotation,registry_gate}.py` · `workspace/tools/{registry_gate_smoke,gen_pregate_symbol_kinds,construct_drift_report,findings_count_matrix,checker_baseline_matrix,checker_cross_matrix}.py` · `workspace/eval/fixtures/api_error_controller/**` · 등재 3문서 · 구현 기록 `evidence/impl/piece2-summary.md` + 동봉 로그 · `cad221b`(봉인 재발행·기록 정정). 대조 = 계획 v2 §2.2·§2.3·§2.4·Δ8·Δ10·Δ11 · rv5-A §3(N-1~N-9) · rv5-C M1·M4.
- 재실행 산출: `$S/rv5A2/`(`$S=/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3`) — `old/`(= `git archive main dddjango/scripts`) · `p1/`(= `git archive 56b27e1`) · `proto/`(정정 시제품 · `proto.diff` 15줄) · `synth_api/`(#648/#649 합성 · 컨트롤러 17형 + 스키마 8형 + OHS + 도메인) · `synth_ps/`(public-surface N-1~N-5 합성 8파일) · `field/`(4사본 sink·stdout) · `drift/`·`fxmain/`·`replay*/`·`gate-kkebi.log`. 실서고 무접촉 · 사본 4 tracked 무변(`$S/spring` 의 untracked `mp_probe_rv5b/` 는 ⑤-1 리뷰어 B 의 잔류물 — 계수에서 `mp_probe_` 접두 제외) · 사본 안에 만든 파일은 `kkebi/rv5a2_probe.md`(게이트 무해 변경) 하나 — 실행 뒤 제거·`git status` 확인. mypy 는 spring venv(cwd=픽스처 good 루트 · ΔC-8 레시피 · ninja 1.6.3 `Status(Generic[T])` 확인). **`make verify` 는 재실행하지 않았다**(봉인 `--write` 가 working tree 를 바꾼다) — 구성 요소를 개별 재실행(§2.9). 소스 수정 0 · `git commit` 0.
- Serena: skipped — `.serena/project.yml` 없음(리뷰·재실행 · 소스 무수정).

## 1. 판정 표

| # | 필답 항목 | 판정 | 핵심 근거(상세 §2) |
|---|---|---|---|
| A-1 | ⑤-1 정정 대조 N-1(`_alias_defs` 전부 기록 + `_resolved_bases`) | **검증됨 + MINOR(N2-1)** | 합성 `MixUser(_B)`(mixin-first TC ClassDef) #646 p1 발화 → HEAD 무발화 ✓ · `[#493]` main→HEAD 4사본 집합 동일(3,216/3,225/3,225/173 · lost 0 gained 0) · main 픽스처 트리 9/9 ✓ — **단 `_exempt_override :719` 만 아직 `_resolved_base`(마지막 정의)를 써서 mixin-first + else ClassDef(N-2 형) + `clean() -> dict[str, object]` 조합에서 #647 거짓 위반(exit 2)** — 시제품 정정 뒤 4사본·픽스처 byte 동일(§2.1) |
| A-2 | N-2·N-3·N-4·N-5·N-9 | **검증됨** | 합성 `synth_ps/` p1 vs HEAD: N-2 else ClassDef `_B` ⓐ 소멸 ✓ · N-3 6형 전부 오라클대로(`tuple[object, ...]`·`tuple[object,str]`·`dict[object,str]` 무 · `tuple[str,object]=(loads, n)` 후보 · `dict[str,object]` 값·`list[object]` 무) ✓ · N-4 `jl`·`J.loads` → `json.loads` ✓ · N-5 한 줄 클래스 2→1 ✓ · N-9 «`e` 주석의» 붙임 ✓ · `import re :93` ✓ · 4사본 56b27e1→HEAD 차분 = **#647 메시지 띄어쓰기뿐**(1,037/1,033/1,053/473 · 경로·줄·규칙 키 차분 0) |
| A-3 | N-6(a)·N-7·C M4 | **검증됨 + MINOR(N2-2 · Q′ 공허 단언 잔존)** | `registry_gate.py:295 candidates is not None` · `:818 cand_new if (n_cands or l_cands) else None` = 계획 N′∪L′≠∅ ✓ · docstring 채널 1항(`:20~22`)·`candidate_*` 키 설명 ✓ · M4 검사기별 legacy(`:806~811`) ✓ · kkebi 게이트 재실측 = 구현 기록과 절·수치 동일(§2.6) · smoke 33/33 · Q 단언 `records == []`·`info #69`·`in` ✓ — Q′ `:315` 는 `payload_q2.get("candidate_lines", [])` 위 `all()` 이라 키 부재 시 공허 참(P0′ 의 키-부재 규칙과 충돌 방향의 회귀를 못 잡는다) |
| A-4 | #648/#649 합성 경계(`_tree_origins`·`_tree_dotted`·`_tree_union_members`·`_status_box_count`·`_schema_rootmodel_mix`) | **검증됨**(사각 3 — §4) | 25형 중 기대대로 22: `Optional[…] \| Status[B]`·문자열·`as S`·`import ninja`·`Union[…]`·`typing.Optional`·`responses.Status`·`Optional["Status[A]"]`·async·중첩 함수·OHS `*_service.py` 발화 / `Status[A \| B]`·`Status[A] \| None`·`A \| Status[B]` 무발화 · #649 `Schema, RootModel[…]`·`_S`(ninja.schema)·`pydantic.root_model`·무첨자·역순·중첩 클래스 발화 / `RootModel[…]` 단독·전이 상속 무 · **도메인 파일 무발화**(슬라이스 대상 = `api/**` + OHS — `_tree_slice2 :7350~7375`) ✓. 미탐 3(현장 0): `Annotated[Status[A] \| Status[B], …]` · `from typing import Union as U` · 함수 안 import |
| A-5 | 4사본 계수·exit·무손실 | **검증됨** | old(main)/new(HEAD) api-error 재실행: A∖B 0 · B∖A = spring #648 **7** · d2eaafe #648 **8**+#649 **1** · f5ee428 **8**+**1** · kkebi **6** · exit 전부 0→2 — `lossless2-verdict.txt` 와 전 셀·전 파일 일치(§2.3) · main 픽스처 트리 9/9 LOSSLESS 독립 재현 · RED 3 = 조각 1과 동일 원인(신설 픽스처 파일에 옛 #493 — 7·1·7) |
| A-6 | `finding_keys.append(None)`·emit 순서·ordered 대조 | **검증됨** | `_suppress_overlapped_tree :7392~7407` 이 `zip(tree.entries, tree_keys)` 로 억제 — `findings.add` 1 : `finding_keys.append` 1 이라 정렬 보존 · #648/#649 키 None 이라 억제 비대상 ✓ · stdout(`emit_all`)·레코드 sink 가 같은 `entries` 순서라 ordered 대조 통과 — 단 EXPECTED 는 **재생성**된 것(`--emit-expected` 스플라이스)이지 무변이 아니다 · `_ast.walk` BFS 라 중첩 함수/클래스 발화는 형제 뒤에 찍힌다(결정적 · 기대 무관) |
| A-7 | openapi 문면 2곳 · `:3371` 권장 | **검증됨 + MINOR(N2-3)** | `:5~7` docstring·`:3363` 조치 = R-0681 rev2 prefLabel «직접 반환 오류 타입 그대로의 response= 선언(concrete·Union·명시값 base — base 뭉뚱그림 금지)» 와 정합 ✓ · findings_count openapi 행 무변 ✓(docstring 비출력 · 조치는 code 레인 footer) · drift 골든 `53913d…` 무변 ✓ — **권장 `:3371`(HEAD `:3372` 주석)은 미검토·미기록**(stale 그대로) · 추가 stale 2곳: `:3358~3359` code 레인 헤더 «response= <Bc>ErrorSchema 계약 불일치» · **`:3478` 트리 슬라이스 #63 메시지** «`response={status: <Bc>ErrorSchema}` 로 직접 선언한다» — 후자는 openapi 골든 레인 stdout 4행에 실제로 찍힌다(고치면 count 지문·drift 골든 재생성 동반) |
| A-8 | 픽스처·매트릭스 | **검증됨 + MINOR(N2-4 · mypy 2)** | good exit 0 · bad exit 2 = `#120~#132·#474·#62 각 1 + #648×1 + #649×1 + ⓓ#125×1` ✓ · fixture 104/104 · baseline 73(`(2, 11, 11, 3, False)`) · count 73(`(2, 11, 1, …#648×1,#649×1)`) · cross «차이 0» · EXPECTED 변경 = 기존 쌍 **5행**(context-isolation·domain-model·layer-skeleton·public-surface·usecase-dto — 기록의 «4행» 은 오기) 신규 쌍 0 ✓ · drift 8/8 + old/new stdout diff = #648/#649 2줄 추가뿐(old×HEAD 픽스처 sha `b883cb…` = 구 EXPECTED · new `7e3edc…` = 신 EXPECTED) ✓ · **mypy strict(spring venv): 신설 good `payment_controller.py` 2 errors(`_use_case` attr-defined :15·:23 — 기존 `order_controller.py` 와 같은 골격 결함) · `schema_out.py` 등 4파일 0** — S-5 의 두 허용형 주석 자체는 0(문맥 추론으로 `Status(200, …)`·`Status(404, …)` 통과) · 기록에 mypy 실측 없음 |
| A-9 | 등재·소성물·미러 | **검증됨** | spec_lint «규칙 552 · ast 293 · ast+ 60 · human 27 · 위반 0» · #648/#649 행 셀 9(=#647 행) · 파이프 0 · 집계 293/281/500/552/435 ✓ · #63 행 08-25 span ✓ · rule-owner-map +2·#63 비고 ✓ · ROSTER +2(`_SCHEMA_ORIGINS`·`_ROOTMODEL_ORIGINS` — `_STATUS_ORIGINS` 는 Base 채널 아님 · 제외 타당) · pregate `--check` in-sync(56종·27) ✓ · byte 미러 6 `cmp` 동일 ✓ · rulepack `--check` 정합 ✓ · ISSUED R-3463~R-3467 ✓ |
| A-10 | 정직 기록(`d701df8` «verify 6/6» 거짓 → `cad221b`) | **검증됨 + 절차 문구 제안(§3-6)** | `verify3.log:423~425` «[manifest] RED · 봉인 후 변경 — construct_drift_report.py · tree_sha256 드리프트» = 원인 확인 · `cad221b` = manifest 재봉인(`sealed_commit 06fef51→d701df8` — 관례 = 봉인 시점 HEAD · 56b27e1/06fef51 도 925d8a8) + 기록·루브릭 정정 + `verify4.log` 6/6 · HEAD 에서 `manifest_seal --check --draft` **green** 재확인 · 처리 충분 — 남는 것은 관례 성문(«봉인은 마지막 쓰기 · verify RED 정정 뒤 재봉인 · 메시지의 verify 주장은 커밋 직전 로그 필수») |
| A-11 | 증거 스크립트 재현성 | MINOR(N2-5) | `patch_api_error.py` 를 main 에 재생 → HEAD 와 **byte 동일** ✓ · `patch_piece1_fixes.py` 를 56b27e1 에 재생 → public-surface 는 `_resolved_bases`(코디 부수 신설) 결손 · smoke 는 `.endswith` 판(첫 실행 실패판) → HEAD 와 다름 · `piece2_fixtures_and_registry.py` 의 #648 등재 행은 셀 안 파이프 3(NF 12 ≠ 커밋 9) — 커밋 본문은 정상이나 스크립트 3개가 커밋을 재현하지 못한다 |

**BLOCKER 0 · MAJOR 0 · MINOR 5(N2-1~N2-5)** + 절차 문구 제안 1 + 사각 6.

## 2. 항목별 상세

### 2.1 N-1 정정과 잔여 결함(A-1 · N2-1)

`_alias_defs :333~336` 이 TC 중간 ClassDef 의 Subscript 기저 전부 + 첫 기저(마지막 자리)를 기록하고, `_classify_base :829~833` 은 `tc_sub` 로 «어느 정의든 TC subscript 면 alias-tc» 를 잡는다 → 합성 `n1_mixin.py` `MixUser(_B)`·`MixForm(_F)`(`class _B(TranslatableAdmin, admin.ModelAdmin[Order])`) #646 p1 2건 → HEAD 0 ✓. `_is_declarative_class :378` 은 신설 `_resolved_bases :361~371`(정의 전부의 합집합)로 #493 면제를 회복 — 4사본 `[#493]` (sev·rule·file·message) 다중집합 main vs HEAD **동일**(spring 3,216 · d2eaafe 3,225 · f5ee428 3,225 · kkebi 173 · lost/gained 0).

잔여: `_resolved_base :351~358`(«뒤 정의 우선» = 목록 마지막) 의 유일한 남은 호출처가 `_exempt_override :719` 다. N-1 정렬 뒤 mixin-first 중간 ClassDef 의 «마지막 정의» = 첫 기저 = **mixin** 이라 `clean()`×Form 면제가 빠진다. 합성 `n1b_mixin_else.py`:

```python
if TYPE_CHECKING:
    class _F(FormMixin, forms.ModelForm[Order]): ...
else:
    class _F(FormMixin, forms.ModelForm): ...      # N-2 형(런타임 짝 ClassDef)
class MixElseForm(_F):
    def clean(self) -> dict[str, object]: return {}
```
→ HEAD `[#647] …:20: clean() 반환 타입의 값 자리가 object` **거짓 위반(exit 2)**. 정본형 else(`_F = forms.ModelForm` Assign 별칭 · `n1_mixin.py MixForm`)에서는 마지막 정의가 else 별칭이라 면제가 살아 무발화 — 즉 트리거 = mixin-first TC ClassDef ∧ else **ClassDef** ∧ 스텁 강제 오버라이드. 현장 4사본 mixin-first 0(rv5-A) 이라 잠복 · 시제품(§3-1) 적용 뒤 4사본 public-surface sink(record_id·run_id 마스킹) 및 `public_surface/{good,bad_rules}` stdout **byte 동일** · 합성 2건 소멸. MINOR(비정본 else 형 한정 · 정정 4줄).

부수 관찰: `_resolved_bases` 는 재대입 별칭(`X = Foo` 뒤 `X = Bar`)에서 합집합을 돌려 «둘 중 하나가 선언적이면 면제» 가 된다 — 검출 집합을 늘리지 않는 방향(면제 확대)이고 현장 무변이라 결함으로 세지 않았다.

### 2.2 N-2~N-5·N-9 합성(A-2)

`$S/rv5A2/synth_ps/application/orders/driven_layer/django_orders/admin/order/` 8파일 · p1(56b27e1) vs HEAD:

| 파일 | p1 | HEAD | 판정 |
|---|---|---|---|
| `n2_else.py` else 직계 `class _B(admin.ModelAdmin)` | `[#646] :9 _B 맨몸` | 무 | N-2 ✓(`rt_only :890` · `:923`) |
| `n3_slots.py` `tuple[object, ...]`·`tuple[object,str]=(loads,"n")`·`dict[object,str]={loads:…}` | ⓓ#650 :5·:6·:8 | 무 | N-3 ✓(Ellipsis 제거·idx·-1 키) |
| 〃 `tuple[str, object]=(loads,"n")` | 무 | ⓓ#650 :7 | ✓ (index 0 자리 = `str`) |
| 〃 `dict[str, object]={"k": loads}`·`list[object]`·`tuple[str,object]=("n", loads)` | 무(ⓓ#647 :9 만) | 동일 | ✓ |
| `n4_alias.py` `from json import loads as jl` | «`json.jl(…)`» | «`json.loads(…)`» | N-4 ✓(`:1026`) |
| `n5_oneline.py` `class One(admin.ModelAdmin): x = …  # type: ignore[type-arg]` | :4 헤더 + :4 속성(2) | :4 헤더(1) | N-5 ✓(`:933`) · `Two` 는 :7+:8 유지 ✓ |
| 메시지 조사 | «`e` 주석 의» | «`e` 주석의» | N-9 ✓ |

현장 56b27e1→HEAD public-surface 차분(4사본): 레코드 수 동일(4,537/4,543/4,562/1,291) · (sev·rule·file·message) 차분 = `#647` violation+info 메시지 띄어쓰기만(1,037/1,033/1,053/473) · (sev·rule·file) 키 차분 **0** — N-3·N-4·N-5·N-2 의 현장 효과 0, 기록과 정합.

### 2.3 #648/#649 합성·현장(A-4·A-5)

합성 `$S/rv5A2/synth_api/` · 명령 `cd synth_api && DJR_FINDINGS_JSON=… python3 dddjango/scripts/check-api-error-controller-contract.py . --error-profile auto` → exit 2 · #648 12(f01·f02·f03·f04·f05·f12·f14·f15·f16·f17·inner·OHS `g01`) · #649 6(C01·C03·C04·C05·C06·C08). 무발화: f06 `Status[A | B]` · f07 `Status[A] | None` · f08 `A | Status[B]` · C02 `RootModel[…]` 단독 · C07 전이(`Base(Schema)` + `RootModel`) · 도메인 `dom_schema.py` D01/d02(대상 밖) ✓. 미탐(사각 §4): f09 `Annotated[…]` 래퍼 · f10 `Union as U`(`_tree_union_members :7173` 이 이름만 본다) · f13 함수 안 import(`_tree_origins` 문서화된 한계). 현장 4사본 `application/**` 에 `-> …Annotated[`·`Union as`·`Optional as`·`import ninja`·`from ninja.responses import` 0 → 영향 0.

현장(각 실서고 venv · cwd=사본 · `--error-profile auto` · old=`$S/rv5A2/old`):

| 사본 | old exit/레코드 | new exit/레코드 | B∖A | 파일 |
|---|---|---|---|---|
| spring 7bfe1aa | 0 / 7 | 2 / 14 | #648 7 | accounts `account_controller.py` :173·:313·:359·:399·:459·:545 · fortune_record `record_archive_controller.py:94` |
| d2eaafe | 0 / 6 | 2 / 15 | #648 8 · #649 1 | accounts 6 · fortune_reading `evidence_provisioning_controller.py:159` · fortune_record :94 · **#649** `evidence_provisioning/schema/schema_out.py:151 EvidenceProvisionResponseSchema` |
| f5ee428 | 0 / 7 | 2 / 16 | #648 8 · #649 1 | 〃 |
| kkebi 6608fb0 | 0 / 27 | 2 / 33 | #648 6 | identity `profile_controller.py:127`·`web_session_controller.py:452` · review :192·:246 · saju `reading_controller.py:145`·`relationship_controller.py:227` |

A∖B 0 전부 · `lossless2-verdict.txt` 와 전 셀 일치. openapi 는 골든·count 행 무변으로 갈음(변경 2곳이 출력 밖/코드 레인 footer).

### 2.4 emit 순서·keys(A-6)

`_slice_check_controller_ast :7230~7242`: #649 는 ClassDef 워크(모든 클래스 · 파일 한정 없음), #648 은 FunctionDef 워크의 `routes` 계산 앞에서 `findings.add` + `finding_keys.append(None)` 쌍으로 방출. `_suppress_overlapped_tree :7392` 의 `zip(tree.entries, tree_keys)` 는 길이·순서 동일을 전제하므로 쌍이 깨지면 #62/#474/ⓓ#125 억제 좌표가 밀린다 — 쌍 유지 확인. findings_count «ordered» 대조는 stdout(`emit_all`)·sink 가 같은 `entries` 순서에서 나오므로 통과하고, EXPECTED 3 해시는 재생성값이다(무변 아님).

### 2.5 openapi(A-7)

변경 2곳(`:5~7` docstring · `:3363` 조치)은 R-0681 rev2 와 어휘 일치. 잔존 stale: `:3372` 트리 슬라이스 주석(계획 «권장 :3371» — 미검토·미기록) · `:3358~3359` code 레인 헤더 · `:3478` #63 트리 메시지(«`openapi_extra` 의 responses 보충 — 오류 응답은 `response={status: <Bc>ErrorSchema}` 로 직접 선언한다») — 후자는 `openapi_error_declaration/bad_rules` 골든 레인 stdout 4행에 실제 등장(`grep` 확인). 고치려면 findings_count 지문(message 포함)·drift 골든 `53913d…` 동반 재생성 — 규범 문면 축(B)과 함께 다음 조각에서.

### 2.6 registry_gate ⓔ2·smoke(A-3)

kkebi 사본 · `rv5a2_probe.md` 1파일 → `registry_gate.py . --anchor HEAD --introduced-json …`: 툴체인 `v2.17.17 · py3.14 · digest a268e474f016714c(39파일)` = `gate2-kkebi.log` 동일 · 귀속 0 · legacy 518(해소 2) · **ⓓ 신규 0 · legacy 1,269 · 검사기별 14행**(public-surface 573 · domain-model 363 · port-adapter 133 · usecase-dto 75 · layer-skeleton 56 …) 전 행 동일 · exit 0 · sidecar 키 8(`candidate_lines`·`candidate_records` 빈 목록 — N′∪L′≠∅ 규칙) ✓ · 실행 뒤 파일 제거·`git status` clean. smoke 재실행 33/33. Q(`:296~305`) 단언 = `candidate_records` 전부 `info`·`#69`·`fresh_probe.py in file` ∧ `records == []` ✓(«첫 실행 불일치 = `.endswith` 판» 을 replay 로 확인 — §2.10). Q′(`:312~316`) 는 `records` 전부 `schema_smoke` ∧ `candidate_lines` 전부 `fresh_probe` 이나 `payload_q2.get("candidate_lines", [])` 가 키 부재를 공허 통과시킨다 — `candidate_lines` 키가 빠지는 회귀(ⓓ 채널 유무 판정 실수)를 Q′ 가 못 잡는다(N2-2).

### 2.7 픽스처·매트릭스(A-8)

- `api_error_controller/good --error-profile auto` exit 0 · `bad_rules` exit 2 · 규칙 분포 `{#120,#121,#123,#124,#125(ⓓ),#126,#131,#132,#474,#62,#648,#649} 각 1` · #648 좌표 `payment_controller.py:10`(def 줄 · 데코 :9) · #649 `schema/schema_out.py:17` ✓. openapi good/bad exit 0 ✓.
- `fixture_matrix` 104/104 · `checker_baseline_matrix` 73 · `findings_count_matrix` 73(api-error `(2, 11, 1, …)` · public-surface 3열째 지문만 갱신 = N-9 메시지) · `checker_cross_matrix` «차이 0건» · EXPECTED diff = 기존 키 5개 값 변화(`#110 1→2`·`#256/#299 1→2`·`#488 26→37`·`#493 2→4`·`#193/#569/#570 1→2`) 신규 키 0 ✓ · `construct_drift_report` 8/8 · `$S/rv5A2/drift/`: old(main)×HEAD 픽스처 sha16 `b883cb584e61d5b1`(=구 EXPECTED) → new `7e3edccdbc247574`(=신) · `diff` = `[#648] …:10`·`[#649] …:17` 2줄 추가뿐 → 재생성 정당.
- mypy strict(`cd good && PYTHONPATH=MYPYPATH=$S/spring $PY -m mypy --config-file $S/spring/pyproject.toml --follow-imports=silent <5파일>`): `payment_controller.py:15·:23 "PaymentController" has no attribute "_use_case" [attr-defined]` 2 · 나머지 4파일 0. 기존 `order_controller.py` 도 같은 2(+`no-untyped-def`) — 조각 1 Δ9 «신설 파일만 strict 0» 기준으로는 미달·기록에 실측 없음(N2-4). S-5 의 검증 대상(두 허용형 · `Status(404, OrdersErrorSchema(…))` · `Status(200, PaymentOut.model_validate(…))` 문맥 추론 · `RootModel[Annotated[…]]` 단독)은 오류 0.

### 2.8 등재·소성물·미러(A-9)

`spec_lint` «규칙 552 · path 172 · ast 293 · ast+ 60 · human 27 · ⑧ 포함 · 위반 0» · `| 648 |`·`| 649 |` NF 9(=`| 647 |`) · 집계 `ast` 293(:218) · 판정×어겼을때 `ast` 281/293 · 계 500/552(:276·:279) · 읽는 법 435(:287) · #63 행 span(:387) ✓ · rule-owner-map :561~562 + #63 비고 ✓ · ROSTER `gen_pregate_symbol_kinds.py:136~141`(assign_set · expect · note) — `_STATUS_ORIGINS` 는 반환 주석 origin(Base 병기 채널 아님)이라 제외 타당 · `--check` in-sync ✓ · byte 미러 6(`cmp` 검사기 3·`registry_gate.py`·`pregate_symbol_kinds.json`·`rulepack.json`) ✓ · `ontology_rulepack --check` 정합 ✓ · ISSUED R-3463~R-3467 · LEDGER graph 6행 ✓.

### 2.9 verify 구성 요소 재실행(A-10)

`make verify` 대신 개별: corpus 는 미실행(B 축) · spec_lint ✓ · fixture ✓ · baseline ✓ · count ✓ · drift ✓ · cross ✓ · registry_gate_smoke ✓ · pregate `--check` ✓ · rulepack `--check` ✓ · `manifest_seal --check --draft` → «green · 그룹 10 · 봉인 파일 258 · 배정 18런 · draft» ✓(HEAD=cad221b · `sealed_commit d701df8` = 관례). `verify3.log:423~425` 의 RED 2건(«봉인 후 변경 — construct_drift_report.py»·«tree_sha256 드리프트») 이 `cad221b` manifest diff(`construct_drift_report.py` sha · harness `tree_sha256` · `sealed_commit`·`self_sha256`) 와 1:1 대응 — 정정 충분.

### 2.10 증거 스크립트 replay(A-11)

- `patch_api_error.py` → main 의 검사기 2개에 적용 → HEAD 와 `cmp` **동일**.
- `patch_piece1_fixes.py` → 56b27e1 의 3파일에 적용 → `registry_gate.py` 동일 · `check-public-surface-annotation.py` 는 `_resolved_bases`·`_is_declarative_class` 변경 결손(HEAD :361~378) · `registry_gate_smoke.py:302` 는 `.endswith("fresh_probe.py")`(HEAD 는 `in` + 주석) — 즉 스크립트가 «첫 실행 실패판» 이고 정정은 손편집.
- `piece2_fixtures_and_registry.py` 의 `rows` #648 문자열은 `-> Status[Out | Err]` 등 셀 안 파이프 3(NF 12) — 커밋 행(NF 9 · «`Status[Out, Err 의 union]`» 표기)과 다름 · #649 행은 동일.

## 3. 정정 제안(코드 수준)

### 3-1 (N2-1 · MINOR) `_exempt_override` — 별칭 정의 전부로 해소(`_is_declarative_class` 와 같은 해소 · `_resolved_base` 는 호출처 0 → 삭제 가능)

`dddjango/scripts/check-public-surface-annotation.py:717~722`(시제품 `$S/rv5A2/proto/` · `proto.diff` 15줄 · 4사본 sink·픽스처 stdout HEAD 와 byte 동일 · 합성 `n1b` 2건 소멸):
```python
    want = FRAMEWORK_OVERRIDE_EXEMPT[fn.name]
    for b in cls.bases:
        for base in _resolved_bases(b, bindings, aliases):  # 별칭 정의 전부(mixin-first 중간 ClassDef 포함) — `_is_declarative_class` 와 같은 해소
            if base in want or (fn.name == "deconstruct" and base.endswith("Field")):
                return True
    return False
```
codex byte 미러 동반 · `pregate_symbol_kinds.json` source_sha 재소성(`gen_pregate_symbol_kinds --write`) · 대표 골든은 public-surface 비대상이라 무변 · findings_count public-surface 행 무변(메시지 무변). 합성 회귀 픽스처로 `public_surface/good` 에 `admin/order/form/mixin_else_form.py`(위 `n1b` 형 · clean 면제) 1파일 추가를 권고 — cross 신규 쌍 0 확인 뒤.

### 3-2 (N2-2 · MINOR) smoke Q′ 공허 단언

`workspace/tools/registry_gate_smoke.py:315`:
```python
            and payload_q2.get("candidate_lines") and all("fresh_probe" in l for l in payload_q2["candidate_lines"])
            and payload_q2.get("candidate_records") and all(r.get("rule") == "#69" for r in payload_q2["candidate_records"])
```

### 3-3 (N2-3 · MINOR) openapi 잔존 stale 3곳 — 조각 3(문면 축과 동반)

`:3372` 주석 → «오류 응답은 operation 이 `response={status: 그 status 의 실제 오류 타입}` 로 «직접 선언»한다» · `:3358~3359` 헤더 «response= 선언 계약 불일치» · `:3478` 메시지 «오류 응답은 `response=` 에 그 status 의 실제 오류 타입 그대로 직접 선언한다(…)». `:3478` 은 레코드 메시지라 `findings_count_matrix --emit-expected`(openapi 행 3열째 지문)·`construct_drift_report --emit-expected`(openapi 행) 재생성 + LEDGER 무관(검사기) + byte 미러 — **봉인 전에** 한다(§3-6).

### 3-4 (N2-4 · MINOR) good 픽스처 mypy strict

`api_error_controller/good/.../payment/payment_controller.py` 에 use case 주입을 명시해 `attr-defined` 2 를 없앤다(기존 `order_controller.py` 도 같은 결함 — 함께 고치면 cross `api_error_controller × *` 계수가 바뀌므로 `checker_cross_matrix --emit-expected` 스플라이스 동반 · 신규 쌍 0 확인):
```python
from typing import Protocol
class _GetPayment(Protocol):
    def execute(self, query: GetPaymentQuery) -> object: ...
@api_controller("/payments")
class PaymentController:
    def __init__(self, use_case: _GetPayment) -> None:
        self._use_case = use_case
```
(Protocol 을 컨트롤러 파일에 두는 것은 픽스처 최소성 편의 — 트리 규칙상 `application_layer/payment/get_payment/get_payment_use_case.py` 실체가 정본이면 그 파일을 추가하고 cross 재산.) 어느 쪽이든 조각 2 기록에 «신설 good mypy strict: 컨트롤러 2(`_use_case` 골격) · 그 외 0» 을 추기.

### 3-5 (N2-5 · MINOR) 증거 스크립트 재현성

`impl/patch_piece1_fixes.py` 에 `_resolved_bases`·`_is_declarative_class` 치환과 smoke `in` 판정을 반영하고, `impl/piece2_fixtures_and_registry.py` 의 #648 `rows` 를 커밋 문자열로 교체(또는 «손편집 후 커밋» 을 스크립트 머리 주석에 명기). 검증 = 본 리뷰 §2.10 replay 명령(`git show <base>:<path>` → 스크립트 → `cmp`).

### 3-6 (절차) 봉인·verify·커밋 메시지 관례 — 계획 Δ3 ⑪ 과 메모리 `ontology-revision-recipe` 에 추가할 문구

> **봉인은 커밋 직전 마지막 쓰기다.** `manifest_seal --write`(⑪) 뒤에 봉인 대상(`workspace/tools/**`·픽스처·검사기·소성물)이 한 글자라도 바뀌면 — verify RED 정정·골든 `--emit-expected`·EXPECTED 스플라이스 포함 — ⑪ 부터 다시 한다(순서: 골든/EXPECTED 갱신 → 봉인 → `make verify` green → 커밋). **커밋 메시지의 «verify n/n» 은 커밋 직전 working tree 에서 실측한 로그(`evidence/impl/verify<N>.log`)를 가리켜야 하며, 로그 없이 쓰지 않는다.** 커밋 뒤 돌린 verify 는 그 커밋의 근거가 아니다 — RED 면 정정 커밋에서 «거짓 표기» 를 문면으로 남긴다(이번 `cad221b` 판형).

## 4. 사각

1. `_tree_union_members :7166~7179` 는 `Optional`/`Union` 을 **이름**으로만 본다 — `from typing import Union as U`·`U[Status[A], Status[B]]` 미탐(합성 f10) · `Annotated[Status[A] | Status[B], …]` 래퍼 미탐(f09). 현장 0. 닫으려면 `head = _tree_dotted(node.value, origins)` 를 `{"Optional","Union","typing.Optional","typing.Union","typing_extensions.Optional","typing_extensions.Union"}` 와 대조하고 `typing.Annotated` 는 첫 원소로 내려간다(4줄).
2. `_tree_origins :7120` 은 함수·클래스 본문 안 import 를 무시한다(f13 무발화 · 문서화됨) · 모듈 수준 `Status = …` 재대입은 pop 하지 않는다 — 현장 0.
3. #649 는 전이 상속(`class Base(Schema)` → `class X(Base, RootModel[…])`) 미탐(C07) — docstring 이 «함께 상속» 만 말하므로 문면과 일치하나 등재 행(#649 «ninja Schema 를 함께 상속하지 않는다»)의 독자는 전이도 기대할 수 있다 — B 축에 넘긴다.
4. `_ast.walk` BFS 순서: 중첩 함수/클래스의 #648/#649 는 형제 뒤에 찍힌다(합성 `inner` :26 이 f17 :32 뒤 · `C06` :30 이 C08 :39 뒤) — 결정적이라 골든에는 무해하나 «파일 안 줄 순서» 를 기대하는 독자에게 낯설다.
5. mypy 는 `payment` 세트 5파일만 돌렸다(bad 세트는 의도적 red 라 제외) · openapi 검사기는 4사본 재실행 없이 골든·count 무변으로 갈음.
6. 사본 오염: `$S/spring/mp_probe_rv5b/`(⑤-1 리뷰어 B 잔류 · `p18_exact.py` 1파일 · 루트 직계라 api-error `_tree_bcs2` 대상 밖 · public-surface 는 old/new 양쪽에 같은 6 레코드 → 접두 제외) · 본 리뷰 종료 시점 4사본 tracked 무변 · 내 파일 0. `verify-ontology`·corpus 미러·codex hand 미러·Coordinator ⓔ1 문면은 B/C 축 — 여기서는 rulepack `--check`·spec_lint·byte 미러만 봤다.
