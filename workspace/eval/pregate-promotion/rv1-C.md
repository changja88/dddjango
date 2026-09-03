# rv1-C — pre-gate 차단 승격 배치 ① 적대 리뷰 · 리뷰어 C(코퍼스 정합·드리프트·표본 외)

- 대상: `workspace/plan/2026-09-03-pregate-promotion-rubric.md` 패키지 초안 P1~P9 · 브랜치 `feat/pregate-enforce` HEAD `399796a`(main `36e9f11` +1 docs 커밋 — 루브릭 파일 1개뿐).
- 방식: 저장소 읽기 전용(이 파일만 씀) · 라이브 저장소(`~/Desktop/spring_dream_server`·`~/Desktop/kkebi-server`) 읽기만 · 실행은 `pregate_fixture_run.py`·`make verify`·`design_pregate.py --block-hash`(출력 전용·git 0회) 세 종.
- 표기: 근거는 `파일:행`. 근거 없는 주장은 «미확인». Serena: skipped — 워크트리에 `.serena/project.yml` 없음(기본 도구로 진행).

## 0. 판정 요약

| # | 심각도 | 요지 | 근거 |
|---|---|---|---|
| C-1 | **MAJOR** | 리비전 번호·IRI 오기. R-3432·3433·3434·3436·3437·3438 은 **전부 `@2026-09-03` Expression 을 이미 점유**(수리 배치 2). 이 배치의 새 Expression 은 `@2026-09-03b` 접미가 필수이고 rev 번호는 R-3433 **rev4**(현행 rev3) · R-3436 **rev3**(현행 rev2 clarification) · R-3438 **rev3** · R-3432 rev3(맞음) · R-3437 **rev3**. 루브릭 «R-3433 rev3»·«R-3436 rev2» 는 현행과 같은 번호라 그대로 집행하면 게이트가 아니라 사람이 헷갈린다 | `ontology/rules/command-dddjango.ttl:2811-2907` · 선례 `discipline-houserules-skill.ttl:653`(R-3417@2026-09-01b) · `architecture-ddd-final.ttl:1741,1755`(R-3442/3443@2026-09-03b) |
| C-2 | **MAJOR** | R-3437(s003/b10) 은 «(검토)» 가 아니라 **필수 개정**. 배너 1행 형식에 `구형 명세 skip 이면 skip(구형 명세)` 가 성문돼 있어 P2/P5 뒤 죽은 분기가 남고, P3 의 `red N건 · 처분 전건 기재` 도 이 블록이 소유하는 형식 문면이다. codex 62행 동형 | `command-dddjango.ttl:3053`(s003/b10 · statesNorm R-0151~0157, R-3437) · `dddjango/commands/dddjango.md:58` · `codex-dddjango/skills/dddjango/SKILL.md:62` |
| C-3 | **MAJOR** | P6 «G2 배너 1행» 의 착지 블록이 없다. G2 배너 = s007/b57(R-0406~R-0411) · G2 배너 항목 추가 선례 = s007/b58(**신규 규범 R-3440/3441 + 신규 블록**). R-3432 는 s006/b9(Phase 1) 소유이고 코퍼스 전체에서 규범↔블록은 1:1(2+ 블록이 statesNorm 하는 규범 0건) → «R-3432 rev3 amendment» 로는 Phase 2 배너 문면을 실을 수 없다. 선택지 ⓐ 신규 채번(R-3444~)+s007 신규 블록 ⓑ R-0411(b57) 또는 R-3440(b58) amendment ⓒ R-3437 을 G1/G1′→G2 로 확장 | `command-dddjango.ttl:3301-3307`(b12) · `3646-3652`(b57) · `3653-3659`(b58) · `3721-3726`(s009/b3) · 중복 검사 `grep statesNorm … uniq -d` = 0 |
| C-4 | **MAJOR** | s006/b10(«pre-gate 캐시 skip·재발화 판형» — R-3432 rev2 의 텍스트 carrier)에 **`djr:statesNorm` 이 없다**. kind-norm 블록이 규범 무연결이고 rulepack 의 R-3432.block 은 s006/b9 다. P6 가 b10 을 건드리면 렌더·LEDGER 는 되지만 규범 조인·rulepack 에는 반영되지 않는다. SHACL `BlockShape-statesNorm` 에 minCount 가 없어 게이트가 못 잡은 것 — 이 배치에서 b10 에 `statesNorm djr:R-3432` 부착 여부를 결정해야 한다 | `command-dddjango.ttl:3213-3217` · `dddjango/scripts/rulepack.json:60664`(block=s006/b9) · `ontology/shapes/djr-shapes.ttl:61-64` · `ontology/LEDGER.tsv:1541`(«R-3432 rev2(s006/b10 신설)») |
| C-5 | **MAJOR** | 하네스 문자열 고정: 러너가 리포트 문면 `(권고·비차단)`·`- 판정: 예보 green`·`- 판정: skip · …` 과 헤더 계수(base 4·p1 1/1·mid 6·imports 1/1/1)를 그대로 검사한다. P1 이 exit 5 문면의 «권고·비차단» 을 건드리면 red · P2 의 noblock 픽스처를 base 묶음 공용 리포트에 넣으면 헤더 4→5(exit 3 도 `write_report_stub` 로 헤더를 append 한다) | `workspace/tools/pregate_fixture_run.py:494,507,526,622,649,665-666,680` · `dddjango/scripts/design_pregate.py:1655-1660,1577-1592` |
| C-6 | **MAJOR** | manifest: `--check` 는 GROUPS 글롭 정의 자체를 봉인본과 대조한다 → P8(pipeline 글롭 +1) 뒤 `--write --draft` 재발행 없이는 verify-base-core red. 게다가 command md·codex SKILL(pipeline) · agents/skills md(plugin_payload) · `ontology/**`(graph) · rulepack.json(packs) · rulepack 골든(queries) · Makefile(protocol) · `manifest_seal.py`·`rulepack_smoke.py`·`query_golden_check.py`(harness) 전부 봉인 대상이라 **P1~P9 어느 하나만 건드려도 재봉인**이다 | `workspace/tools/manifest_seal.py:71-79,85-97,110-117,160-166,985-1002` · `Makefile:155-156` · 선례 `git show --stat f2450ad`(T2-0b-manifest.json 동반) |
| C-7 | MINOR | `design_pregate.py` 는 현재 **어느 봉인 그룹에도 없다**(T2-0b-manifest.json 내 `pregate` 0건) — P8 의 «등재» 는 사실과 정합. `pregate_fixture_run.py`·`gen_pregate_symbol_kinds.py`·`reverse_coverage.py` 도 봉인 밖 | `grep pregate workspace/eval/ab/T2-0b-manifest.json` = 0 · `manifest_seal.py:51-180` |
| C-8 | MINOR | 소성물 label 드리프트: rulepack 의 R-3433 label «관찰 모드 red 처분 …» · R-3436 label «pre-gate 구형 명세 skip 한정 … 차단 승격 시 폐지» — prefLabel 교체 + `make rulepack` 으로만 갱신(손편집 금지). rulepack 엔트리에 deontic 유형 필드는 없어 P5 유형 변경은 팩 형상에 무영향 | `dddjango/scripts/rulepack.json:60684,60719-60733` · `workspace/tools/ontology_rulepack.py:10` |
| C-9 | 검증됨 | 미러 상태: `design_pregate.py` Claude↔codex **byte 동일**(cmp) · scripts 디렉터리 `diff -rq` 차이 = `__pycache__` 뿐 · codex Coordinator 114행 = Claude 96행과 **3어절**(codex 병렬 정의 «spawn 전부 → wait 전 shell 1회»·«6번» vs «step 6»·조사 «이»)만 다름 · `commands/*.md` 는 corpus_mirror_sync 스코프 밖 → codex 는 손 미러 | `cmp` 결과 · `workspace/tools/corpus_mirror_sync.py:8,17` · 어절 diff(스크래치) |
| C-10 | 검증됨 | 병행 미머지 변경 없음: `main..HEAD` = 루브릭 1커밋 · `fix/field-typecheck` 는 main 에 머지됨(`88a65a0`, `main..fix/field-typecheck` 0) · `norm/*` 5 브랜치 전부 main 대비 0 ahead. 단 main 의 R-3442/3443@2026-09-03b 가 target-counts `ExpressionShape 3548` 의 현재 기준 | `git log --oneline main..HEAD` · `git branch -a` · `target-counts.json` |
| C-11 | 검증됨(표본 외) | kkebi-server `.dddjango/` 21 항목 = **런 20 + `violations/`**(루브릭 «21런» 은 디렉터리 수). design-spec.md 20/20 에 `<!-- machine: file-plan -->` **0** · `<!-- machine:` 마커 자체 0 · pregate-report.md 0 → 차단 전환 시 20/20 이 형식 red 로 선다(의도된 손실 — 설계 §5-6 성문) | `find ~/Desktop/kkebi-server/.dddjango -name design-spec.md` · §5 표 |
| C-12 | 판단 필요 | P5 «Exception→Prohibition» 유형 변경: `djr:deprecated` 사용 0(루브릭 «선례 0» 확인) · ISSUED 는 유형을 기록하지 않음(id·날짜·파일만) · SHACL 은 클래스별 shape 라 유형 변경이 게이트 위반은 아님 · wiring `delegatedTo` 유형 무관. **유형 변경 선례는 미확인**(grep 으로 판정 불가 — 저작 규약 `ontology-authoring.md` 에 «유형 변경» 조항 없음) | `grep -rn djr:deprecated ontology/rules` = 0 · `ontology/ISSUED:3436` · `djr-shapes.ttl:105-117` · `ontology/wiring/command-dddjango.ttl:681` |
| C-13 | MINOR | 러너에 **exit 4 를 기대하는 픽스처·도구는 0** — 픽스처 md 11/11 이 file-plan 블록 보유 · 러너 기대 exit ∈ {0,2,3,5} · 다른 도구(`rulepack_smoke`·`gen_pregate_symbol_kinds`·`reverse_coverage`·`registry_gate_smoke`) 에 `exit 4`/`returncode == 4` 0건 → P2 는 기존 하네스를 깨지 않되 **skip(exit 4) 경로는 하네스 무커버**(실체화 0·결손 0 skip 도 픽스처 없음 — imports-update-only 는 exit 5) | `grep -ln "machine: file-plan" workspace/eval/fixtures/pregate/*.md` = 11 · `pregate_fixture_run.py:8-37` |
| C-14 | MINOR | 문서·원장의 «관찰 모드» 잔존 중 **현행 규정으로 읽히는 것**: `ledger.md:4`(판정 규칙 «R-3433 rev3» → rev4 로) · `reverse_coverage.py:139`(why 문자열 «관찰 모드·G2 비대체») · 설계 v4 `§5-1:103`·`§5-6:108`·`§9-6/7:144-146`·`§10 M2:155`. 나머지는 역사 기록 | §1 표 |
| C-15 | 검증됨 | design-architect 쪽 무변경 정합: R-3431 블록 «채널에 없으면 부재로 전사(fail-closed) — 부재가 위반이면 red 가 정답» 은 P2 와 같은 방향 · R-3424~R-3431 enforcedBy `c/design_pregate.py`(Checker 개체 실재) · codex design-architect SKILL 81-86행 동형 | `agent-design-architect.ttl:2084-2089` · `wiring/agent-design-architect.ttl:478-500` · `wiring/registry.ttl:109` |
| C-16 | 검증됨 | 현재 트리 하네스 green: `pregate_fixture_run.py` **PASS**(10종+E 계열 6단계+유닛) · `make verify` — §3 하단 실측 참조 | 실행 출력 |

## 1. C1 — «관찰 모드 / observe / 권고·비차단 / 구형 명세 skip / 차단 승격 전까지» 문자열 전수

검색: `grep -rnE "관찰 모드|observe\b|권고·비차단|구형 명세|차단 승격|모드 관찰|MODE = "` (`.git`·`.venv`·`__pycache__` 제외). `observe` 영문 매치 중 `api_error_backstop_matrix.py:4276-4448`(픽스처 함수명 `observe`)·`query_golden_check.py:70,138`(함수명)·`docs/work_flow.html`(`ResizeObserver.observe`)·design-review-api·cleancode final.md 의 «observed/관찰된 shape» 는 **무관**(제외).

| 층 | 파일:행 | 문면 | 분류 |
|---|---|---|---|
| 정본(그래프) | `ontology/rules/command-dddjango.ttl:2826` | R-3433 prefLabel «관찰 모드 red 처분 — …» | **패키지가 바꿔야 함**(P3 — prefLabel 교체) |
| 정본 | `…:2868` | R-3436 prefLabel «pre-gate 구형 명세 skip 한정 … 차단 승격 시 폐지(«캐시 skip» 과 구별)» | **바꿔야 함**(P5) |
| 정본 | `…:3027` s002/b8 | «skip 행의 종류(캐시 skip·실체화 0·구형 명세)» | **바꿔야 함**(P7 — R-3438 amendment) |
| 정본 | `…:3053` s003/b10 | «구형 명세 skip 이면 `skip(구형 명세)`» | **바꿔야 함**(R-3437 — C-2, 루브릭 누락) |
| 정본 | `…:3274` s006/b9 | 제목 «(관찰 모드)» · «red 는 게이트 차단이 아니라 … **권고**이고(관찰 모드 — 차단 승격 전까지)» · «(관찰 모드의 유일한 추가 절차 의무)» · «**구형 명세 skip 한정** … 차단 모드 승격과 함께 이 skip 조항은 폐지된다» | **바꿔야 함**(P3·P5·P7 — 한 블록 안 4곳: 제목·권고 문장·«유일한 추가 절차 의무»·skip 조항. 루브릭은 앞 둘만 적시) |
| 투영물 | `dddjango/commands/dddjango.md:28,58,96` | 위 3 블록의 렌더 | 재투영으로만(직접 수정 금지 — graph-owned 11 마커) |
| 미러(손) | `codex-dddjango/skills/dddjango/SKILL.md:62,81,114` | 동일 3곳(114 는 codex 병렬 문면 3어절 보존) | **바꿔야 함**(P7 손 미러) |
| 소성물 | `dddjango/scripts/rulepack.json:60684,60729` + codex `…/scripts/rulepack.json` 동일행 | R-3433·R-3436 label | `make rulepack` 재소성(손편집 금지) |
| 실행기(byte 미러 2) | `dddjango/scripts/design_pregate.py:2`(docstring «(관찰 모드)») · `:73-74`(exit 4/5 사용문) · `:112`(`MODE = "observe"`) · `:1545,1589,1711`(헤더 «모드: 관찰({MODE})») · `:1704,1732`(«요약: … · 모드 관찰») · `:1662`(skip 사유 «구형 명세 한정 조항») | | **바꿔야 함**(P1·P2). `:58,1520,1699,1724` «권고·비차단» 은 exit 5 채널 문면 — **남김**(exit 5 비차단 유지 = R-2; 바꾸면 C-5 러너 red) |
| 하네스 | `workspace/tools/pregate_fixture_run.py:36,662,666,680` «권고·비차단» | exit 5 기대 문면 | 남김(exit 5 불변) — P1 이 실행기 문면을 유지하는 조건부 |
| 하네스 | `workspace/tools/reverse_coverage.py:139` «(관찰 모드·G2 비대체 — R-3432~R-3438)» | why 산문(검증 판정 무관) | 판단 필요 → 갱신 권고(봉인 밖 — 재봉인 불요) |
| 픽스처 | `workspace/eval/fixtures/pregate/imports-red-spec.md:5` «exit 5(권고·비차단)» | 픽스처 산문 | 남김 |
| 문서(설계 정본) | `workspace/design/2026-09-01-pregate-design.md:6,8,103,108,115,121,126,144-146,155` | «관찰 모드 우선»·§5-1 «관찰 모드 «권고» → 승격 후 «반송 의무»»·§5-6 «승격 시 skip 조항 폐지»·§9-6 «승격 릴리즈에서 pipeline 그룹 등재»·§10 M2 | §5-1·§5-6·§9-6·§9-7·M2 = **집행 추기(판단 필요 — P9 범위)** · 나머지 역사 |
| 문서(원장) | `workspace/eval/pregate-observe/ledger.md:1,3,4,139` | 제목 «관찰 모드 실측 대장»·판정 규칙(«R-3433 rev3»)·발견 ⑧ «차단 승격 시 filtered=반송 의무로 …» | L4 rev 번호 갱신 + L139 «P4 로 종결» 추기(P9) · 제목은 역사 |
| 문서(계획) | `2026-09-03-improvement-roadmap.md:19,37,43` · `2026-09-02-pregate-repair-plan.md`(§5 «관찰 모드 유지 — MODE 불변») · `2026-09-03-repair-batch-2-plan.md`(10) · `2026-09-03-repair-batch-3-rubric.md:51-84`(N-1 → R-1 이월) · `2026-09-01-pregate-ontology-plan.md` · `2026-09-01-pregate-backtest.md` · `2026-09-01-pipeline-speed-baseline.md` | 역사 기록 | 남김(로드맵 R-1 행만 P9 갱신) |
| 문서(리뷰 산출) | `workspace/eval/pregate-observe/reading-v21714/**`(11 파일) · `workspace/eval/field-report-typecheck/rv3/C.md` · `workspace/eval/2026-09-03-lane-duration-investigation.md` · `workspace/eval/t3/**`(4) | 역사 기록 | 남김 |
| 원장 | `ontology/LEDGER.tsv:1553-1557`(note 열) | 수리 배치 2 사유문 | 남김(append-only) |
| 조감도 | `workspace/design/ontology-adoption-map.html:639` «(속도 리비전·관찰 모드)» | 2026-09-01 행 | 남김 + 승격 행 추가(P9) |
| 라이브(표본 외) | `~/Desktop/spring_dream_server/.dddjango/*/pregate-report.md` 6 파일 헤더 «모드: 관찰(observe)» | 실런 기록 | 남김(발주측 산출물) |
| 무관 | `docs/work_flow.html`·`docs/work_flow.spec.json`·`README.md`·`dddjango/README.md` | pre-gate 언급 0 | 해당 없음 |

**드리프트 지점 요약(두 런타임이 다른 규범을 갖게 되는 곳)**: codex SKILL.md 62·81·114 는 어떤 검사기도 대조하지 않는다(render_sync 는 codex 미참조 · corpus_mirror_sync 는 final.md 11종 한정 · manifest pipeline 그룹은 «변경됐는가» 만) → 손 미러 누락 = 조용한 분기. 배치 체크리스트에 «codex 3곳(+G1′ 195·캐시 116 P6 결정 시) 어절 diff 첨부» 를 산출물로 요구할 것.

## 2. C2 — 리비전 레시피(이 배치 전용 · 단계별 · 누락 시 red 타깃)

전제: `.venv` 실재(`make ontology-env`) · 편집은 rdflib 구조 편집 + `ontology_canon.canon_turtle(...)` 재직렬화(왕복 byte 동일 선확인) · 모든 Expression IRI 는 `<전체 IRI>` 표기(`ontology-authoring.md:13,142`).

| 단계 | 작업 | 이 배치의 구체값 | 누락 시 red |
|---|---|---|---|
| 1 | 정본 편집 `ontology/rules/command-dddjango.ttl` — 새 Expression 노드 + Norm `currentExpression`·`prefLabel` 교체 + 블록 `djr:text` 교체 | **R-3433** `<…#R-3433@2026-09-03b>` rev **4** · wasRevisionOf `@2026-09-03` · revisionKind **redefinition**(P3) — 블록 s006/b9 · **R-3436** `@2026-09-03b` rev **3** · redefinition · (C-12 결정 시) `a djr:Exception`→`a djr:Prohibition` · **R-3438** `@2026-09-03b` rev **3** · amendment — s002/b8 · **R-3437** `@2026-09-03b` rev **3** · amendment — s003/b10(C-2) · **R-3432** `@2026-09-03b` rev **3** · amendment — 착지는 C-3 결정(ⓐ 면 신규 R-3444~ 채번 + s007 신규 블록 + wiring `delegatedTo` 행 + ISSUED append) · s006/b10 statesNorm 부착 여부(C-4) | verify-ontology 1/10(canon diff≠0·파스) · 3/10 SHACL(`ExpressionShape` revision/specializationOf 결손) · 10/11 structural ⑤(currentExpression 왕복 단절) · 7/10 ISSUED(ⓐ 채번 누락 시) |
| 2 | `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_gate.py` green | — | pre-commit 훅이 같은 4단으로 차단 |
| 3 | 재투영 `ontology_render.py --apply command-dddjango` | md 28·58·96(·98·s007 신규) 갱신 | verify-ontology 9/10 render_sync · pre-commit |
| 4 | LEDGER 재기준선 행 append(graph 절도 관례 — `LEDGER.tsv:1541-1556` 선례) | s002·s003·s006(+s007) 각 1행 «rebaseline:2026-09-03 승격 배치 …» | **red 아님**(`ontology_ledger_check.py:61` 은 prose 한정) — 관례 위반·감사 지적 대상 |
| 5 | `target-counts.json` | `ExpressionShape` 3548 → **3548+N**(N = 새 Expression 수: R-3432·3433·3436·3437·3438 = 5, C-3 ⓑ 선택 시 +1, ⓐ 선택 시 NormShape/WorkShape 3452→+1 도) | verify-ontology 4/10 hierarchy_check |
| 6 | q4 골든 `query-golden.json` | `distinct_works 3443` 은 **Work 수** 기준 — 리비전만이면 불변. C-3 ⓐ(채번) 시만 `query_golden_check.py --emit` | verify-ontology 11/11(채번 시) |
| 7 | `make rulepack` | R-3433/3436/3438/3437/3432 `expression` IRI·label 갱신 · `built_from` 재결속 · codex `scripts/rulepack.json` 은 scripts 디렉터리 byte 미러이므로 **복사 필수** | verify-base-core `ontology_rulepack.py --check` + 마지막 단 `diff -rq`(`Makefile:154,158`) · verify-base-regen `rulepack_smoke` |
| 8 | corpus_mirror_sync | **대상 아님** — `commands/*.md` 는 스코프 밖(`corpus_mirror_sync.py:17`) · 소스 미러 교체 불요 | (없음 — `--check` 그대로 green) |
| 9 | codex 손 미러 `codex-dddjango/skills/dddjango/SKILL.md` | 62(배너 1행 형식) · 81(s002/b8) · 114(s006/b9 — 3어절 codex 문면 보존) · (P6 착지에 따라 116/182-184/195) | **red 아님** — 검사기 없음 → 두 런타임 규범 분기(C1 요약) |
| 10 | 실행기 P1·P2 `dddjango/scripts/design_pregate.py` → `cp` codex 미러 | MODE·헤더·요약·docstring·exit 4 사유 → exit 3 분기 | verify-base-core `diff -rq` · manifest ③ «미러 파손»(`manifest_seal.py:1005-1007`) |
| 11 | 픽스처·러너 | `noblock-spec.md` 신설(exit 3) · 러너에 별도 리포트로 추가(공용 리포트면 헤더 계수 4→5 갱신) · 기존 문면 검사(`:665-666,680`) 유지 | verify-base-regen `pregate_fixture_run.py`(P2 후 기대 불일치 시 exit 1) |
| 12 | manifest `manifest_seal.py` GROUPS.pipeline += `dddjango/scripts/design_pregate.py` → `python3 workspace/tools/manifest_seal.py --write --draft` | T2-0b-manifest.json 재발행(pipeline·plugin_payload·graph·packs·queries·protocol·harness 전부 갱신) | verify-base-core `--check --draft` exit 2(`manifest_seal.py:985-988` «글롭 정의가 봉인본과 다르다» · «봉인 후 변경») |
| 13 | 기록(P9) | 설계 v4 §5-6/§8/§9-6 집행 추기 · `ledger.md:4` «R-3433 rev3»→rev4 · «승격 집행» 절 · 로드맵 R-1 · 조감도 행 · `reverse_coverage.py:139` | red 아님 |
| 14 | `make verify` 6/6 green · rulepack 변경 커밋이므로 `make verify-mutation` 권장(DEVELOPMENT §5) | — | — |

## 3. C3 — 실행기 변경(P1·P2)이 깨뜨릴 수 있는 하네스

| 하네스 | 고정 지점(파일:행) | P1(모드 문면) 영향 | P2(블록 부재 → exit 3) 영향 |
|---|---|---|---|
| `pregate_fixture_run.py` 헤더 계수 `_header_count`(`## pre-gate 예보` 수) | `:494` base=4 · `:507,526` p1=1/1 · `:622` mid=6 · `:649,668,682` imports=1/1/1 | 없음(헤더 문자열 «## pre-gate 예보 —» 불변 조건) | noblock 을 base 공용 리포트에 넣으면 4→5(exit 3 경로도 `write_report_stub` → 헤더 append `design_pregate.py:1655-1660,1586`) — 별도 리포트 권장 |
| exit 기대 | `:468`(0) `:475`(3) `:483`(2) `:502`(0) `:516`(2) `:556-598`(E1~E4 0/0/3/3) `:615`(2·2) `:645`(0) `:660`(5) `:674`(5) | 없음 | 기존 기대 무영향(exit 4 기대 0건) |
| 리포트 stub·본문 문면 | `:649` «### 계약 실존 (boundary-imports 3단 · 결손 0건» · `:665` «- 판정: 예보 green» · `:666` «계약 실존 결손 3건(권고·비차단)» · `:680` «- 판정: skip · 계약 실존 결손 1건(권고·비차단)» | **exit 5 채널의 «(권고·비차단)» 을 바꾸면 red** — P1 은 «모드» 문면만 바꿔야 함 | 없음 |
| stdout 요약 | `:645` «요약: 귀속 0건 · 실존 결손 0건» · `:660` «… 실존 결손 3건» · `:674` «요약: 실체화 0 · 실존 결손 1건» — 접두 부분일치 | «· 모드 관찰»→«· 모드 차단» 교체 무해 | 없음 |
| 블록 해시 스탬프 | `:98 _BLOCK_HASH_RE` · `:509` | 없음 | 없음 |
| 집계·귀속 정규식 | `:86-97`(`_FORECAST_RULE_RE`·`_EXISTENCE_*`·`_DOMAIN_MODEL_ROW_RE`) | 없음 | 없음 |
| `reverse_coverage.py` | `:136-140` design_pregate.py 존재 + why 문자열 | 없음(산문) | 없음 |
| `rulepack_smoke.py` | `:88` roster 상수 `{"design_pregate.py"}` | 없음 | 없음 |
| `gen_pregate_symbol_kinds.py --check` | 검사기 소스 추출 → `pregate_symbol_kinds.json`(design_pregate.py 미참조 — grep 0) | 없음 | 없음 |
| `registry_gate_smoke`·`anchor_diff_smoke` | pregate 미참조 | 없음 | 없음 |
| **exit 4 기대 픽스처/도구 실측** | 픽스처 md 11/11 file-plan 블록 보유 · `grep "exit 4\|return 4\|returncode == 4"` workspace/tools = 0 | — | **0건** — 단 skip 경로(exit 4: 실체화 0·결손 0) 자체가 픽스처 무커버 |
| 현재 트리 실측 | `PYTHONUTF8=1 python3 workspace/tools/pregate_fixture_run.py` → **PASS — pre-gate 픽스처 10종+E 계열 6단계+유닛 기대 일치** | — | — |
| `make verify`(현재 트리) | **6/6 green**(178s — web 28s·base-core 52s·ontology 69s·backstop 98s·regen 129s·cross 178s) | — | — |

## 4. C4 — P6 의 Coordinator 문면 위치와 R-3437 관계

| 대상 | 그래프 블록 | statesNorm(소유 규범) | md 투영 행(Claude / codex) | P6 와의 관계 |
|---|---|---|---|---|
| Phase 2 step 6 결정적 백스톱(registry_gate 실행) | s007/b12 | R-0301~R-0310 | 114 / 131 | P6 «슬라이스 dispatch 전 `--base` 재발화 선행» 은 이 블록이 아니라 Phase 2 진입·반송 경로(s009/b3·s007 Contract mismatch)의 문면 |
| Phase 2 step 7 G2 배너 | s007/b57 | R-0406~R-0411(R-0411 = «…잔존 시 G2 제시 금지(legacy 잔존은 별도 보고 항목)») | 165 / 182 | «pre-gate 최신성 1행» 의 자연 착지 — R-0411 amendment 또는 신규 규범 |
| G2 배너 «승인 유입 N건» 별도 항목 | s007/b58 | **R-3440·R-3441**(2026-09-03 신규 채번 + 신규 블록) | 167 / 184 | **선례**: G2 배너 항목 추가 = 신규 규범+신규 블록. R-3440 amendment 로 «최신성 1행» 을 병기하는 길도 있음 |
| G1′ 재승인(수정 모드) | s009/b3 | R-0418~R-0421 | 180 / 195 | 이미 «Phase 2 중이면 재발화 판형: `--base <G1 기준선 SHA>`» 성문 — P6 첫 문장의 중복 위험(정합 개정·설계 진화 경로는 여기 없음) |
| Phase 1 pre-gate 문단(관찰 모드 제목) | s006/b9 | R-3432·R-3433·R-3434·R-3435·R-3436 | 96 / 114 | R-3432 의 유일한 statesNorm 블록 — G2 배너 문면을 여기에 두면 Phase 1 절이 Phase 2 배너 의무를 진술하는 배치 드리프트 |
| 캐시 skip·재발화 판형 | s006/b10 | **없음**(C-4) | 98 / 116 | P6 해시 대조 = 이 블록의 «skip 조건은 `--block-hash` 동일 시뿐» 규칙을 G2 시점에 재적용하는 것 → **모순 없음**(질문 B), 그러나 규범 무연결 블록 |
| G1/G1′ 배너 pre-gate 1행 형식 | s003/b10 | R-0151~R-0157, **R-3437** | 58 / 62 | R-3437 은 명시적으로 **G1/G1′** 한정(prefLabel `:2882`). P6 의 «G2 배너 1행» 은 R-3437 범위 밖 → R-3437 을 G2 로 확장(rev3)하거나 신규 규범. P3 의 «red N건 · 처분 전건 기재» 병기·P2 의 `skip(구형 명세)` 삭제는 R-3437 필수 개정(C-2) |

관측 근거 재현(표본 외 축, 라이브 읽기): `~/Desktop/spring_dream_server/.dddjango/20260903-1214-fortune-catalog/pregate-report.md` 헤더 4개(03:59Z·04:24Z·04:33Z·04:42Z) 블록 해시 `d759829e35d6→05e1a2244b95→6d58c244a8d5→6cf8e2ffdfc3`, 마지막 이후 skip 행·재실행 0 · 현재 design-spec `--block-hash` = **`cb95a1bddb32`** ≠ 마지막 헤더 `6cf8e2ffdfc3` → 루브릭 P6 관측(재실행 0·해시 불일치) **재현됨**.

## 5. C5 — 표본 외(kkebi-server) 대조

| 항목 | 실측 | 근거 |
|---|---|---|
| 런 수 | `.dddjango/` 항목 21 = 런 폴더 **20** + `violations/` | `ls ~/Desktop/kkebi-server/.dddjango` |
| design-spec.md 보유 | 20/20 | `find … -name design-spec.md` |
| `<!-- machine: file-plan -->` 보유 | **0/20** | `grep -l 'machine: file-plan'` |
| `<!-- machine:` 마커 어떤 종류든 | 0/20 | 동일 |
| pregate-report.md | 0 | `find … -name pregate-report.md` |
| 현행(관찰 모드) 첫 메시지 — exit 4 | `skip — machine 블록 부재(<!-- machine: file-plan --> 없음): 구형 명세 한정 조항` (stdout + 리포트 stub `- 판정: skip`) | `dddjango/scripts/design_pregate.py:1662-1665` |
| 배너에 실리는 문면(R-3437 현행) | `skip(구형 명세)` | `command-dddjango.ttl:3053` |
| P2 후 첫 메시지 — exit 3 경로 | 현행 형식 red 프레임: `형식 red — {n}건 (기계 블록이 규범 문법 밖이다 · architect 반송 재료):` + 오류 행(초안 문면 «machine 블록 부재 — 차단 모드: 블록 의무») · 리포트 stub `- 판정: 형식 red` | `design_pregate.py:1655-1660` · 루브릭 P2. **주의**: 프레임 문장 «규범 문법 밖» 은 «블록 부재» 에 의미상 어긋남 — 부재 전용 문면 권고 |
| 영향 | 차단 전환 시 kkebi 형(구형 명세 재발주) 20/20 이 G1 전 형식 red → architect 반송(블록 5종 작성 의무) — 설계 v4 §5-6 «승격 시 폐지·신규·개정 명세는 블록 의무» 성문과 일치 = **의도된 손실**. 단 «형식 반송 ≤1/레인» 계수(§8 ⑶)에 이 반송을 어떻게 계상할지 미성문(판단 필요 — 승격 후 계수 규칙) | `2026-09-01-pregate-design.md:108,134` |

## 6. C6 — 병행 미머지 변경과의 충돌

| 항목 | 실측 | 판정 |
|---|---|---|
| `git log main..HEAD` | `399796a` 루브릭 1커밋(파일 1) | 충돌 없음 |
| `fix/field-typecheck` | `main..fix/field-typecheck` 0 · merge-base `4699d7e` · main `88a65a0` 에 머지됨 | 이미 머지 — 충돌 없음. 단 그 머지가 `target-counts.ExpressionShape=3548`·`architecture-ddd-final.ttl` 의 `@2026-09-03b` 선례를 남김 |
| `norm/pregate`·`norm/pregate-repair`·`norm/repair-batch-2`·`norm/revision-10`·`norm/slot-promotion` | 전부 main 대비 0 ahead | 잔여 브랜치(정리 대상) — 충돌 없음 |
| 수리 배치 3(보류) | N-1(filtered 근거 유형) 은 «R-1 이월» 로 종결(`repair-batch-3-rubric.md:80,84`) — 본 배치 P4 가 그 이월분 | 중복 아님 — P4 반영 시 배치 3 루브릭에 «P4 로 집행» 역참조 추기 |
| 봉인본 | `T2-0b-manifest.json` status PENDING(draft) · cache_parity «drift»(claude 3·codex 1 mismatch — v2.17.16 설치본 vs main 의 typecheck 수리 후 트리) | 릴리즈 보류 상태의 정상 드리프트 — 배치와 무관, 재봉인 시 함께 갱신됨 |

## 7. 실행 실측

- `PYTHONUTF8=1 python3 workspace/tools/pregate_fixture_run.py` → **PASS**(현재 트리 · 2026-09-03).
- `make verify` → **6/6 green**(178초 · 로그 `/tmp/djr-verify.lOiKY7`) — 승격 배치 착수 전 기준선 green 확인.
- `cmp dddjango/scripts/design_pregate.py codex-dddjango/skills/dddjango/scripts/design_pregate.py` → 동일.
- `(cd ~/Desktop/spring_dream_server && python3 …/design_pregate.py <catalog>/design-spec.md . --block-hash)` → `블록 해시 cb95a1bddb32`.

## ④ 반영 목록 (계획 ② 에 넣어야 할 것)

1. **[C-1]** 패키지 표의 리비전 번호·IRI 정정: R-3433 rev4 · R-3436 rev3 · R-3438 rev3 · R-3437 rev3 · R-3432 rev3 — 전부 `@2026-09-03b`.
2. **[C-2]** R-3437 을 «검토» 에서 **개정 확정** 으로: `skip(구형 명세)` 분기 삭제 + P3 의 «red N건 · 처분 전건 기재» 형식 + (P6 결정에 따라) G2 확장.
3. **[C-3]** P6 착지 결정 게이트 항목 신설: ⓐ 신규 채번+s007 신규 블록(선례 b58) / ⓑ R-0411 또는 R-3440 amendment / ⓒ R-3437 G2 확장 — R-3432 단독 amendment 는 불가(규범↔블록 1:1).
4. **[C-4]** s006/b10 `statesNorm djr:R-3432` 부착(또는 부착하지 않는 사유 기록) — 같은 커밋에서 rulepack `R-3432.block` 변동 확인.
5. **[C-5]** P1 문면 범위를 «모드 문면 5곳(`:2,112,1545,1589,1704,1711,1732`) + docstring exit 4 설명(`:73`)» 으로 한정하고 exit 5 «(권고·비차단)» 은 불변으로 명시 · P2 픽스처는 별도 리포트 파일로(헤더 계수 불변) 또는 base 계수 4→5 갱신을 명시.
6. **[C-6·C-7]** P8 을 «GROUPS.pipeline += design_pregate.py → `manifest_seal.py --write --draft`» 로 구체화하고, 배치 마지막 커밋에 재봉인 동반을 체크리스트화.
7. **[C-8]** P3·P5 에 prefLabel 교체 문면 초안 포함(rulepack label 이 곧 C암 «명칭» — 관찰 모드 잔존 금지).
8. **[C-9·C1]** codex 손 미러 3곳(62·81·114)+(P6 착지) 어절 diff 를 ④ 산출물로 요구 — 병렬 정의 3어절 보존 조건.
9. **[C-12]** P5 유형 변경(Exception→Prohibition) 선례 미확인 — 계획 ② 에서 «유형 유지·redefinition 만» 대안과 비교해 결정.
10. **[C-13]** exit 4(실체화 0·결손 0 skip) 경로 픽스처 부재를 이월 항목으로 등재(승격 후 skip 경로는 캐시 skip 과 함께 계수 대상).
11. **[C-14]** P9 에 `ledger.md:4` rev 번호·`reverse_coverage.py:139`·설계 v4 §5-6/§8/§9-6 집행 추기를 명시.
12. **[C-11·C5]** 승격 후 «형식 반송 ≤1/레인» 계수에 구형 명세 블록 부재 반송의 계상 규칙(별도 계수 권고)을 P3/P9 문면에 추가.
