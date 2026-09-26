# 진단 B3 — pre-gate 결함 F4-21 · F4-22 · F4-23 (+ 툴체인 digest)

- 작성 2026-09-26 · 진단만(저장소 수정 0) · 대상 = 현행 main(`git diff dddjango--v2.18.3 HEAD` 가 `design_pregate.py`·`anchor_diff.py`·`check-port-adapter-pairing.py` 에서 공백 → 현장 2.18.3 과 같은 코드).
- 표기: **[검증]** = 코드 인용·현장 증거 대조·scratch 재현으로 확인 · **[추론]** = 확인하지 않은 판단.
- 재현은 전부 scratch 사본(`…/scratchpad/f4-22/` · `DJR_VIOLATIONS_DIR=…/f4-22/viol`)에서만 했다. 현장 저장소는 읽기와 `git show`/`log` 만 했다. Serena·Graphify는 쓰지 않았다(지시로 금지).

## 0. 요약

| # | 근본 원인(한 줄) | 재현 | 수정 범위 | 권고 순위 |
|---|---|---|---|---|
| F4-21 | 형식 검사가 «기준선 부재 ∧ HEAD 실존»을 두 갈래(기실현 add / 타 레인 유입)로만 나누고, 사본에도 승인 유입이 없다 | scratch 재현 ✓ | 스크립트 + graph-owned(Coordinator) + Codex 의미 미러 | 4 |
| F4-22 | #574 는 본문 `Call` 을 보는 규칙이라 스텁에서 원리적으로 안 뜬다(설계상 C급 사각). 방향 규칙 #573/#574 는 배포 산문에 없다 | scratch 재현 ✓ | 스크립트(선언 검사 1종) + 선택: graph-owned 산문 | 3 |
| F4-23 | `--base ≠ HEAD` 일 때 «HEAD 대비 dirty»를 «기준선 트리» 위에 겹쳐 혼합 상태가 된다. 그 때문에 신규 BC 골격 가드가 오판한다 | 현장 증거 + scratch 재현 ✓ | 스크립트만 | 2 |
| digest | `--check-report` 최신성은 블록 해시만 본다. 툴체인이 바뀌어도 옛 예보가 «최신»이다 | 코드 확인 | 스크립트 + 권고: graph-owned 문면 | 1 |

## 1. 공통 배경 — 격리 사본은 어떻게 만들어지나 [검증]

- `main()` 은 `_extract_archive(repo, base_sha, copy)` 로 **기준선 트리**를 풀고, 이어서 `in_baseline` 을 계산한다(`dddjango/scripts/design_pregate.py:2885-2889`). 다음이 형식 검사다(`:2893-2895` — HEAD 조회는 `--base` 를 명시했을 때만 한다). 그 뒤 `_overlay_dirty` 를 부르고(`:2908`), `lift_realized_adds`(`:2910`)를 거쳐 앵커를 커밋한다(L).
- `_overlay_dirty`(`:1114-1150`)는 `git status --porcelain`, 곧 **worktree 대 HEAD** 차분을 사본 위에 복사한다. 사본은 기준선 트리다. 그래서 기준선이 HEAD 가 아니면 차분의 기준과 사본의 트리가 서로 다르다.
- 사각 목록 S7 은 이 동작을 «사본 = 기준선 트리 + (worktree−HEAD) 오버레이 — 기준선 이후 커밋분은 사본에 없다»로 적는다(`:2483-2486`). 이것이 의도된 설계라는 증거는 픽스처 E1 이다. E1 은 «기준선 이후 커밋된 add → 사본 밖 → 스텁 · 기실현 0»을 고정한다(`workspace/tools/pregate_fixture_run.py:559-573`).
- `--check-report` 는 git 을 부르기 전에 끝난다(`:2828-2829`). 그래서 함께 준 `--base` 는 무시된다. scratch 에서 확인했다: `--check-report … --base <G1>` 의 출력에 리포트 속 기준선(M^2)이 그대로 찍혔다.
- 신규 BC 골격 가드는 사본의 앵커 커밋에 `application/<bc>` 가 하나라도 있으면 `materialize_skeleton` 을 건너뛴다(`:1891-1900` · `git ls-tree HEAD application/<bc>`).

## 2. F4-21 — 승인 main 머지 유입을 «타 레인 유입 STOP»으로 처리

**원인 [검증]**
- `baseline_form_errors`(`design_pregate.py:2623-2661`)는 update 대상이 기준선에 없고 HEAD 에 있으면 `:2646-2649` 의 형식 red 를 낸다. 메시지가 주는 갈래는 «자기 기실현 add 면 add 로 복원 · 타 레인 유입이면 STOP» 둘뿐이다. 승인 유입이라는 세 번째 갈래가 없다.
- `--approved-merge-file` 는 registry_gate 에만 있다(`registry_gate.py:704` · 판정은 `_provenance_split` `:531-625`, F1 blob 3중 일치는 `:606-609`). 로더는 `anchor_diff.load_approved_merges`(`anchor_diff.py:256-321`)다.
- Coordinator 도 승인 목록을 registry_gate 에만 동반시킨다(`dddjango/commands/dddjango.md:30`·`:167`).
- 형식 red 를 통과시켜도 문제는 남는다. 사본은 기준선 트리라서 승인 머지로 들어온 파일이 사본에 없다(§1). 그러면 update 시뮬레이션과 계약 실존 판정이 그 파일을 보지 못한다.

**현장 증거 [검증]**
- `.dddjango/20260912-1312-fortune-house-b4/pregate-report.md:3541-3549` 가 형식 red 1건이다(`tests/test_search_term_mapping.py`).
- `s4-r21-pregate-provenance.json` 의 blob 값: 9e303793=null · HEAD^1=null · HEAD^2=HEAD=`91960aef`. `pregate_supports_approved_merge_file: false` 이다. 곧 F1 이 완전히 성립하는 verbatim 유입이다.

**현장 보고 문면 정정 [검증]**
1. «check-report 에도 입력이 없다»는 틀렸다. check-report 는 마지막 절의 문자열만 읽는다(`:2703-2768`). exit 3 은 마지막 판정이 형식 red 였기 때문이다. pre-gate 만 고치면 check-report 는 그대로 통과한다.
2. 발주자가 승인한 우회(`--base 97cdb35f` = M^2)는 사본에서 레인 자신의 S1~S3 커밋을 뺀다. 그런데 check-report 는 기준선을 해석만 하고 대조하지 않는다(`:2766` 에서 표시만 한다). 그래서 `s4-r22/r23-check-report.txt` 는 «정합 · 기준선 97cdb35f958e» 로 통과했다. 기준선 치환이 도구상 보이지 않는다.

**재현 [검증]** scratch `r21`: base → lane S1 → main 이 `config/inflow_settings.py` 추가 → `merge --no-ff main` → 명세 `update config/inflow_settings.py`.

| 조건 | 결과 |
|---|---|
| `--base <G1>` | exit 3 «update 대상 기준선 이후 실존» |
| 같은 조건에 `--approved-merge-file` | exit 1 «unrecognized arguments» |
| `--base main`(현장 우회) | exit 0 · 기준선 e3ba311 |
| 이어서 `--check-report` | exit 0 · «기준선 e3ba31139e86» |

**수정안(최소)**
- S-1 `design_pregate.py` [스크립트 · Codex byte 미러 동반]
  - `anchor_diff.APPROVED_MERGE_FLAG` 를 받는다. 검증은 `load_approved_merges(path, repo, base_sha, head_sha)` 를 재사용한다 — 사슬 · 2부모 · 구간 검증이 registry_gate 와 같다.
  - 승인 유입 집합 I 를 정의한다: I = {p | ∃ 참여 M: blob(M^1:p) ≠ blob(M:p) = blob(M^2:p) ∧ p ∉ 기준선 트리}. registry_gate F1 의 앞 절과 같다. 충돌 해소분(M ≠ M^2)은 제외한다.
  - ⓐ 형식 검사: update·remove 는 `in_baseline ∪ I` 로 실존을 판정한다. add 가 I 에 들면 «add 충돌(승인 유입 실존)» 형식 red 를 유지한다.
  - ⓑ 사본: 형식 검사 뒤, 오버레이와 앵커 전에 I 의 blob(M:p) 를 사본에 쓴다. 그러면 L 에 실리므로 타 레인 실물의 위반은 L∩N 으로 귀속 밖이 된다.
  - ⓒ stdout·리포트 헤더에 «승인 유입 N경로(머지 sha12…)» 행을 싣는다.
  - ⓓ `:2647` 메시지에 세 번째 갈래 «승인 머지 유입이면 `--approved-merge-file`»를 추가한다.
  - check-report 는 무변이다.
- G-1 [graph-owned] `dddjango.md:30`(산출물 위치 절 `:15`)·`:98`(Phase 1 절 `:83`)·`:167`(Phase 2 절 `:101`)은 전부 graph-owned 다.
  - 정본은 `ontology/rules/command-dddjango.ttl:3176`(승인 목록) · `:3360`(캐시 skip · 재발화 판형) · `:3802`(승인 머지 문단)이다.
  - 넣을 문면: «approved-merges.txt 가 있으면 `--base` 재발화 pre-gate 에도 동반».
  - 절차: `ontology_render.py --apply command-dddjango` → `make rulepack` → `codex-dddjango/skills/dddjango/SKILL.md:116` 의미 미러. 기존 표현의 개정이므로 새 ID 채번이 필요한지는 개정 레시피로 판단한다.
- 선택: check-report 에 기대 기준선을 대조하는 입력을 둔다(우회의 가시화). 최소 범위 밖이다.

**위험 · 영향 픽스처** — 중간.
- 새 입력 채널이 앵커 L 을 넓힌다. 다만 신뢰 부류가 registry_gate 승인 채널과 같다(발주자 소유 · verbatim 한정).
- 플래그를 안 주면 경로가 동일하다. 기존 mid · enforce · checkreport 묶음의 기대값은 무변이다.
- `pregate_fixture_run.py` 에 새 묶음이 필요하다: 무플래그 exit 3 / 플래그 exit 0 + «승인 유입 1» / I 에 든 add → exit 3 / 승인 목록 밖 머지 → exit 1.

## 3. F4-22 — use case 의 `<data>_in` 생성(#574)을 설계 단계에서 못 잡음

**원인 [검증]**
- #574 는 두 조건을 요구한다(`check-port-adapter-pairing.py:1333-1358`): application_layer 파일이 `*_in`(port/framework) 모듈에서 이름을 import 하고, 그 이름을 **`ast.Call` 로 호출**해야 한다.
- 스텁 본문은 `...`/`raise NotImplementedError` 뿐이다(설계 `workspace/design/2026-09-01-pregate-design.md:56`). 그래서 스텁에서는 원리적으로 뜨지 않는다. 이는 설계 비목표 «C급 본문 규칙»에 해당한다(`:16`). 백테스트도 #574 ×2 를 «명세-유래 · C급 사각»으로 분류했다(`workspace/design/2026-09-01-pregate-backtest.md:23` · `workspace/eval/pregate-backtest/classification.md:71-72`).
- 설계 단계 신호는 명세에 이미 있다. h1 명세의 포트 **인자** 타입이 바로 그 자료다(`design-spec.md:357` `run_select(triples: tuple[GraphTripleOut,…])` · `:365` `fetch(…, arguments: UpstreamFetchArguments)`. rename 전에는 `_in` 이었다 — `:7` 개정 주석).
  - 인자로만 쓰이고 어떤 포트 메서드도 반환하지 않는 `_in` 자료라면, 앱이 그 자료를 얻는 길은 직접 생성뿐이다(#574 확정).
  - 백테스트 2건(`ReadingBundlePort.pin(ReadingBundleIn)`·`translate(TranslateQueryIn)`)도 같은 형태다.
- #573/#574 방향 정의(«들어오면 `_in` · 나가면 `_out` · `_in` 생성은 어댑터뿐»)는 내부 설계 문서 `workspace/design/2026-08-08-tree-revision-spec.md:895-896` 에만 있다.
  - `dddjango/skills`·`agents`·`commands` 를 grep 하면 0건이다. 검사기 메시지(`check-port-adapter-pairing.py:298`)에만 있다.
  - houserules 트리는 `<data>_out.py`·`<data>_in.py` 이름만 보여 준다(`discipline-houserules/references/final.md:93-94`).
  - [추론] architect 가 «메서드 입출력» 기준으로 이름 붙인 것은 이 산문 공백의 결과다.

**재현 [검증]** scratch `r22`: green2 명세 변형이다(`render_request_in.py::RenderRequestIn` + 포트 `render(self, *, request: RenderRequestIn)` + use case).

| 단계 | 결과 |
|---|---|
| pre-gate | exit 0 green · 선언 확정/후보 0 |
| 보존 사본의 스텁에 check-port-adapter-pairing | exit 0 · #574 0 |
| use case 에 `RenderRequestIn(number=query.number)` 한 줄 추가 후 | exit 2 `[#574] …render_invoice_use_case.py:9` |

**수정안(최소)**
- S-2 `check_declarations`(`design_pregate.py:1699-1787`)에 선언 검사 «#574 예보»를 추가한다 [스크립트]. `_DeclarationTypes.resolve` 를 재사용한다.
  - 대상은 add·update 포트 계약 클래스(`application_layer/port/**`·`framework/**`)의 메서드다.
  - **인자** 주석이 `*_in` 모듈(검사기 `:1349` 와 같은 술어) 클래스로 해소되는데, 그 신원이 계획 · 사본의 어떤 포트 메서드 **반환**에도 나오지 않으면 → 선언 확정이다(차단 · 전건 처분).
  - 해소 불능이면 → 선언 후보다.
  - 사각 목록 S2 문면(`:2473`)에 이 범위를 추가한다. S1~S9 개수 단언(`pregate_fixture_run.py:841-842`)은 무변이다.
- G-2 [graph-owned · 권고] #573/#574 방향 정의를 배포 산문에 올린다. 후보는 houserules §1·§3(`discipline-houserules/references/final.md:38`·`:265`, 둘 다 graph-owned → `ontology/rules/discipline-houserules-final.ttl`) 또는 architect 계약이다. Coordinator `:96` 의 «명시 효과와 출처 결합 DTO의 지원 밖은 S2» 문면도 정합화한다(`command-dddjango.ttl:3417`).

**위험 · 영향 픽스처** — 낮음~중간.
- 새 차단 항목이다. 기존 레인이 재발화할 때 legacy 포트가 `_in` 인자를 쓰면 확정이 뜰 수 있다. 다만 실위반이고 ignored+빚 경로가 있다. 캠페인 재측정 스캔의 #574 는 0건이다(`refactor-campaign/evidence` grep).
- 새 픽스처 명세가 필요하다: 양성 1(인자 전용 `_in`) · 음성 2(`_out` rename · 다른 포트가 반환한 `_in` 중계).
- `gen_pregate_symbol_kinds.py --check` 와 checkreport 묶음은 무영향이다(스텁 종류 무변).

## 4. F4-23 — `--base` 재발화가 부분 상태에서 어긋남

**원인 [검증]** §1 의 혼합 사본이 원인이다. 기준선 ≠ HEAD 인데 WIP 가 dirty 하면, 사본은 «기준선 트리 + HEAD 대비 dirty 파일»이 된다.
- 계획 add 는 `lift_realized_adds` 가 걷어낸다(`:1218-1236`). 하지만 계획 밖 dirty 파일(새 폴더의 `__init__.py` 등)은 앵커 L 에 남는다.
- 그 결과 신규 BC 가드(`:1896-1900`)가 «이미 있는 BC»로 오판하고 골격 실체화를 건너뛴다. 그러면 기준선 이후 S1 이 커밋한 골격 칸이 사본에 없어 #488/#569 가 N∖L 로 귀속된다.
- clean tree(WIP 커밋 뒤)에서는 오버레이가 공집합이다. 사본 = 기준선 트리이고 BC 부재 → 골격 실체화 → green 이 된다.

**현장 증거 [검증]** h1 `pregate-report.md` 와 커밋 시각을 대조했다.

| 시각(KST) | 사건 | 결과 |
|---|---|---|
| 02:12:48 | pre-gate `--base 16dd54bb` · 블록 해시 c40161ad04da | 귀속 red 24(#488 ×22 · #569 ×2) · 결손 0 (`:200-207`) |
| 02:39 | S2 커밋 `e2a58a51` | S2 WIP 동안 계획 밖 `__init__.py` 23개가 untracked 였다(`git show --name-status`) |
| 02:42:38 | 같은 해시 · 같은 기준선으로 재실행 | green (`:291-298`) |

- 02:12 는 S2 커밋 전이므로 부분 상태였다.
- 귀속 24건의 경로는 **전부** S1 커밋 `a1e1635b`(부모 = 16dd54bb)가 추가한 파일이다. 예: `in_memory_adapter/{command,…}/__init__.py` · `django_rag_service_library/{admin,migrations,models}` · `test/{e2e,factories,fake}` · `*_command.py` 2.

**현장 보고 문면 정정 [검증]**
1. 증상은 «실존 결손 오탐»이 아니다. 귀속 red 24 이고 결손은 0 이다.
2. `--check-report` 는 git 을 쓰지 않는다(§1). 어긋난 것은 pre-gate 실행이다.
3. «사용 조건 미문서화»는 절반만 맞다. Coordinator 는 «미커밋 WIP 는 커밋 또는 stash 후 실행»을 규정한다(`dddjango.md:98`·`:182`·`:197`). 하지만 도구는 이 조건을 강제하지도 알리지도 않고, S7 은 오버레이를 정상 동작처럼 적는다. h1 레인은 이 조건을 어기고 실행했다(STOP 문서 «S2 미커밋»).
4. 캠페인 plan-v2 `:29` 의 «F4-22/23 — 모든 레인 G1 에 영향»도 고쳐야 한다. G1 초기 예보는 기본 `--base HEAD` 라서 오버레이가 정합하다. F4-23 은 Phase 2 재발화에서만 생긴다.

**재현 [검증]** scratch `r23`: `green-spec.md` · 기준선 ffe57dd.

| 단계 | 상태 | 결과 |
|---|---|---|
| T0 | 기준선 그대로 | exit 0 |
| T1 | S1 커밋(BC 일부) 뒤 clean | exit 0 |
| T2 | S2 WIP(계획 밖 untracked `test/__init__.py`·`test/unit/__init__.py` + 계획 add) | **exit 2** `[#488] application/billing/domain_layer/domain_service` |
| T3 | S2 커밋 뒤 clean | exit 0 |

T2 의 보존 사본을 보면 billing 아래에 `driving_layer`·`driven_layer` 가 없다 → 골격 건너뜀을 확인했다.

**수정안(최소 · 스크립트만)**
- S-3 `main()`(`:2908`): `explicit_base ∧ base_sha ≠ HEAD` 이면 `_overlay_dirty` 를 부르지 않는다. 대신 «dirty overlay 생략(기준선≠HEAD · N경로 — 재발화 사본 = 기준선 트리 + 이 명세 스텁)» 1행을 stdout 과 헤더에 싣는다.
  - 결과는 규약을 지킨 실행(WIP 커밋 또는 stash)과 같아진다. T2 가 T1/T3 과 같은 값이 된다.
  - 기본 모드와 `--base HEAD` 는 무변이다.
  - 문서 문면도 고친다: docstring `:106-110` · S7/S8(`:2483-2490`) 스크립트 상수.
  - Coordinator 문면(`:98`)은 여전히 참이므로 graph 수정이 필요 없다.
- 기각: 현장 제안 «사본 = 기준선..HEAD + 작업 트리». 이렇게 하면 레인의 기실현 실물이 앵커로 섞여 들어가 재발화 예보의 뜻(«G1 기준선 대비 계획»)이 G2 의 몫과 섞인다. E1 계약(`pregate_fixture_run.py:559-573`)과도 충돌한다.
- 대안: dirty 면 exit 1 로 거절한다. 현장처럼 `.dddjango/` 를 추적하는 저장소에서는 명세 개정마다 커밋을 강요하게 되어 마찰이 크다.

**위험 · 영향 픽스처** — 낮음.
- 기존 mid 묶음 E1~E4 · E1′/E2′ 는 무변이다. E2 · E2′ · E4 는 기준선 = HEAD 이고, E1 · E1′ 는 clean 이다(`:554-637` 을 읽고 확인).
- `pregate_transcription_smoke.py:254-` 는 기본 모드라 무영향이다.
- 새 케이스 E5(위 T2 판형 → exit 0 기대)를 추가해야 한다. mid 리포트 헤더 수 단언(`:636` «6»)은 별도 리포트를 쓰거나 계수를 갱신한다.
- [추론] 이 결함은 신규 BC 골격 가드 말고도 기존 BC 의 새 자리표시자 폴더에서 L 을 오염시킬 수 있다. 그 경우 주로 오탐이지만 미탐 가능성도 배제할 수 없다. S-3 은 이 경로 전체를 닫는다.

## 5. 툴체인 digest — pre-gate 최신성

- [검증] 리포트 스탬프는 `dddjango v<버전> · 블록 해시` 뿐이다(`design_pregate.py:2502-2504`). `check_report` 는 블록 해시만 비교한다(`:2727-2730`). Coordinator 캐시 skip 도 블록 해시만 조건으로 쓴다(`dddjango.md:98`). R2/R3 지적(`review-R2-evidence.md:95`·`review-R3-risk.md:159`)과 일치한다.
- [검증] digest 함수는 이미 registry_gate 에 있다(`_tree_digest`·`_toolchain_line` `registry_gate.py:227-242` — scripts 폴더의 `*.py`·`*.json` 전량). pre-gate 는 `registry_gate` 를 이미 import 한다(`:136`). Claude 와 Codex 의 scripts 폴더는 `diff -rq` 공백이므로 런타임에 따라 digest 가 갈리지 않는다.
- S-4 [스크립트]
  - `_executor_stamp` 에 `· 실행 트리 digest <registry._tree_digest()[0]>` 를 붙인다.
  - `check_report` 에 두 판정을 추가한다: 리포트 digest ≠ 현재 → «stale(툴체인) · 재발화», 토큰 없음 → «툴체인 증명 불가(구판 헤더)». 구판 해시 처리(`:2727`)와 같은 방향으로 fail-closed 다.
  - `요약:` 행에 digest 일치 여부를 싣는다.
- G-4 [graph-owned · 권고] 캐시 skip 조건에 «∧ digest 동일»을 추가하고(`command-dddjango.ttl:3360`), G2 최신성 1행 문면(`:3809`)도 고친다. 이것 없이도 안전하다. check-report 가 stale 로 막아 재실행을 강제하므로 자기교정된다. 다만 헛 skip 한 번의 비용이 든다.
- 픽스처: checkreport 묶음(`pregate_fixture_run.py:779-835`)은 같은 실행에서 만든 리포트라 digest 가 같다. «구판 헤더» 케이스는 해시 토큰만 지우므로 여전히 3 이다. 새 케이스 2개(digest 불일치 → 3 · digest 토큰 없음 → 3)를 추가한다.
- 위험: 낮음. 대가는 릴리즈마다 진행 중 레인이 1회 재실행하는 것이다. 이는 의도된 «버전 동결» 기계 집행이다.

## 6. 우선순위 권고 (BC 전역 리팩터 캠페인 · 레인마다 G1 pre-gate)

1. **digest(S-4)** — 스크립트만 고치면 된다. 모든 레인의 G1 예보가 G2 까지 유효한지 지키는 유일한 항목이다. 캠페인 S2 수리 묶음(F4-24 · F4-20 검사기 변경)이 캠페인 도중 릴리즈된다(plan-v2 `:29`). 합의된 «버전 동결 · 릴리즈 창»(review-synthesis `:16`)을 기계로 집행하는 수단이기도 하다.
2. **F4-23(S-3)** — 스크립트만 · 위험 낮음 · S-4 와 한 릴리즈로 묶을 수 있다. G1 에는 무영향이다. 다만 여러 슬라이스로 도는 리팩터 레인의 STOP → 명세 개정 → 재발화 고리에서 거짓 red 와 잘못된 처분(filtered/ignored 오기재)을 없앤다.
3. **F4-22(S-2, 선택 G-2)** — G1 시점 검출이라 캠페인 G1 에 직접 닿는다. 그러나 캠페인 빚 스캔의 #574 는 0건이다. 그래서 새 설계의 명명 오류만 대상이다(이력 4회). 산문 공백(G-2)은 graph 개정이 필요하다.
4. **F4-21(S-1 + G-1)** — 변경 폭이 가장 크다(스크립트 + graph-owned + Codex 의미 미러 + 픽스처). 캠페인 파동 규칙(동시 3 · 생산자/소비자 쌍 분리 · 직렬 착륙, plan-v2 `:33`·`:64`)이 main → 레인 머지 노출을 줄인다. 당장은 발주자 승인 우회가 있다. 다만 check-report 가 기준선 치환을 보지 못한다는 점(§2 정정 2)은 캠페인 발주서에 «재발화 기준선 = G1 SHA 확인» 1행으로 막아 두기를 권한다.

## 7. 재현 기록 (scratch · 재실행 가능)

- 헬퍼: `…/scratchpad/f4-22/pg.sh`. 복사한 scripts 로 `.venv/bin/python design_pregate.py` 를 실행하고 `DJR_VIOLATIONS_DIR=…/viol` 을 설정한다.
- 출력:
  - F4-23: `t0.out`~`t3.out` · 저장소 `r23`
  - F4-21: `t21a~d.out` · 저장소 `r21` · `spec21.md` · `approved-merges.txt`
  - F4-22: `t22.out`·`c22a.out`·`c22b.out` · `spec22.md` · 보존 사본 `k22`
- pre-gate 가 자체적으로 만든 시스템 임시 사본(`/var/folders/…/design-pregate-*`)은 `--keep` 확인 뒤 지웠다.
