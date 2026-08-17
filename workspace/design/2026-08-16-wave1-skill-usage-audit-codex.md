# 웨이브 1 스킬 사용 감사 — Codex 세션 (증거 문서)

> 2026-08-16 실시. broccoli-server-rebuild 웨이브 1에서 codex판 dddjango 플러그인이 의도한 대로
> 스킬이 사용됐는지, Codex 쪽 세션(llm_meta 워커 트리 · child_settings 교차 리뷰어)의 rollout 을
> 감사한 서브에이전트 보고 전문이다. 후속 개정(codex 역할 경계 조임 등)의 증거 앵커로 쓴다.

---

## 0. 감사 대상 식별 결과

설치본은 `~/.codex/plugins/cache/changja88-dddjango/dddjango/2.11.0/` (marketplace rev `7a1d352` = 소스 미러 HEAD)이며, `diff -rq` 결과 소스 미러(`/Users/hyun/Desktop/dddjango/codex-dddjango/skills/`)와 **완전 동일** — 설치본 기준 감사와 미러 기준 감사가 등가다.

**세션 1 — llm_meta 리빌드 워커**: "재시작 여러 개"가 아니라 **메인 1 + spawn_agent 서브에이전트 8의 세션 트리**였다 (session_meta의 `parent_thread_id`로 확정):

| rollout (~/.codex/sessions/2026/08/16/) | 정체 | 크기 |
|---|---|---|
| `rollout-…T12-56-08-…6f26….jsonl` | 메인(워커=Coordinator) `01a008b6-6f26` | 4.96MB |
| `…T13-01-23-…3b9e…` | SUB `/root/llm_meta_design` (design-architect) | 3.4MB |
| `…T13-30-20/28/36-…` | SUB `review_ddd` / `review_api` / `review_db` | 1.2/1.0/1.5MB |
| `…T13-36-37-…7cf7…` | SUB `review_discipline` | 3.2MB |
| `…T14-14-18-…fc3f…` | SUB `acceptance_red` | 1.0MB |
| `…T14-23-14-…2d20…` | SUB `llm_meta_coder` | 4.3MB |
| `…T15-04-20-…cc53…` | SUB `final_code_review` | 2.3MB |

**세션 2 — child_settings XR**: `rollout-…T17-27-23-…c3a6….jsonl` (1.9MB, cwd `rebuild-child-settings`, 첫 메시지 "너는 웨이브 1 child_settings BC의 교차 리뷰어(적대적 감사)다"). 각 큰 파일에 딸린 소형 파일들은 도구 호출 승인을 심사하는 Codex 내부 approval-assessor 그림자 세션으로 감사 대상이 아니다.

## 1. 기대치 (정본 `dddjango/SKILL.md` + 역할 스킬 «로드할 지식 스킬» 절)

| 역할 | 로드해야 할 스킬 |
|---|---|
| Coordinator | 오케스트레이터 본문(재적재 금지) · 역할은 전부 spawn 위임 · G0 빚스캔+refactor-scope.md · build_anchor 1회 기록 · 리뷰 다발 «전부 spawn 후 wait»(discipline lightweight 합류) · G2에서 registry_gate `--anchor` |
| design-architect | dddjango-architecture-ddd · architecture-api · architecture-db · dddjango-discipline-houserules(+references/final.md) · discipline-tdd |
| design-review-ddd | dddjango-architecture-ddd |
| design-review-api / -db | architecture-api / architecture-db + discipline-tdd |
| acceptance-tester | discipline-tdd 먼저 → dddjango-implementation-test · architecture-api · dddjango-architecture-ddd |
| coder | discipline-tdd 먼저 → implementation-test · implementation-django(-ninja/-web) · implementation-python · discipline-cleancode · discipline-houserules — «승인 작업에 맞게 골라» |
| discipline-reviewer | discipline-cleancode · discipline-tdd · implementation-test · discipline-houserules(final.md 직접 대조) |

## 2. 세션 1 판정 — llm_meta 워커 트리

### (a) 파이프라인 골격: 높은 수준으로 준수
- 트래커 라인·게이트 배너 실사용: `dddjango · 요구·스코프 [1/4]` → `G0 스코프 승인` 배너(13:00:52) → **build_anchor를 첫 dispatch(13:01:23 architect spawn) 전에 full SHA로 1회 기록·커밋**(13:00:53, `6629fe28…`).
- Phase 1: architect spawn → lens 리뷰어 3종 연속 spawn(13:30:20/28/36) 후 wait → 4렌즈 blocker로 **G1 반송** → architect 반영 → G1을 `request_user_input` 게이트로 제시(14:10) → 조정자 승인.
- Phase 2: acceptance(14:14) → coder(14:23, 외부 계약 Red 14건 확인 후 진행) → 규율 감사 **G2 불가 판정(#92/#97)** → 조용히 고치지 않고 **G1′ STOP → `request_user_input` A/B 제시 → A안 승인 → coder가 Red→Green 집행**(모범적 반송 축 작동) → `registry_gate.py . --anchor 6629fe28…` 반복 실행 → G2 자가 게이트 보고 → 조정자 수용.

### (b) 스킬 로드 실태: 기대치 대비 사실상 전량 일치
**모든 서브에이전트가 세션 첫 셸 호출([1])에서 자기 역할 SKILL.md를 설치본 경로에서 로드했다** — spawn 지시("역할 스킬 X를 로드해 그 역할로 작동하라")가 충실히 집행된 결정적 증거다.

- design: 기대 5종 전부 로드([1] design-architect SKILL, [5]~[6] architecture-ddd/api/db/houserules/tdd, [31]~[34] references/final.md를 rg 목차→sed 절 단위 **부분 적재**).
- review_ddd/api/db: 각자 기대 스킬 정확히 로드. **review_db는 [25]에서 동결 사본과 플러그인 references의 `cmp`를 실측해 byte 동일(`architecture_cmp=0`)을 확인** — 모범 사례.
- review_discipline: 기대 4종 전부 + 백스톱 4종(registry_gate·check-public-surface-annotation·check-layer-skeleton·check-choices-literal-consumption) 직접 실행.
- acceptance: 기대 4종 전부([1]에서 discipline-tdd를 acceptance SKILL과 함께 최우선 로드).
- coder: 기대 8종 중 7종 로드. **implementation-django-ninja만 미로드 — llm_meta는 OHS 전용(HTTP 어댑터 없음)이라 «골라 쓴다» 계약상 정당한 생략**(과소 아님). check-public-surface-annotation.py 소스까지 정독([154]~[156])해 면제 규칙을 확인.
- final_code_review: discipline-reviewer 역할 스킬 + 기대 지식 4종 + registry_gate/checker 실행.

### 누락/과잉/방식위반 (증거)
1. **[누락] `refactor-scope.md` 부재** — Phase 0 빚 스캔(27종 exact command·exit 기록)이 수행되지 않았다(`.dddjango/20260816-rebuild-llm_meta/`에 scope.md·design.md·build_anchor만 존재). 「증거 없는 빚 0은 G0 blocker」 문면 위반. 정상 참작: 그린필드 리빌드 worktree + 발주서가 G0을 선결정.
2. **[경계 위반] 메인이 `design.md`를 직접 패치**(16:27, §8 입장표 갱신 — MAIN rollout의 patch_apply 2건 중 하나). 「design-spec은 architect 전속」 위반. 정상 참작: G1′ A안 승인문이 "design.md 갱신"을 지시했으나 집행 주체 선택이 어긋났다.
3. **[방식위반·경미] 리뷰 다발 분할** — discipline reviewer가 3 lens와 동시가 아닌 6분 뒤(13:36) 합류. 단 세션이 사유를 발화함: "동시 슬롯 한계가 메인 포함 4라 lens 리뷰 3종을 먼저 병렬 실행" — 플랫폼 제약 + 보고 동반.
4. **[과잉] 코디네이터의 월경 적재** — 메인이 coder·acceptance용 지식 스킬(implementation-django+references, implementation-test, discipline-tdd 등)을 직접 정독([97]~[106])하고, superpowers 스킬 6종(using-superpowers·TDD·subagent-driven·requesting/receiving-code-review·systematic-debugging)과 graphify 전문(650줄+)도 적재. 역할 경계상 불필요한 컨텍스트 비용.
5. **[방식·경미] 오케스트레이터 본문 2회 적재**([1] 전문 + [7]~[11] 슬라이스 재적재) — 단 codex엔 본문 자동 주입이 없어 1회차는 필수이며 2회차는 출력 절단 재시도로 보임.
6. **[참고] 앵커 이원화** — review_discipline·final_code_review는 `--anchor 50344f9a`(G1 문서 커밋)로 내부 감사, 최종 게이트 판정은 메인이 build_anchor(`6629fe28`)로 재실행. 차분 세탁은 아니나 앵커가 역할 간에 달랐다.

### (c) 특이 사항
- **규율 «값»은 동결 사본(`rebuild/specs/discipline/` 5파일, 전 세션이 전문 정독), 파이프라인 «절차·역할·입장표·백스톱»은 플러그인 스킬** — 이원 체제로 소비됐고, 동결 사본과 플러그인 references가 byte-identical(현재도 `cmp` 통과)이라 실질 충돌 없음.
- 자기지식 진행 정황 없음 — 오히려 컨텍스트 압축 후 역할 SKILL 재적재가 반복(SKILL 22행의 «압축·유실 시 재읽기 우선» 규정에 부합).

### 종합 판정: **의도대로 (경미 이탈 3건 — refactor-scope.md 부재, design.md 직접 패치, 다발 분할)**

## 3. 세션 2 판정 — child_settings XR (`01a009ae-c3a6`)

이 세션은 플러그인 파이프라인 역할이 아니라 발주 워크플로의 교차 리뷰어다(플러그인에 대응 역할 스킬 없음). 기대치의 정본은 XR 브리프(동결 5파일 + scope.md Source 절)다.

- **(a) 골격**: 파이프라인 골격 비적용(서브에이전트 0·게이트 0). 브리프 절차(정본 정독 → 5렌즈 대조 → 비-DB 실측 → 지정 절대 경로 보고 → 재검 라운드)는 준수. 실측: pytest collect-only + `-m 'not django_db'`, manage.py check, makemigrations --check, ruff, OpenAPI export. 초회 M1~M4·m1 반송 → 재검 **PASS(blocker 0·major 0·minor 0)**, 보고서 바이트 일치까지 검증.
- **(b) 스킬 로드**: 동결 5파일 **전문 정독**([13]~[20], nl -ba 전량 — 브리프 지시 부합)이 1차, 플러그인은 보충 — architecture-api·architecture-db·dddjango-discipline-houserules·dddjango-implementation-test의 SKILL.md + references/final.md를 § 단위 부분 적재([21][22][59]~[64]). discipline-cleancode·discipline-tdd 플러그인판 미로드는 동결 사본이 동일 내용(byte-identical)이라 실질 누락 아님.
- **(c) 특이**: ① 적대 감사에 가장 근접한 `dddjango-discipline-reviewer`(백스톱 사각·거짓지적 방지 목록 소유)를 읽지 않았다 — 위반은 아니나 아쉬운 미활용. ② **백스톱 check-*.py·registry_gate 미실행** — 정적 검사라 «비-DB 실측» 제약에 안 걸렸는데도 육안 대조만 했다(repo 내 registry_gate 존재를 rg로 탐색만 [28]). 결정적 백스톱 없는 PASS 판정은 llm_meta 쪽 감사 체계보다 약하다.

### 종합 판정: **의도대로 (브리프 기준 준수 · 플러그인 백스톱 미활용은 재량 범위이나 개선 여지)**

## codex판 특유 패턴 3줄
1. **스킬 로드 = 셸 sed/nl 수동 파일 읽기** — 네이티브 본문 주입이 없어 오케스트레이터 본문조차 수동 적재이며, 컨텍스트 압축 후 같은 SKILL 재적재가 구조적으로 반복된다(«본문 재적재 금지» 전제가 codex에선 성립 조건부).
2. **spawn 지시문이 rollout에 암호화(gAAAA…)로 기록**돼 부모 쪽에서 지시 감사가 불가 — 준수 여부는 자식 rollout의 첫 행동(역할 SKILL 로드)으로 역증해야 하며, 이번엔 8/8 전부 첫 호출이 역할 SKILL 로드였다.
3. **동시 슬롯 한계(4)와 followup_task 재사용**이 claude판 문면을 변형한다 — 리뷰 다발이 3+1로 쪼개지고, architect 반영·재리뷰가 «재spawn» 대신 동일 스레드 followup으로 집행됐다(기능 등가·문면 이탈). 부수적으로 openai-curated superpowers·graphify가 병설돼 플러그인 밖 스킬 전문 적재가 모든 세션의 최대 과잉 항목이었다.
