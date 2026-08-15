# coder 병렬화 자료조사 — 실무 관행 · 계약 기법 · 멀티에이전트 실증

2026-08-15. 사용자 아이디어(coder 병렬 + 전체 설계도를 가진 coordinator 중재 + 슬라이스 중첩 최소화·사전 합의 + 실무 관행 이식)의 효과·구현 가능성 검토 재료.
배경 실측: 05 구현이 양 레인 공통 최대 칸(claude 3h37m=60% · codex 8h00m=68% — `optimization-board.md` 2.8.0 행).

---

## 0. 결론 요약 — 사용자 아이디어 대비 판정

| 아이디어 항목 | 판정 | 근거 |
|---|---|---|
| coder를 병렬로 실행 | **지지·단 폭 2~3** | 실증 최적 N=2~4, N=8부터 하락(CAID) · DORA 고성과 문턱 = 동시 미통합 작업선 ≤3 |
| 전체 설계도를 가진 coordinator가 중재 | **지지 — 실무 integrator와 정확히 동형** | integrator의 실제 일 3가지 = merge 순서 결정·영역별 승인·green 유지(rollback 우선). 전역 dependency 정보를 orchestrator가 쥐는 것이 배정 품질을 지배(CAID: 같은 설정 두 run이 핵심 파일 배정 여부로 8.7% vs 34.3%) |
| 슬라이스 중첩 최소화·중첩은 사전 합의/중재 | **지지 — 단 «사후 협상»이 아니라 «사전 제거»** | 통신량 증가로는 안 풀림(CooperBench: 예산 20%를 통신에 써도 success 불변) · 중첩은 분할 단계에서 구조로 제거하는 편이 싸다 |
| 미구현 의존은 interface를 약속하고 진행 | **지지 — 단 계약은 산문이 아니라 기계 실행물** | API-first·Design by Contract·CDC 전부 «기계가 검증하는 계약»이 전제. 산문 합의만 있으면 spec-implementation drift로 사문화 |

핵심 경고 둘:
- **분할 품질이 성패다.** naive 파일 분할은 speedup 0에 cost만 +44~60%(Co-Coder), 조정 없는 2-agent 협업은 success −30%(CooperBench). 응집(cohesion) 기반 분할일 때만 wall-clock 1.81~2.10x + 품질 동반 상승.
- **격리는 지시문이 아니라 물리로.** 공유 workspace + 지시 수준 분리(soft isolation)는 single-agent보다도 나빴다(CAID 55.5 < 57.2). git worktree 격리가 필수.

---

## 1. 축 1 — 실무 팀의 영역 분할·중첩 처리·합류 실증

### 분할
- **code ownership 3모델**(Fowler): strong(단독 소유자·타인은 patch만 — 병목·비권장) / weak(지정 소유자+전원 수정 허용·큰 수정 전 상의) / collective(전원 소유 — pair·리뷰로 2인 이상의 눈이 전제). https://martinfowler.com/bliki/CodeOwnership.html
- **Google OWNERS**: 디렉터리 계층별 승인권 — 수정은 누구나, 해당 디렉터리 owner 승인 필수. 이 모델이 file locking을 대체. 5만 엔지니어·일 6~7만 commit 규모 실증. https://abseil.io/resources/swe-book/html/ch16.html
- **GitHub CODEOWNERS**: 경로 패턴→자동 리뷰 라우팅+merge 게이트. «수정 금지»가 아니라 «수정 시 승인 경로»의 기계화. https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
- **vertical slice 분할**: "Minimize coupling between slices, maximize coupling in a slice" — slice 하나=작업자 하나면 중첩이 구조적으로 축소. layer 분할은 한 기능이 전 layer를 가로질러 접촉면 최대화. https://www.jimmybogard.com/vertical-slice-architecture/
- **Conway's law**: 분할은 통신 구조를 복제 — 시스템 분해와 조직(agent 편성) 분해는 함께 설계해야 한다. https://martinfowler.com/bliki/ConwaysLaw.html

### 중첩 처리
- **trunk-based development**: branch 수명 ≤2일 · branch당 작업자 1명 · 개발자 branch끼리 merge 금지. 중첩 관리의 본질 = «충돌을 없애기»가 아니라 «작고 즉시 보이게». https://trunkbaseddevelopment.com/short-lived-feature-branches/
- **CI 규율**: "No code sits unintegrated for more than a couple of hours"(Beck) · 깨진 build 최우선·기본 대응은 revert. https://martinfowler.com/articles/continuousIntegration.html
- **semantic conflict**: rename+구이름 호출처럼 텍스트 merge가 못 잡는 충돌 — self-testing build가 유일한 안전망. https://martinfowler.com/articles/branching-patterns.html
- **hot-spot 파일**: merge의 7.6~19.3%가 충돌(2,731 프로젝트 실측)하고 충돌은 소수 파일에 몰림. 실무 답은 구조 소멸 — GitLab은 전원이 편집하던 CHANGELOG.md를 버리고 commit trailer+생성기로 전환(entry-per-file·생성 파일화). `merge=union`은 공식 문서가 경고하는 최후수단. https://docs.gitlab.com/ee/development/changelog.html · https://arxiv.org/pdf/2102.11307
- **mob programming**: 설계 합의가 안 선 큰 변경은 병렬화하지 않고 작업선 1개로 — 우리로는 «설계 승인 후 분배» 단계에 해당. https://mobprogramming.org/

### 합류 실증
- **DORA 고성과 문턱**: active branch ≤3 · 최소 하루 1회 trunk merge · code freeze 없음 — 이를 지키는 팀이 delivery 성과·조직 성과 모두 우위. https://dora.dev/capabilities/trunk-based-development/
- **big-bang 통합 실패**: 수개월 통합 표류 목격담(Fowler) · HP LaserJet 펌웨어가 branch→trunk 전환으로 신기능 개발 시간 5%→40%(8배). 단 전제 = 자동 테스트. https://itrevolution.com/articles/the-amazing-devops-transformation-of-the-hp-laserjet-firmware-team-gary-gruver/
- **integrator의 실제 일 3가지**: ① merge 순서 결정·수행(integration manager — 기여자는 서로 안 기다림·통합만 단일 지점 직렬화) ② 영역별 승인(lieutenant/OWNERS) ③ green 유지(Google Build Cop — 누가 깨뜨렸든 rollback 우선). https://git-scm.com/book/en/v2/Distributed-Git-Distributed-Workflows · https://abseil.io/resources/swe-book/html/ch23.html

---

## 2. 축 2 — 미구현 의존: «interface 먼저 약속»의 실무 형태

- **API-first**: Design→Review→Mock→Implement→Validate. 계약 문서(OpenAPI)를 정본으로 확정→mock server 생성→소비 측 즉시 개발·제공 측 동시 구현. 전제 = 구현-문서 일치의 기계 강제(contract testing·lint를 CI 필수 체크로). 없으면 drift로 사문화. https://apisyouwonthate.com/blog/a-developers-guide-to-api-design-first/
- **Design by Contract**(Meyer): precondition/postcondition/invariant를 코드에 명시+실행 중 검사. 상속 시 subcontracting(pre는 약화만·post는 강화만)으로 하위 구현이 계약을 못 깨게. https://www.eiffel.com/values/design-by-contract/introduction/
- **Consumer-Driven Contracts**(Robinson/Fowler): consumer가 «실제로 쓰는 부분만» 계약으로 제출, 그 합집합이 provider 의무. 한계 명시 — "a breaking change is still a breaking change": 계약은 파기를 없애지 않고 조기에·귀책 명확하게 드러낼 뿐. https://martinfowler.com/articles/consumerDrivenContracts.html
- **Pact + pending pacts**: consumer 기대를 pact 파일로 기록→provider 실물에 replay 검증→`can-i-deploy` 게이트. **귀책의 기계 판정**: 첫 성공 검증 이후 같은 계약이 실패하면 provider 귀책 — 판정은 기계, 새 기대의 수용 여부만 사람 몫. https://docs.pact.io/blog/2020/02/24/how-weve-fixed-the-biggest-problem-with-the-pact-workflow
- **test double↔실물 정합**(Rainsberger 대응쌍): double을 쓰는 collaboration test마다 같은 계약을 실물에 실행하는 contract test를 짝으로 — 없으면 «double green·실물 red» false positive. 교체 시점 통과 조건 = stub에 기록한 기대를 실물에 replay해 전건 green. https://martinfowler.com/bliki/ContractTest.html
- **branch by abstraction / walking skeleton**: 항상 빌드·동작을 유지한 채 abstraction 뒤에서 병행 구현 / 전 구성요소를 관통하는 최소 end-to-end를 먼저 연결한 뒤 각 부품을 병렬로 살찌움 — stub 위에만 쌓는 위험의 보험. https://martinfowler.com/bliki/BranchByAbstraction.html · https://www.oreilly.com/library/view/97-things-every/9780596800611/ch60.html
- **계약 변경 중재**(Azure Breaking Change Board): spec diff 도구가 47종 파기 후보를 기계 검출→라벨→심의 승인 없이 merge 불가. 귀책 판정=기계·파기 승인=사람의 분리. https://devblogs.microsoft.com/azure-sdk/azure-approach-to-versioning-and-avoiding-breaking-changes/
- **LLM 특화**: 계약(spec)은 작고 초점 있게 쪼개는 것이 agent 준수율의 조건(arXiv:2510.19274) · 실무 가이드 공통 원칙 "One file, one owner". https://arxiv.org/abs/2510.19274

---

## 3. 축 3 — 멀티에이전트 병렬 코딩 실증

### 사례
- **Anthropic research system**: orchestrator-worker. subagent별 objective·boundary·output format을 명시한 위임. 단일 Opus 대비 +90.2%(research eval) · 시간 최대 −90% · 단 tokens 15x. 초기 실패 = 과잉 spawn·중복 탐색 → effort scaling 규칙으로 대응. https://www.anthropic.com/engineering/built-multi-agent-research-system
- **Anthropic C compiler**: 16 agents·2주·~$20k로 10만 줄 컴파일러. 중앙 orchestrator 없이 git lock 파일로 task claim(git atomicity가 mutual exclusion). 실패 = 전원이 같은 버그에 몰려 상호 덮어씀 → oracle(GCC)로 버그를 파일 단위 분산. https://www.anthropic.com/engineering/building-c-compiler
- **Cognition(Devin)**: 「Don't Build Multi-Agents」(병렬 write는 conflicting implicit decisions) → 2026 수정 입장 「writes stay single-threaded, 추가 agent는 intelligence만」. fresh-context review agent가 PR당 평균 ~2 bugs(58% severe) — context를 공유하지 **않을 때** 더 잘 잡음. https://cognition.com/blog/multi-agents-working
- **제품 공통형**(Cursor·Codex·Jules·Factory): task마다 VM/container/worktree 격리 + branch당 1 agent + PR 합류. 병렬 폭 대비 정량 수치는 미공개.

### 논문(핵심 수치)
- **CAID**(arXiv:2603.21489 — 가장 직접적): manager가 repo를 dependency graph로 모델링, ready set에서만 배정, 강결합·순환 dependency 파일은 같은 engineer에 묶음. engineer마다 git worktree, 공유 파일(`__init__.py` 등)은 restricted. conflict는 유발 engineer가 main pull 후 자기 해소. 지시는 자연어가 아니라 구조화 JSON. 수치: single 대비 PaperBench +25.6pp·Commit0-Lite +14.7pp / **soft isolation은 single보다 나쁨(55.5<57.2)** / **N=2→4 개선·N=8 하락** / 배정 품질이 지배(8.7% vs 34.3%) / **wall-clock은 오히려 김 — 이득은 정확도**.
- **Co-Coder**(arXiv:2606.00953): cohesion-aware graph partitioning일 때만 **wall-clock 1.81x/2.10x + cost −28/−35% + pass +11.3/+14.0pp**. naive 파일 분할 = speedup 0·cost +44~60%. Claude Code Agent Teams는 최속(680s)이나 pass 16.3%로 sequential 이하.
- **CooperBench**(arXiv:2601.13295): 조정 없는 2-agent 협업은 단독 대비 **success −30%**. 통신 예산 20%로도 안 풀림 → 사전 분할이 사후 협상보다 싸다.
- **AgenticFlict**(arXiv:2604.03551): AI agent PR 14.2만 건 실측 — 27.67%에서 merge conflict. 작은 PR일수록 유의하게 낮음.
- **MAST**(NeurIPS 2025): multi-agent 실패 14모드 분류 — 다수가 LLM 한계가 아닌 시스템 설계 결함.
- **STORM**(arXiv:2605.20563): write 시점 충돌 검출로 worktree 대비 +18.7(Commit0) — 격리 방식의 대안 축.
- **METR RCT**: 인간 검증이 병목이면 AI 도구로 오히려 19% 느려짐 — 합류·검증 편성이 손익을 결정.

---

## 4. 우리 파이프라인 설계 초안 (step 4 개정 — L8 구체화·2.9.0 후보)

현행: coordinator가 슬라이스 분할→**한 개씩 직렬 배차**→슬라이스별 경량 감사→홀리스틱 감사→백스톱 27종. 직렬 강제 문면은 «의존 사슬 bottom-up»·«같은 파일 동시 편집 금지» 둘뿐.

개정 골자 6개 — 전부 위 실증에 1:1 대응:

1. **wave 편성**: coordinator가 설계 명세의 의존 그래프에서 슬라이스를 wave로 묶는다.
   - **wave 0 (직렬·coder 1)**: 공유층 — domain aggregate·값 객체·port 계약(ABC 시그니처)·경계 스키마·입구 배선의 walking skeleton. 이것이 «interface 먼저 약속»의 실물이며, 이후 **mypy+ABC가 계약 위반을 기계 검출**한다(계약=기계 실행물 요건 충족).
   - **wave 1+**: 의존 없는 use_case 슬라이스를 **2~3개 병렬** 배차. 강결합 슬라이스는 같은 coder에 묶는다(분할 품질=성패).
2. **물리 격리**: coder마다 git worktree + 전용 테스트 DB(`POSTGRES_TEST_DB` 접미 분리 — L5 레인 간 분리 실증의 재사용). soft isolation 금지.
3. **restricted 파일 선언**: aggregate·domain 공유 파일, admin, api 배선(registry), settings, **migrations** — wave 0 이후 동결. 변경 필요 시 coordinator 중재(요청→판정→전 coder 전파 = Pact pending의 축소판). migrations는 병렬 중 생성 금지, 합류 후 coordinator가 일괄 생성 — 순차 번호 충돌을 hot-spot 구조 소멸 방식으로 원천 제거.
4. **합류 규칙**: wave 종료마다 merge(마지막 일괄 금지 — big-bang 실증). coordinator가 순서대로 merge→층별 green→conflict·red는 **유발 coder에 귀속 재배차**(main pull 후 자기 해소 — CAID). coordinator = integration manager + Build Cop.
5. **검증 2단 무변**: 슬라이스 경량 감사=merge 관문(다른 coder 구현과 파이프라인화), 홀리스틱 감사+백스톱 27종=최종 관문 그대로. Cognition 실증(fresh-context reviewer가 더 잘 잡음)이 현행 독립 감사 구조를 지지.
6. **배차 지시 형식**: 산문이 아니라 구조화 명세 — objective·소유 파일 목록(배타)·참조 계약·boundary·완료 조건.

**기대 효과와 상한**: 실증 상한 = wall-clock 1.8~2.1x(응집 분할 조건 충족 시). 05가 claude 3h37m이므로 현실 목표 ≈ 05 30~40% 단축. 단 CAID처럼 wall-clock이 늘고 정확도만 오르는 결과도 가능 — 첫 적용 라운드에서 레이어 실측으로 판정한다.

**성능>속도 게이트 점검**: 리뷰 렌즈·검사기 27종·감사 범위·게이트 문면 전부 무변(바뀌는 것은 step 4의 실행 편성뿐), 합류 검증은 오히려 추가 — 정보 손실 0 · 판정 무변 충족.

**착수 전 결정 필요(사용자)**: ① step 4 개정(2.9.0) 착수 여부 ② G2 직접 계열 5종 수정(개선 후보 ⑤)과 같은 릴리즈로 묶을지 ③ 첫 적용 BC.

---

## 5. 보강 조사(같은 날 2차) — Claude Code 생태계 플러그인·스킬·세션 도구의 실물

사용자 요청: «superpowers 같은 유명 코드 작성 플러그인·스킬의 병렬 방식 조사». 3축 — ① 설치본 superpowers 스킬 원문 직접 판독 ② 플러그인 생태계(레포 원문 대조) ③ swarm·worktree 세션 도구+실사용 후기.

### 5.1 superpowers — 구현 병렬화를 하지 않는다 (설치본 6.2.0/6.3.0 원문 확인)

- 구현 파이프라인(subagent-driven-development)에 **명문 금지**: "Never dispatch multiple implementation subagents in parallel (**conflicts**)" — plan의 task 1개=fresh subagent 1개 직렬 위임, task마다 리뷰(spec compliance+code quality)→fix loop(상한 5라운드·4라운드부터 상위 모델)→최종 whole-branch 리뷰.
- 병렬 스킬(dispatching-parallel-agents)은 **독립 버그 조사·테스트 수리 한정** — worktree 격리 없이 «같은 파일·공유 상태면 사용 금지» 전제. merge 절차 없음(controller 눈검사+full suite 재실행).
- 내부 설계 문서가 병렬 리뷰 파이프라이닝을 **실측 후 기각**한 기록 보존(«benefit below the run-to-run noise floor»).
- **재사용 가치 최대 부품**: writing-plans의 task별 **Interfaces 블록** — "Consumes: [정확한 시그니처] / Produces: [후행 task가 의존하는 정확한 함수명·파라미터·반환 타입]". 직렬 handoff 계약이지만 배차 전에 동결하면 그대로 병렬 계약서. 그 외: 조정 상태의 파일 영속화(ledger — compaction 생존), diff·리뷰 패키지의 파일 경유 전달.
- 실측된 실패 모드: compaction 후 ledger 없던 controller가 완료 task 전체 재배차 · dispatch prompt 비대(42k chars) · worker가 스스로 reviewer를 띄워 좌석 중복.

### 5.2 생태계 전체의 수렴 패턴 (레포 원문 대조 결과)

1. **동시 write의 실물은 예외 없이 «분할 소유»** — worktree/branch 단위(claude-squad·Crystal·Conductor·Kilo Agent Manager) 또는 배타 파일 집합(ccpm streams·공식 Agent Teams). 격리 없는 동시 write를 허용하는 도구 0개.
2. **구현은 직렬 기본, 리서치·리뷰만 병렬** — superpowers(직렬 명문)·compound-engineering(ce-work 직렬 기본+안전 게이트 통과분만 병렬·ce-code-review는 리뷰어 동시 배치)·공식 Agent Teams(권장 시나리오가 병렬 리뷰·경쟁 가설 디버깅 — "without the coordination challenges that come with parallel implementation").
3. **합류를 자동화한 도구 0개** — compound «integrate one result→verify→canonical commit→retire»(순차 통합) · ccpm «충돌은 auto-resolve 금지, 보고 후 정지» · squad/Crystal/uzi/Conductor는 인간이 diff 보고 merge/rebase 선택.
4. **의존 그래프+claim 큐+상태 파일화** — Agent Teams(파일 락은 task claim에만·의존 task 자동 unblock), ccpm(의존 미충족 stream 큐잉), superpowers ledger.
5. **과장 판명 목록**: SuperClaude `/spawn`(실물 없음 — todo 분해) · wshobson/agents(순차 체인 문서뿐) · ccpm «no conflicts»(같은 worktree 수동 파티셔닝·«89%/3x»는 자사 보고) · Agent Teams 소개글의 «자동 격리»(공식 문서 부정 — "Two teammates editing the same file leads to overwrites. Break the work so each teammate owns a different set of files.") · task-master(순차 next-task 플래너) · **claude-flow**(placeholder 명령 이슈 #578·비감사 벤치마크·실사용 «poor results» 후기 — 공유 디렉터리 swarm의 정착 실사용 사례 확인 안 됨) · Roo Code Orchestrator(순차 재귀 — 부모 pause+summary 복귀, 병렬은 open feature request).

### 5.3 실사용 후기의 수렴치

- **유효 병렬 폭 3±2** — «Up to 3, your brain keeps up. Past 5, you drop the thread» · Codex 계열 «3–5 sweet spot» · 보드·자동 게이트를 갖추면 ~8. **논문(CAID 2~4)·DORA(미통합 작업선 ≤3)와 삼중 일치.**
- **병목 서열**: ① 합류 지점의 리뷰 처리량(전 소스 공통 — "agents can move faster than you can review") ② 상태 추적·관리 오버헤드 ③ semantic 충돌(worktree로 파일 충돌은 막아도 남음) ④ 로컬 자원(메모리·DB·port).
- **정착 편성 원형**: «spec 선행 확정 → ownership-disjoint 분해 → worktree 물리 격리 → 폭 2~5 → 워커 간 통신 없음 → 슬라이스당 branch → 순차 merge+게이트 리뷰». Conductor 실사용 교훈 — "without the attack document, N parallel agents is chaos. With it, N parallel agents is just a faster queue."
- **best-of-N**(같은 슬라이스 다중 시도 후 선택 — Codex `--attempts`·Crystal)은 실증된 품질 레버. 단 토큰 N배 선형 — 재료 결함 의심 슬라이스에만 선별 투입할 것.

### 5.4 설계 초안(§4) 보정

§4 골자 6개는 생태계 실증과 전부 합치(wave 0 계약 동결=Conductor spec.md 교훈·superpowers Interfaces 블록과 동형, restricted 파일=Agent Teams 공식 권고와 동형). 보강으로 추가·강화할 것:

- **⑹ 강화 — 배차 명세에 Interfaces 블록**: 슬라이스마다 «Consumes: [wave 0 계약의 정확한 시그니처] / Produces: [후행·이웃이 의존할 함수명·타입]»을 명문화(superpowers 부품 이식). 소유 파일 목록은 배타(disjoint) 검증을 배차 전에 기계로.
- **⑺ 신설 — 충돌 시 정지 규칙**: merge conflict·소유 밖 파일 접촉은 자동 해소 금지 — 검출 즉시 해당 coder 정지, coordinator가 귀속 판정 후 재배차(생태계 표준 «report and pause» + CAID 귀속 규칙의 결합).
- **⑻ 신설 — 조정 장부 파일화**: wave 편성·배차 계약·완료 마킹을 파일로 영속화(superpowers ledger 사고·Agent Teams 완료 마킹 lag가 실측 실패 모드).
- **병렬 폭 2~3 재확인** — 논문·DORA·실사용 삼중 수렴. 폭 확대의 전제는 합류 게이트 처리량.
- **우리 구조의 유리한 점**: 실사용 병목 1위(인간 리뷰 처리량)가 우리는 기계 게이트(층별 green·백스톱·경량 감사)라 완화됨. 단 경량 감사 agent가 새 병목이 될 수 있어 감사 파이프라인화(§4-5)가 전제.
- **채택 안 함**: 공유 디렉터리 swarm(실증 0·과장 논란) · 자동 merge 해소 · 런타임 자율 분해(spec 선행 확정이 실증 우위). best-of-N은 이번 개정에 안 넣고 «재료 결함 의심 슬라이스 한정 레버»로 후보 큐에만 등재.

---

## 6. 적용 체크리스트 — 병렬 coder를 돌리기 위해 적용해야 하는 것 전부

### A. 프로토콜 문면 개정 (dddjango.md Phase 2 step 4 — 2.9.0 후보)

| # | 항목 | 적용 내용 | 실증 근거 | 준비도 |
|---|---|---|---|---|
| 1 | wave 편성 규칙 | coordinator가 설계 명세의 의존 그래프로 슬라이스를 wave로 묶음. **wave 0**=공유층(aggregate·port 계약·경계 스키마·배선 walking skeleton) coder 1명 직렬 → **wave 1+**=무의존 슬라이스 병렬. 강결합 슬라이스는 같은 coder에 | CAID(배정 품질이 지배)·Co-Coder(응집 분할일 때만 1.8~2.1x)·walking skeleton | 신규 문면 |
| 2 | 병렬 폭 상한 | 동시 coder **≤3** 명문 | CAID(2~4 최적·8 하락)·DORA(≤3)·실사용(3±2) 삼중 수렴 | 신규 문면 |
| 3 | 배차 명세 형식 | 산문 금지 — objective·**배타 소유 파일 목록**·**Interfaces 블록**(Consumes/Produces: 정확한 시그니처)·완료 조건 | Anthropic 위임 원칙·CAID 구조화 JSON·superpowers writing-plans | 신규 문면+템플릿 |
| 4 | restricted 파일 | admin·api 배선·settings·공유 domain 파일: wave 0 이후 동결. 변경은 coordinator 중재(요청→판정→전 coder 전파) | CAID restricted·Agent Teams 공식(«파일 집합을 나눠라»)·Pact pending(귀책 기계 판정) | 신규 문면 |
| 5 | migrations 규칙 | 병렬 중 생성 금지 → wave 합류 후 coordinator 일괄 생성(순차 번호 충돌 원천 제거) | hot-spot 구조 소멸(GitLab CHANGELOG 방식) | 신규 문면 |
| 6 | 합류 규칙 | wave 종료마다 coder분을 **한 번에 하나씩** 순차 merge + 층별 green + 관련 테스트. 마지막 일괄(big-bang) 금지 | compound «integrate one→verify→commit»·DORA·HP 사례(5%→40%) | 신규 문면 |
| 7 | 충돌 시 정지 | merge conflict·소유 밖 파일 접촉은 자동 해소 금지 — 해당 coder 정지 → coordinator 귀속 판정 → 유발 coder가 main pull 후 자기 해소 | 생태계 표준 «report and pause»·CAID 귀속 규칙 | 신규 문면 |
| 8 | 감사 편성 | 슬라이스 경량 감사=merge 관문(다음 wave 구현과 파이프라인화). 홀리스틱 감사+백스톱 27종 **무변** | Cognition fresh-context reviewer·검증 2단 | 기존 감사 재배치 |

### B. 인프라·도구 (하네스·스크립트)

| # | 항목 | 적용 내용 | 실증 근거 | 준비도 |
|---|---|---|---|---|
| 9 | coder별 git worktree | coder마다 worktree+branch 생성·정리 절차 | soft isolation은 single보다 나쁨(CAID 55.5<57.2) | 도구 존재·절차 신규 |
| 10 | coder별 테스트 DB | `POSTGRES_TEST_DB` 접미 분리(coder 단위로 확장) | L5 레인 간 분리 실증 재사용 | 기존 실증 재사용 |
| 11 | 배타 검증 스크립트 | 배차 전 소유 파일 목록 교집합=0 + restricted 접촉 0 기계 확인 | «One file, one owner»·ccpm stream 파티셔닝 | 신규 소형 도구 |
| 12 | 조정 장부 파일 | wave 편성·배차 계약·완료 마킹을 `.dddjango/<run>/` 파일로 영속화 | superpowers ledger 사고(compaction 후 전체 재배차)·Agent Teams 완료 마킹 lag | 신규 파일 규약 |
| 13 | merged-state 검증 | merge 직후 통합 상태에서 테스트 실행(semantic conflict — rename+구이름 호출류 — 검출) | Fowler semantic conflict·merged-result 테스트 | 기존 make test 활용·시점 규정만 신규 |

### C. 무변 확인 (성능>속도 게이트)

| # | 항목 | 내용 |
|---|---|---|
| 14 | 판정 장치 무변 | 검사기 27종·G1/G2 문면·리뷰 4렌즈·감사 범위 전부 무변 — 바뀌는 것은 step 4 실행 편성뿐. 정보 손실 0·판정 무변 |
| 15 | 효과 판정 기준 | 첫 적용 라운드에서 레이어 실측(01~06) 계속 — 05 단축 폭과 총 wall-clock 증감으로 판정(정확도만 오르고 시간은 안 주는 CAID 패턴 경계) |

### D. 사용자 결정 필요

| # | 항목 | 내용 |
|---|---|---|
| 16 | 릴리즈 편성 | step 4 개정(2.9.0)을 검사기 5종 수정(개선 후보 ⑤)과 묶을지 분리할지 |
| 17 | 첫 적용 BC | 병렬 편성 첫 라운드의 대상 BC |
| 18 | 레인 B(codex) 적용 | 병렬 coder는 하네스(Agent 도구) 기능이라 claude 레인 우선 — codex 레인은 native subagent thread 지원 검토 후 별도 결정(문면은 공용 가능) |

---

## 7. 역할·테스트·충돌 편성 (사용자 master coder 안 검토·보정 — 08-15)

사용자 안: coder들이 master coder에게 묻고, master coder가 coordinator(설계도 보유)에게 물어 겹침·문제를 해결해 coder들에게 나눠준다.

**판정: 방향 유지·역할 재정의.** «상시 질의 중개자»는 실증이 부정(CooperBench — 통신 예산 20%도 무효·중첩은 사전 제거가 정답)하고 하네스 구조상 홉만 추가(coder 질문은 어차피 coordinator로 반환됨)·두 번째 대형 context를 만들어 직렬 병목을 재생산한다. 대신 **master coder = 공유층 소유자 + 합류 집행자(단독 writer)** — integration manager + Build Cop + designated owner의 결합으로 재정의하면 실증과 전부 합치.

### 7.1 좌석 편성

| 좌석 | 소유 | 하는 일 |
|---|---|---|
| coordinator | 설계 명세·판정 | wave 편성·배차·계약 변경 판정·귀속 판정. **코드 안 씀(무변)** |
| **master coder** | 공유층·통합선 | wave 0 공유층 구현(계약 실물 제작자=중재 적격) → wave 합류마다 merge 실행·merged-state 테스트·acceptance 판정·migrations 일괄 생성·교차 원인 결함 수리 |
| coder ×2~3 | 자기 슬라이스(배타 파일) | 구현+자기 슬라이스 테스트. 막히면 정지·보고(자가 해석 금지 — 현행 규율 유지) |

### 7.2 테스트 3층

| 층 | 무엇 | 누가·언제 |
|---|---|---|
| 1 | 슬라이스 내부 테스트(단위·내부 루프) | 각 coder가 자기 worktree+전용 DB에서 자체 처리 |
| 2 | **acceptance(합쳐야 가능한 것)** | **쪼개지 않는다** — 통합선에 통째로 상주. Phase 2 시작의 바깥 루프 Red 생성은 무변. 입장 표의 테스트↔use case 매핑으로 coordinator가 wave별 «기대 green 집합»을 도출 → wave 합류 후 master coder가 전체 실행: 기대 집합 green·미구현분 Red 유지=정상(바깥 루프 TDD 원형). **기대 green이 red = 통합 결함** → 귀속 |
| 3 | 홀리스틱 감사·백스톱 27종 | 최종 관문 무변 |

wave 0 walking skeleton이 acceptance를 첫 wave부터 «실행되는» 상태로 만들어 배선 결함 조기 검출.

### 7.3 충돌 해결 책임 매트릭스

| 충돌 유형 | 해결 주체 | 방식 |
|---|---|---|
| 텍스트 merge conflict | 유발 coder | main pull 후 자기 해소·재제출(CAID) |
| 소유 밖 파일 접촉·계약 위반 | coordinator 판정 → 해당 coder | 자동 해소 금지·정지 후 재작업 |
| 계약 자체 결함(설계 결함) | coordinator 개정·전 coder 전파 | 수리 코드 필요 시 master coder 투입 |
| 합류 후 통합 결함(acceptance red·semantic conflict) | master coder | 귀속 판정 — 단일 원인은 해당 coder 재배차·교차 원인은 직접 수리 |

질문 빈도 자체는 배차 전 계약 동결(Interfaces 블록·§5.4-⑹)로 낮추는 것이 전제 — 질문이 잦으면 slice 분할 실패의 신호로 본다.

### 7.4 합류 후 acceptance 실패의 처리 절차 (08-15 확정 방향)

1차 책임=master coder. 단 첫 일은 수리가 아니라 **귀속 판정**. 수리 주체는 원인 4종으로 갈린다:

| 원인 | 판별 신호 | 수리 주체 |
|---|---|---|
| ① 단일 슬라이스 결함 | 입장 표에서 한 use case 귀속·슬라이스 단독 재현 | 해당 coder(자기 worktree 수리→재합류) |
| ② 교차 결함 | 각자 green·조합에서만 실패(가정 불일치) | master coder 직접 수리 |
| ③ 계약·공유층 결함 | 양쪽 다 계약대로인데 실패 | coordinator 개정 판정 → master coder 공유층 수리 → 재배차 |
| ④ 테스트 자체 결함 | 테스트가 승인 계약을 잘못 옮김 | coordinator 판정 전용(spec 근거 필수 — 테스트 역주행 차단 현행 규율) |

**순차 합류=bisect**: «한 coder분씩 merge+즉시 merged-state 테스트» 규칙(§6-6) 덕에 실패는 특정 merge 단계에서 드러남 — 용의자는 «방금 슬라이스 단독 결함(①)» vs «조합(②)» 둘로 좁혀지고, 단독 재현 여부 확인 하나로 갈린다. big-bang이면 이 판별 자체가 불가능. 원칙: **원인 지식이 있는 좌석이 고친다**(전부 master에 몰면 직렬 병목 재생산·전부 coder에 돌리면 없는 context로 수리).

### 7.5 공용 부품을 coder 여럿이 각자 만든 경우 — 중복 통합의 주체

경우 구분: ⓐ **같은 공유 파일을 양쪽이 수정** — 배타 소유 목록+restricted 규칙 위반이라 발생 자체가 차단 대상(정지→coordinator 중재). ⓑ **같은 의미의 부품(값 객체·helper·스키마 등)을 각자 자기 슬라이스 파일에 따로 구현** — 파일 충돌도 게이트 실패도 없이 생기는 semantic 중복. 물음의 본체는 ⓑ.

**통합 주체 = master coder** (교차 사안 ②의 동형 — 어느 한 coder의 소유도 아님):
1. 검출: 합류 단계에서 master coder가 슬라이스 간 동형 부품 대조(+홀리스틱 감사의 «가까운 중복» 렌즈에 «슬라이스 간 중복» 명시 강화 — 병렬 신설 항목).
2. 판정: 같은 업무 의미인지 확인(같은 낱말·같은 규칙인가) — 애매하면 coordinator에 칸 판정 요청(«이 낱말의 뜻을 누가 정하나» 기준).
3. 통합: 하나를 정본으로 골라(또는 합성해) **공유 칸으로 승격**, 나머지 삭제, 양쪽 호출부 재배선 — 공유 칸은 master coder 소유 영역이라 권한 정합.
4. 재검증: merged-state 테스트+acceptance 기대 집합 재실행.

**예방 두 겹**:
- wave 0 설계에서 공용 부품을 미리 식별해 공유층에 선치(둘 이상의 슬라이스가 쓸 재료는 계약에 올림) — 설계 명세·리뷰 렌즈에 «공용 재료 식별» 항목 후보.
- 병렬 중 coder 규칙: 계약에 없는 공용 후보가 필요하면 **자기 슬라이스 사적 위치에만** 만들고 남의 슬라이스 것 참조 금지 — 참조가 없어야 합류 때 하나를 지우는 통합이 안전하다.

이 편성은 전역 지침 원칙 06(«성급한 추상화보다 중복 경계 — 같은 의미로 확인될 때 모은다»)과 정합: 병렬 중 중복을 허용하고, **합류점에서 같은 의미가 실증된 뒤** 하나로 모은다.

---

## 8. 전체 flow 종합 (08-15 확정 방향 — step 4 개정 문면의 뼈대)

### 8.1 slice 분할 기준 (coordinator)

| # | 기준 | 내용 |
|---|---|---|
| 1 | 단위 | use case vertical slice(현행 슬라이스 단위 유지) — layer 분할 금지 |
| 2 | 경계 | **파일 소유권 배타** — 슬라이스별 소유 파일 목록이 서로 교집합 0 |
| 3 | 강결합 | 같은 파일·순환 의존·긴밀 협력 슬라이스는 **같은 coder에 묶음**(억지로 쪼개지 않음) |
| 4 | 공유 | 둘 이상이 쓰는 재료(aggregate·값 객체·port 계약·스키마·배선)는 슬라이스에서 빼서 **wave 0으로 승격** |
| 5 | 크기 | 작게 유지(작은 단위일수록 conflict 확률 실측 하락) — 단 3번이 우선 |

### 8.2 흐름

```
G1 승인 설계 명세 + 입장 표
   │
   ▼
[coordinator] ① 슬라이스 추출(8.1 기준) ② 의존 그래프 → wave 편성(폭 ≤3)
   ③ 배차 명세 작성: objective·배타 소유 파일 목록·Interfaces(Consumes/Produces
     시그니처)·완료 조건 ④ 기계 검사: 소유 교집합 0·restricted 접촉 0
   ⑤ wave별 acceptance 기대 green 집합 도출(입장 표 매핑) ⑥ 조정 장부 기록
   │
   ▼
[acceptance-tester] 바깥 루프 Red 전량 생성(무변) — 통합선(main)에 상주
   │
   ▼
wave 0 [master coder 단독·직렬]
   공유층 구현 + walking skeleton(acceptance가 «실행되는» 상태) → 계약 동결 선언
   → 이후 공유 표면은 restricted
   │
   ▼
wave n [coder A·B·C 병렬 — 각자 worktree + 전용 테스트 DB]
   배차 명세 수령 → 내부 루프 TDD(Red→Green→Refactor) → 자기 슬라이스 테스트
   green + 층별 래칫 → 완료 보고(diff·증거는 파일 경유)
   규율: 소유 밖 파일 접촉 금지 / 계약에 없는 공용 후보는 사적 위치에만·남의
   슬라이스 참조 금지 / 막히면 정지·보고(자가 해석 금지 — 현행 규율)
   │
   ▼
[master coder] 합류 — 한 coder분씩 순차(=bisect):
   merge → merged-state 테스트(층별 green) → 슬라이스 경량 감사(merge 관문·
   다른 coder 작업과 파이프라인화) → acceptance 실행(기대 집합 대조) →
   슬라이스 간 중복 부품 대조·통합(공유 칸 승격·호출부 재배선)
   실패 시 귀속 판정(§7.4): ①단일 슬라이스→해당 coder ②교차→master 직접
   ③계약 결함→coordinator 개정 후 master 수리 ④테스트 결함→coordinator 전용
   text conflict → 유발 coder가 main pull 후 자기 해소
   │
   ▼
wave 완료: migrations 일괄 생성 → 장부 갱신 → [coordinator] 다음 wave 배차
   │ (wave 반복)
   ▼
전 wave 종료: 홀리스틱 감사 + 백스톱 27종 + G2 — 전부 무변
```

### 8.3 좌석별 책임 요약

| 좌석 | 쓰는 코드 | 판단 | 책임지는 실패 |
|---|---|---|---|
| coordinator | 없음(무변) | wave 편성·배차·계약 개정·귀속 상소·테스트 결함 판정 | 분할 품질(병렬 손익의 지배 변수) |
| master coder | 공유층·합류점·교차 수리 | 귀속 1차 판정·중복 통합 판정 | 통합선 green 유지·acceptance 기대 집합·중복 소멸 |
| coder | 자기 슬라이스만 | 없음(막히면 정지·보고) | 자기 슬라이스 테스트 green·배타 준수·conflict 자기 해소 |
