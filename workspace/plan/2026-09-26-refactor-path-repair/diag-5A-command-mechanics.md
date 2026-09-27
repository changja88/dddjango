# 진단 5A — 리팩토링 커맨드를 더하는 기계적 연쇄와 모양 선택 (2026-09-27)

범위: 로드맵 5(결정 1 — `evening-report.md` §5) 중 «커맨드를 어떤 모양으로 더하고, 그러면 무엇이 연쇄로 바뀌는가». 리뷰어 «BC 전체 점검 모드»의 내용은 5B, 약한 단언은 5C 소관이다.
방법: 읽기 전용 조사 + scratch 사본 실험(`/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/diag5a/` — `repo/` 사본 · `plug/` 사본 · `expA.py` · `verify-ontology-*.log`). 원본 저장소는 이 파일 말고 쓰지 않았다. Serena·Graphify 미사용(지시).
표기: **[실측]** = 파일·명령 결과로 확인 · **[추정]** = 확인하지 않은 판단.

## 권고

**(B) 얇은 전용 입구 + Coordinator 안의 «리팩토링 모드» 새 절(graph).** 결정 1 의 «전용 커맨드» 문언을 지키면서 Phase 0~3 규범(Coordinator 56,189 토큰)을 한 곳에만 두고, 새 문서 키 연쇄와 쌍 개정 비용을 피한다.

- 입구 = `dddjango/commands/refactor.md`(`/dddjango:refactor`) — `disable-model-invocation: true` · 규범 없는 산문 · 본문은 «Skill 도구로 `dddjango:dddjango` 를 불러 리팩토링 모드로 작동하라 — 대상: `$ARGUMENTS`» 수준. Coordinator 를 **Read 로 읽게 하지 않는다**: Read 한 번에 1~83행만 보이고(56,189 토큰 > 상한 25,000), `$ARGUMENTS`·`${CLAUDE_PLUGIN_ROOT}` 가 치환되지 않는다 **[실측]**.
- 입구 파일은 corpus-manifest 1행과 LEDGER prose 행으로 해시를 보호한다(verify-ontology green · 무단 편집 red **[실측]**). Codex 는 얇은 스킬 `dddjango-refactor`.
- 추정 작업량 **[추정]**: 5A 몫(커맨드 기계 연쇄)은 약 0.5 작업일이다. 로드맵 5 전체는 규범 저작, 리뷰어 모드, 행동 시험까지 약 4~6 작업일이고 5B·5C 결과에 따라 달라진다. A 는 5A 몫이 1~1.5일 더 든다. A 를 자립형으로 만들면 이후 Coordinator 를 개정할 때마다 쌍으로 개정해야 한다(Coordinator 정본은 08-22 이후 커밋 22회 · 09-01 이후 18회 **[실측]**). C 는 B 보다 약 0.3일 싸지만 결정 1 문언에 맞지 않는다.

## 0. 핵심 실측

| # | 확인한 것 | 결과 |
|---|---|---|
| 1 | 커맨드 등록 방식 | `dddjango/.claude-plugin/plugin.json` 에 `commands` 필드 없음 → `commands/*.md` 자동 발견. Codex 는 커맨드 개념이 없고 `codex-dddjango/.codex-plugin/plugin.json` 의 `"skills": "./skills/"` 로 스킬 폴더를 자동 발견 |
| 2 | `claude plugin validate --strict`(2.1.282) | 새 커맨드를 더해도 green. **YAML 이 깨진 커맨드 파일을 넣어도 green**이다(`--json` 의 `contents: []`). 커맨드 파일은 이 검증의 보증 밖이다 |
| 3 | manifest 에 없는 새 산문 커맨드 | ledger·render_sync·reverse_coverage·corpus_lint 가 전부 green 이다. corpus_lint 대상은 여전히 «md 30»이고, `manifest_seal --check --draft` 출력은 추가 전과 byte 동일하다. **red 는 0 이지만 보호도 0** 이다(훅·봉인·린트 어디에도 잡히지 않는다) |
| 4 | manifest 1행 + LEDGER prose 행(새 산문 커맨드) | `make verify-ontology` 11단 green(73초). 입구 파일을 무단 편집하면 `ontology_ledger_check` 가 exit 2(«미이관 절 부식») |
| 5 | 새 그래프 문서 키(A) — rules/wiring ttl + registry Agent + ISSUED + `render --apply` + LEDGER graph 행 | verify-ontology red 는 두 곳뿐이다. hierarchy 계수 5종(Section +3 · Block +3 · Work/Norm/Expression +1)과 query-golden q4(+1)다. 둘을 갱신하면 green 이다. 그다음 `ontology_rulepack --check` 가 red 이고 `make rulepack` 뒤 green 이다. gate·SHACL·meta·골든 23·gate-smoke·ISSUED·ledger·render_sync·structural·paths 는 무변경으로 통과했다 |
| 6 | Read 상한 | 이 세션 하네스의 Read 도구로 `dddjango/commands/dddjango.md` 를 읽으면 «56189 tokens, cap 25000 · lines 1-83 of 220» 이 나온다 — 전문을 보려면 3쪽 이상 읽어야 한다. 10행 `빌드할 기능: $ARGUMENTS` 는 문자 그대로 보인다. 사용자 Claude Code 판의 상한 값은 확인하지 않았다 |
| 7 | 커맨드의 모델 호출 가능성 | 이 세션의 Skill 목록에 `dddjango:dddjango` 가 있다(`dddjango.md` 에 `disable-model-invocation` 없음). `dddjango-web:dddjango-web` 은 없다(`dddjango-web.md:5` `disable-model-invocation: true`) |
| 8 | 새 문서 키 선례 | **없음**. `ontology/rules/*.ttl` 을 추가한 커밋은 T1·T3 이관 4건뿐이다(`ceb3c6a4` · `fe1057c7` · `71bdc810` · `148911d9` — 전부 기존 산문 md 이관). 새 **절**을 추가한 선례는 있다: `56b27e12`(implementation-django §18 `s094-18` — `workspace/eval/field-report-3/evidence/impl/piece1_ontology.py` + `ontlib.new_section`, SectionShape 545→546) |
| 9 | 커맨드가 다른 커맨드 파일을 따르는 선례 | 이 저장소·dddart·dddjango-web 에는 없다(각 커맨드 1개). 공식 플러그인에는 있다: `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/code-modernization/commands/modernize.md:63` «read `${CLAUDE_PLUGIN_ROOT}/commands/modernize-preflight.md` and carry it out with those arguments as if they had typed it». 커맨드→Skill 도구 위임 선례: `…/plugins/hookify/commands/hookify.md:9`(스킬 적재). Codex 의 스킬→스킬 적재 관용구는 `codex-dddjango/skills/dddjango/SKILL.md:24` |

새 문서 키의 최소 절차 **[실측 — scratch 한 번 통과 · 선례 아님]**:

1. md 초안을 쓴다(절 헤딩 · frontmatter는 `---` 헤딩의 `s001` 절이 된다).
2. `corpus-manifest.tsv` 에 1행을 추가한다.
3. `ontlib` 식 rdflib 스크립트로 `rules/<키>.ttl` 을 쓴다. 들어가는 것은 Document · Section(headingSnapshot · owner-graph · inDocument) · Block(verbatim) · Work/Expression 이다.
4. `wiring/<키>.ttl` 에 delegatedTo·enforcedBy 를 쓰고, `wiring/registry.ttl` 에 Agent 를 손으로 추가한다.
5. ISSUED 를 append 한다.
6. `ontology_render.py --apply <키>` 를 돌린다(마커가 삽입되고, frontmatter 안 마커는 기존 커맨드와 같은 모양이 된다).
7. LEDGER graph 행을 절 수만큼 append 한다.
8. `target-counts.json` 과 `query-golden.json` q4 를 갱신한다.
9. `make rulepack` 을 돌린다.

`ontology_migrate.py` 경로는 권하지 않는다. 동결 센서스 `sections.tsv` 행이 있어야 하고(68~74·124~131행), `--emit-registry` 는 `check-*.py` 만 glob 한다(244행). 그래서 registry 에 있는 `behavior_guard.py`·`design_pregate.py` 개체 2개를 떨어뜨린다 **[실측: registry Checker 29 · check-*.py 27]**.

## 1. 연쇄 표

선택지:
- **A** = 새 커맨드 파일 + 새 그래프 문서 키. 두 형태가 있다: A1 자립(Phase 0~3 을 재진술) · A2 Phase R 만 소유하고 Coordinator 에 위임.
- **B** = 얇은 산문 입구 + Coordinator 새 절.
- **C** = 새 커맨드 없이 `/dddjango` 안의 모드.

표기: 필수 · 권장 · 선택 · —(불필요).

| 파일·도구 | 왜 (근거) | A | B | C |
|---|---|---|---|---|
| `dddjango/commands/<새>.md` | 새 입구 | 필수(graph 투영) | 필수(산문 · 규범 0) | — |
| `dddjango/.claude-plugin/plugin.json` | commands 자동 발견 [실측] | — | — | — |
| `.claude-plugin/marketplace.json` · `.agents/plugins/marketplace.json` | 플러그인 단위 등재 | — | — | — |
| `codex-dddjango/skills/dddjango-<새>/SKILL.md` | Codex 에는 커맨드가 없어 스킬로 입구를 만든다. `dddjango-` 접두는 형제 dddart 와의 전역 이름 충돌 회피 관례다(`corpus_mirror_sync.py:111-113`) | 필수(A1 이면 대형 의미 미러) | 필수(얇음) | — |
| `codex-dddjango/.codex-plugin/plugin.json` `defaultPrompt` | 선택. 넣으면 독립 토큰 `dddjango` 가 있어야 한다(`request_guide_contract.py:129` — `dddjango-refactor` 만으로는 불합격) | 선택 | 선택 | 선택 |
| `codex-dddjango/skills/dddjango/SKILL.md` | Coordinator 의미 미러(아래 hook 동반) | 필수 | 필수 | 필수 |
| `workspace/design/2026-08-19-ontology-t1-census/corpus-manifest.tsv` | render·ledger·migrate 의 문서 키 정본(`ontology_render.py:25-33` · `ontology_ledger_check.py:36-45`) | 필수 | 권장(산문 등재 = 해시 보호 · manifest 에만 있고 ttl 이 없는 첫 문서) | — |
| `ontology/rules/command-<새>.ttl` · `ontology/wiring/command-<새>.ttl` | 새 문서 정본 | 필수 | — | — |
| `ontology/rules/command-dddjango.ttl`(+wiring) | hook: s004 모드 판별(`dddjango.md:67`) · s005 «리팩터링 대상 = 백스톱 위반» 정의(79) · 결과 표 형식(80) · 정리할 것 없음(84) · s006 비위반 이동 STOP(106) · s007 5번 감사 입력(117) · 7번 ⓐ 잔존 산식(174) | 필수(hook) | 필수(hook + «리팩토링 모드» 새 절) | 필수(hook + 새 절) |
| `ontology/wiring/registry.ttl` | 새 커맨드에 delegatedTo 하면 `a/command-<새>` Agent 가 필요하다. 손 편집(`--emit-registry` 금지 — 위) | 필수 | — | — |
| `workspace/tools/ontology_migrate.py` `AGENTS`(232-234) | 재방출 경로를 쓸 때만 | 선택 | — | — |
| `ontology/ISSUED` | 새 규범 채번 | 필수 | 필수 | 필수 |
| `ontology/LEDGER.tsv` | 절 기준선 | 필수(새 문서 절 전부 graph 행 + 개정 절) | 필수(개정 절 + 입구 prose 행) | 필수(개정 절) |
| `workspace/eval/fixtures/ontology_gate/target-counts.json` | 계층 계수 회귀 [실측 red] | 필수 | 필수 | 필수 |
| `workspace/eval/fixtures/rulepack/query-golden.json` q4 | 새 Work 가 있으면 +n [실측 red] | 필수 | 필수 | 필수 |
| `dddjango/scripts/rulepack.json` ×2(`make rulepack`) | `built_from` 해시 [실측 red] | 필수 | 필수 | 필수 |
| `ontology_render.py --apply` | 투영 | 새 키 + command-dddjango | command-dddjango(+에이전트) | 동일 |
| `workspace/tools/section-path-map.tsv` · `paths.ttl` · `derive_path_globs` | final.md 절↔트리 행 전용 [실측 green] | — | — | — |
| `ontology_census`·`sections.tsv` | migrate 경로를 쓸 때만 | 선택 | — | — |
| `workspace/hooks/pre-commit` | 코드는 바뀌지 않는다. 대상은 ttl 스테이지 → 게이트, `dddjango/(skills\|agents\|commands)/*.md` → ledger_check(7-17행) | 자동 | 자동(등재 시에만 입구가 시야에 든다) | 자동 |
| `ontology_render_sync.py` | rules/*.ttl 기준으로 순회하고, manifest 에 없으면 exit 2(90-93행) | 자동 | 자동(산문 입구는 대상 밖 — 정상) | 자동 |
| `workspace/tools/manifest_seal.py` `pipeline` 글롭 | `dddjango/commands/dddjango.md` 가 고정이다(71-85행). 확장하지 않으면 새 커맨드는 봉인 밖이다 [실측: 출력 동일]. Codex 새 스킬은 `plugin_payload` 의 `codex-dddjango/skills/**/*.md`(96행)로 자동 포함 → 봉인 재발행 chore | 필수 | 필수 | 재발행만 |
| `workspace/tools/corpus_lint.py` `collect_docs`·`is_normative` | `commands/dddjango.md` 고정(57-85행). 수정하지 않으면 린트 밖 [실측 «md 30» 불변] | 권장 | 권장 | — |
| `workspace/tools/runtime_parity_check.py` | 대조 절은 step 6′ 하나(21-28행) | 권장(두 Coordinator 대조) | 선택 | — |
| `workspace/tools/reverse_coverage.py` | `commands/*` 는 일괄 «flow 정본»(172-173행)이라 자동 green [실측] | 설명 분기 선택 | 설명 분기 선택 | — |
| `workspace/tools/anchor_integrity_check.py` | commands/*.md 는 glob 자동이고 Codex 역할 튜플은 고정(242-255행). `make verify` 밖 | 선택 | 선택 | — |
| `corpus_mirror_sync.py` · `request_guide_contract.py` | commands·SKILL 면제(17행) · 커맨드 무관 | — | — | — |
| `checker_lint.py:286` · `field_report_checker_smoke.py:915` | Coordinator 문구 존재 검사 — Coordinator 개정 때 유지 확인 | 확인 | 확인 | 확인 |
| `Makefile` release·verify | release 는 manifest version 2곳만 바꾸고(277-290), verify 목록도 바뀌지 않는다 | — | — | — |
| `dddjango/REQUEST_GUIDE.md` ↔ `codex-dddjango/REQUEST_GUIDE.md`(byte 미러 — verify-base-core `cmp`) | §2 시작 문법(23-56행)을 바꾸고, §6 정리 문단(163-176)도 바꾼다. 173행 «표준 위반이 아닌 기존 코드를 … 지금은 하지 않으며»가 결정 1 과 충돌한다 | 필수 | 필수 | 필수 |
| `README.md` | 303행 «커맨드 1개: `/dddjango:dddjango`» · 5·107·120행 사용 예 | 필수 | 필수 | 선택 |
| `AGENTS.md:21·28` · `docs/DEVELOPMENT.md:13` | «30 문서 키» · 커맨드 목록 | 필수(31) | 권장(21행 목록만) | — |
| `docs/work_flow.html` · `workspace/design/ontology-adoption-map.html` | 파이프라인 지도 · 조감도 상시 갱신 지침. `docs/master.html` 은 사용자 미커밋 변경이라 손대지 않는다 | 필수 | 필수 | 필수 |
| 공통 — `agent-discipline-reviewer` · `agent-design-review-ddd`(±api·db) · `agent-design-architect` ttl+wiring+render md + Codex 역할 SKILL 4~5 | 결정 1-b 의 전체 점검·판정 모드(5B) | 필수 | 필수 | 필수 |

5A 고유 파일 수(공통 에이전트 작업 제외 · 문서 포함) **[실측 목록 기준 계수]**:

| 선택지 | 새 파일 | 수정 파일 | 합 | 비고 |
|---|---|---|---|---|
| A | 4(md · rules · wiring · Codex 스킬) | 약 17 | 약 21 | — |
| B | 2(md · Codex 스킬) | 약 14 | 약 16 | 그중 ttl 계열 6개는 hook 작업과 공유 |
| C | 0 | 약 11 | 약 11 | — |

## 2. 선택지 비교

| 축 | A 새 커맨드 + 새 그래프 문서 키 | B 얇은 입구 + Coordinator 새 절 | C `/dddjango` 안의 모드 |
|---|---|---|---|
| 결정 1 «전용 커맨드» | 합치 | 합치 — 입구가 유일한 트리거다(Phase R 은 입구 표지가 있을 때만 켜진다) | **불합치**. 사용자 원문은 «리팩토링 이라는 명시적인 커맨드를 만들어서»다. 인자 플래그(`--refactor`)면 △. 요청문으로 판별하면 `dddjango.md:67` «모드 지정은 판별 입력이 아니다»를 뚫어야 한다 |
| 그래프 영향 | 문서 키 30→31 · Agent 8→9 · 새 문서 절 전부 · A1 이면 Coordinator 전 절 재진술(`djr:restates`) | 문서 키 무변 · command-dddjango 절 +1(새 절 선례 `56b27e12`) · 입구는 manifest prose 행만 | B 와 같음(입구 행 없음) |
| 런타임 위험 | A1 은 위임 위험이 0 이지만 두 Coordinator 가 표류한다. A2 는 B 와 같은 위임 위험이 있다 | 입구가 Coordinator 를 불러와야 한다. **B-2 Skill 위임**: 하네스가 `$ARGUMENTS` 를 치환하고 `dddjango:dddjango` 는 모델 호출이 가능하다 [실측 7]. 다만 중첩 확장 시 `allowed-tools` 적용 여부는 [추정] — 행동 시험이 필요하다. **B-1 Read 위임**: 3쪽 이상 부분 읽기와 변수 미치환 [실측 6]이 있지만 공식 선례가 있다(`modernize.md:63`) → 대체 경로로만 둔다 | 위임 없음. 대신 모드 오발화(자연어 «정리해줘»로 켜짐) 위험이 있다 |
| 기능 실행의 컨텍스트 | A2 는 Phase R 을 기능 실행이 싣지 않는다(장점) | `/dddjango` 실행마다 Phase R 절도 실린다. 56K 토큰 위에 약 3~6K(+5~10%) [추정] | B 와 같음 |
| Codex 대응 | 새 스킬 `dddjango-refactor`. A1 은 125KB 급 의미 미러 2벌 | 얇은 스킬(«스킬 `dddjango` 를 로드해 리팩토링 모드로» — `SKILL.md:24` 관용구). `SKILL.md:22` «세션 시작에 이미 로드돼 있다» 문면은 입구 경유를 예외로 적어야 한다. Codex 의 스킬 명시 호출(`$스킬명`) 방식은 [추정] | 스킬 설명·본문의 모드 문면만 |
| 규범 중복·유지보수 | A1 은 Coordinator 개정마다 쌍 개정이다(×2 런타임 — 36일 22커밋 [실측]). A2 는 Phase R 과 Phase 0 3~4번이 문서를 가로질러 참조되어, 절 이름이 바뀌면 조용히 끊긴다(교차 참조 검사가 verify 밖) | 없음. Phase R·hook·Phase 0 이 한 문서에 있다 | 없음 |
| 5A 몫 작업량 [추정] | 1.5~2일(A2) · A1 은 3일 이상 + 지속 비용 | 0.5일 | 0.2일 |

A2(Phase R 을 새 문서 키가 소유)는 차선이다. 기능 실행의 컨텍스트를 아낀다는 이점이 있다. 그러나 G2 잔존 산식과 STOP 예외는 어차피 Coordinator(Phase 1·2)에 있어야 하므로 리팩토링 규범이 두 문서로 갈라진다. 게다가 새 문서 키 연쇄가 1회 더 든다.

## 3. Coordinator 재사용 지점

| Coordinator 절(키 · 행) | 리팩토링 실행에서 | 판정 |
|---|---|---|
| 모드 판별 s004(67) | 입구 표지를 판별 입력으로 인정한다. 이 표지는 점검을 «더하기»만 하고, G0·빚 스캔 생략 지시를 따르지 않는다는 규칙은 그대로다. `/dddjango` 로 들어온 «정리 요청»의 처리는 §5-1 | 개정 |
| Phase 0 1·2번(72-78) | 스코프 메모 = 대상 BC + (선택) 사용자 항목 + «밖에서 보이는 동작 불변». lens 는 ⓐ 경로에 2번 판정을 적용한다(수정 모드 2번 `dddjango.md:191` 과 같은 방식) | 그대로 |
| Phase 0 3번 빚 스캔(79) | 27종 · 대상 BC · exact command 기록은 그대로다. 문장 «「리팩터링 대상」의 별도 정의는 없다 — 백스톱이 내는 위반이 곧 그것이다»는 리팩토링 모드에서 «+ BC 전체 점검 항목»으로 고친다. 스캔 원출력의 `[ⓓ#N]` 후보 라인(14개 검사기가 발행 — 예: `check-layer-skeleton.py:94` 200행 신호 ⓓ#644 · `check-public-surface-annotation.py` #645/#647/#650)이 전체 점검의 기계 씨앗이다 | 개정(소) |
| **새 3′·3″ 번** | 3′: 리뷰어 BC 전체 점검 다발. Phase 1 2번의 «병렬 = 한 응답 안 다발» 정의를 재사용한다. 3″: design-architect 판정·중재(G0 전). **Phase 0 이 서브에이전트를 부르는 첫 경우다** | 신설(5B) |
| Phase 0 4번 G0 질문·배너(80) | 질문 순서(86)는 그대로다: 폴더 → 실행 선택 → 빚 질문(검사기 + 의미 항목 + «판정 제외») → 스코프 승인. 배치 질문은 없다(정리 요청 제외 규칙). ⓐ/ⓑ/ⓐ′ · «미룰 수 없음» · 결정 출처(82) · 충돌(83) · 실행과 앵커(85) · G0 정지 기록(86)도 그대로다 | 그대로 |
| 결과 표 형식(80 `위반 \| 백스톱 \| 미룰 수 있나`) | 제안: `ID \| 위반 \| 출처(registry #N \| 리뷰어 · 규칙 문구) \| 파일:행 \| 미룰 수 있나`. 여기에 `## 판정 제외(architect)` 절을 더한다(`M<n> · 근거 = 규칙 문구 인용 — 비위반 사유`). ID 는 검사기 `C<n>`(경로 · 규칙) · 의미 `M<n>` 이다. 결정 줄의 `<항목 ID 목록>` 을 그대로 쓴다 | 개정 |
| 정리할 것 없음 정지(84) | 조건이 «검사기 ⓐ 0 ∧ 의미 ⓐ 0(제외 뒤) ∧ 사용자 항목 0»으로 넓어진다 | 개정(소) |
| Phase 1 전체(90-105) · pre-gate | 그대로 쓴다. architect 입력에 Phase 0 판정 결과를 더한다 | 그대로 |
| Phase 1 «슬라이스 0 과 비위반 이동의 STOP»(106) | «백스톱 위반이 아닌 기존 코드의 이동»을 «G0 ⓐ 목록(검사기·의미)에 없는 기존 코드의 이동»으로 바꾼다. 동작 불변 불가 → `ⓐ 재상정` 은 그대로다(의미 항목에도 적용) | 개정 |
| Phase 2 3번 슬라이스 0 · 0T/0C · 동작 보존 창(113) | 그대로 쓴다. 기능 슬라이스가 없으므로 Phase 2 = 슬라이스 0 전부다. 결정 2 (가)로 창이 적용된다 | 그대로 |
| Phase 2 1번 인수 테스트 | 외부 계약이 바뀌지 않으므로 입장 표는 대개 `reuse/retain` 이다. 현행 라우팅이 그대로 성립한다 | 그대로 |
| Phase 2 5번 감사(117) | 입력에 «ⓐ 의미 항목 목록(규칙 문구 · 원 파일:행) + `behavior_guard` 0C 대응표(옛→새 경로)»를 더한다 | 개정 |
| Phase 2 6번 registry 게이트(123-) | 그대로 | 그대로 |
| Phase 2 7번 G2 ⓐ 잔존(174) | 아래 산식 | 개정 |
| 수정 모드 · Phase 3 · 엣지 · 경계 | 그대로. 경계 절의 기계 기록 열거에 새 기록 파일이 생기면 추가한다 | 그대로 |

**의미 항목을 ⓐ/ⓑ 틀에 넣을 수 있나**: 넣을 수 있다. 결정 출처, ⓐ′, «미룰 수 없음», 충돌, 재상정은 항목의 출처와 무관하게 작동한다. 새로 필요한 것은 ⓑ 와 다른 제3 상태 **«판정 제외»(architect · 규칙 문구 근거)**다. 경계 조건이 있다. 비용·범위를 이유로 항목을 빼는 것은 제외가 아니라 ⓑ 이고 사용자 출처가 있어야 한다. 이렇게 막지 않으면 제외가 «암묵 ⓑ»(현장 28건 유형 — `diag-A-field-evidence.md`)의 새 세탁로가 된다.

**G2 «ⓐ 잔존» 산식** — registry_gate 로 셀 수 없는 절반을 채운다:

- N = N_c(검사기 ⓐ) + N_m(의미 ⓐ). G0 에서 동결하고, `ⓐ 재상정` 으로 뺀 항목은 제외한다.
- M_c = |registry_gate legacy 잔존 ∩ ⓐ_c(경로·규칙)| — 현행 그대로다.
- M_m = ⓐ_m 가운데 G2 재대조에서 «잔존»으로 판정된 수.
  - 판정 주체는 그 항목을 낸 리뷰어 역할이다(전체 점검 모드의 «ⓐ 대조» 변형). coder·Coordinator 가 스스로 판정하지 않는다.
  - 출력은 항목마다 «해소(근거 파일:행) | 잔존(파일:행)»이다.
  - 기계 보조(fail-closed): ⓓ 채널이 있는 규칙은 0C 대응표로 옮긴 경로에 같은 `[ⓓ#N]` 이 남아 있으면 리뷰어 판정과 무관하게 잔존이다.
- 배너 1행은 `G0 ⓐ N건(검사기 N_c · 의미 N_m) 중 잔존 M(검사기 M_c · 의미 M_m)` 이다. M>0 이면 G2 제시를 금지한다(현행 차단 그대로).
- 비용: G2 직전 리뷰어 재호출 1다발이 늘어난다. discipline-reviewer 가 낸 항목은 5번 감사에 합칠 수 있다 **[추정]**.

## 4. dddjango-web 차이(짧게)

- **산문 정본(그래프 밖)**: 커맨드를 더해도 온톨로지 연쇄가 0이다. 새로 만드는 것은 `dddjango-web/commands/<새>.md` 와 `codex-dddjango-web/skills/dddjango-web-<새>/SKILL.md` 다. 함께 바꾸는 것은 REQUEST_GUIDE 2개(verify-web `cmp` byte 미러 — §6 198-201행 정리 예시 교체)와 `README.md:317` «커맨드 1»이다. `workspace/tools`·`Makefile` 가운데 `dddjango-web/commands` 를 참조하는 곳은 0이고, 봉인 대상도 아니다 **[실측 grep]**.
- **B-2 불가**: `dddjango-web.md:5` `disable-model-invocation: true` 라서 Skill 위임이 막힌다. 그 플래그를 풀거나, B-1 Read 를 쓰거나(112,769 bytes — dddjango 와 같은 쪽 나눔이 추정된다 · `arguments: [feature, api_url]` 이름 인자는 미치환), 입구 안에 절차를 둔다(웹은 산문이라 A1 형태의 중복 비용이 상대적으로 작다). 셋 중 고른다 **[추정]**.
- **재사용할 «정리 모드»가 없다**: `dddjango-web.md` 에 «빚»은 0회이고, 백스톱은 touched 한정이다 **[실측]**. 결정 1-d(G0 빚 조사 신설)가 먼저 들어가야 얇은 입구가 성립한다 → 로드맵 6 순서는 «1-d → 리팩토링 입구»다.
- 모드가 풀·수정·트리비얼 삼분류(119행)에 «기존 화면 재개 입구»(22행)와 `build-state.json` 스키마(55행)까지 있어서, 리팩토링 실행의 상태 값을 더해야 할 수 있다 **[추정]**. 동작 보존 장치의 web 판은 없다(로드맵 6).

## 5. 열린 질문 (사용자 결정)

1. **`/dddjango` 로 들어온 «정리 요청»의 처리** — 현행(`dddjango.md:67` — 로드맵 1 `e3ad8e16` 로 도입)은 풀 파이프라인으로 받아 검사기 빚만 정리한다. 결정 1-d 는 web 에 대해 «정리 요청은 리팩토링 커맨드로 안내한다 — dddjango 와 같은 방식»이라고 적었다. 선택지:
   - (가) dddjango 도 같게: 정리 요청이면 G0 에서 `/dddjango:refactor` 를 안내하고 정지한다. 대가는 이미 배포된 경로의 동작이 바뀌는 것이다.
   - (나) 둘 다 유지: `/dddjango` 정리 요청 = 검사기 빚만, 리팩토링 커맨드 = 검사기 + 의미다. 대가는 비슷한 두 경로 때문에 사용자가 헷갈리고 가이드 문단이 둘로 는다는 것이다.
2. **커맨드 이름** — 권고는 파일 `commands/refactor.md` → `/dddjango:refactor` 다. Codex 는 전역 이름 충돌 관례에 따라 `dddjango-refactor`, web 은 `/dddjango-web:refactor` · `dddjango-web-refactor` 다. 대안은 `/dddjango:dddjango-refactor`(길지만 검색하기 쉽다).

(약한 단언 강화 (가)/(나)는 5C 가 정리한다 — 결정 2 Q3.)
