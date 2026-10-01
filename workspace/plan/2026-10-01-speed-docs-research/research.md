# 멀티 에이전트 플러그인 속도 조사 — Claude Code · Codex

## 1. 결론

1. **[문서 확인]** Claude 캐시는 긴 입력의 TTFT를 줄이지만, Opus 5.5의 200k–1M 입력에서 캐시 유무별 지연 곡선·전체 지연 감소율은 **[찾지 못함]**이다. 현재 평균값만으로 «입력이 커서 느리다»는 인과는 확정할 수 없다. → Q1-6~9, 후보 (라).
2. **[문서 확인]** Claude `SendMessage` 재개는 이전 대화를 유지하고 기존 캐시를 재사용할 수 있다. 서브에이전트의 기본 TTL은 5분이며, 새 일반 서브에이전트는 부모 캐시를 그대로 받지 않는다. → Q1-2, Q2-1~3.
3. **[소스 확인]** Codex 0.159.3 V2의 `fork_turns` 기본값은 `all`; `none`은 부모 대화 상속을 끊는다. 기본 동시 슬롯은 루트 포함 4개지만, 설정·실행 지침은 별도로 이어진다. → Q3-1~6.
4. **[문서 확인] + [추정]** 리팩토링 전용 절을 참조 파일로 옮기고 일반 실행에서 읽지 않게 하면, 호출된 코디네이터 본문에서 그 분량을 뺄 수 있다. 토큰 감소의 방향은 설명되지만 실제 속도 개선량은 실험이 필요하다. → Q4, 후보 (다).
5. **[문서 확인]** 긴 맥락의 품질 저하와 새 맥락·인계 산출물 사용에는 공식 근거가 있다. 그러나 설계자를 매 개정마다 새로 만드는 것이 dddjango의 속도·품질 모두에 유리하다는 결론은 **[추정]**이며 아직 검증되지 않았다. → Q2-6~7, 후보 (가).

## 조사 기준

- 확인일: **2026-10-01**. 표의 날짜는 조회일이며, 문서 발행일과 구분한다.
- 로컬 비교 대상은 brief가 제공한 **Claude Code 2.1.286 / Opus 5.5 / 1M**, **Codex CLI 0.159.3**이다. 실측 로그를 다시 분석하거나 벤치마크를 실행하지 않았다.
- `[문서 확인]`은 공식 설명, `[소스 확인]`은 고정된 공개 구현, `[추정]`은 그로부터의 해석·실험 제안, `[찾지 못함]`은 이번 조사로 확정할 수 없는 항목이다. 부재 표시는 해당 사실이 없다는 증명이 아니다.
- 공식 URL에서 이동한 `platform.claude.com`, `claude.com`, `learn.chatgpt.com`도 해당 공식 문서의 리다이렉트 목적지로 확인했다. 아래 링크는 지시서가 허용한 원래 공식 URL을 우선 사용한다. 제3자 자료는 사용하지 않았다.
- Codex 소스는 전부 **`rust-v0.159.3` → `01fc69f4026735edfdf6789820549727a4867b11`**에 고정했다. 릴리즈 화면은 9월 30일 게시로 표시한다. [S0]
- **소스 줄 표기 한계:** 아래 `rL`은 웹에서 열람한 raw 파일의 표시 줄이며 0부터 시작한다. 웹 도구의 빈 줄 정규화 때문에 GitHub 원본 줄번호와 같지 않다. 원본 줄번호는 확정하지 못했으므로 잘못된 `#L` 앵커를 만들지 않았다. 파일 경로·커밋·함수명·확인한 표시 줄을 함께 제공한다.
- 최신 문서는 계속 바뀐다. 특정 버전 요건이 적힌 항목은 함께 기록했지만, 현재 문서 전체를 Claude Code 2.1.286의 고정 스냅샷으로 간주하지 않는다. Codex 역시 공개 소스 기본값과 호스트의 실제 설정·도구 노출은 구분한다.

## 2. 질문별 답과 근거

### Q1. Claude 프롬프트 캐시와 지연

**캐시 읽기는 입력을 없애는 것이 아니라, 일치하는 접두부의 재계산을 줄이는 방식이다.** 비용 할인율을 지연 감소율이나 구독 한도 할인율로 대입하면 안 된다.

| ID | 주장·답 | 표지 | 출처·확인일 | 짧은 원문 인용 |
|---|---|---|---|---|
| Q1-1 | Claude Code가 캐시를 자동 관리한다. 동일 접두부를 재사용하며, 앞부분 변경 이후는 다시 계산한다. 파일별 독립 캐시가 아니다. | [문서 확인] | [C1] · 2026-10-01 | “handles prompt caching for you”; “match is exact” |
| Q1-2 | API TTL은 5분·1시간이며 적중 시 갱신된다. Claude Code 구독 포함 사용량의 **메인**은 기본 1시간, **서브에이전트 등은 기본 5분**이다. API 키·클라우드·usage credits에서는 기본 5분이다. | [문서 확인] | [C1] · 2026-10-01 | “One hour”; “Five minutes” |
| Q1-3 | TTL은 `promptCacheTtl` / `subagentPromptCacheTtl`, 또는 각각 `CLAUDE_CODE_PROMPT_CACHE_TTL` / `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL`로 선택한다. 두 버킷을 따로 설정하며 v2.1.242 이상이다. TTL 1시간 자체가 적중 요청을 더 빠르게 하지는 않는다. | [문서 확인] | [C1], [C2] · 2026-10-01 | C1: “Choose the TTL yourself”; C2: “same with respect to latency” |
| Q1-4 | Opus 5.5 API 표준 요금은 100만 토큰당 일반 입력 **$4**, 출력 **$20**, 5분 쓰기 **$5**, 1시간 쓰기 **$8**, 읽기 **$0.20**이다. 읽기는 **일반 입력의 5%**다. 다른 모델에 흔한 10%를 이 모델에 적용하면 틀린다. | [문서 확인] | [C3] · 2026-10-01 | “5% of the standard input price” |
| Q1-5 | API에서 전체 입력은 `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`다. Opus 5.5 등 대부분 모델에서 읽기는 **ITPM에서 제외**, 새 입력·캐시 쓰기는 포함한다. Haiku 3.5는 읽기도 포함하는 예외다. 이것이 요청 수 제한·출력 제한까지 없앤다는 뜻은 아니다. | [문서 확인] | [C4] · 2026-10-01 | “Do NOT count toward ITPM” |
| Q1-6 | 공식 과거 사례의 TTFT는 100k 토큰 책 대화에서 **11.5초→2.4초(-79%)**, 10k many-shot에서 **1.6초→1.1초(-31%)**, 긴 시스템 프롬프트의 10턴 대화에서 약 **10초→2.5초(-75%)**다. 서로 다른 작업이므로 입력 길이에 따른 단일 곡선으로 비교할 수 없다. | [문서 확인] | [C5] · 2026-10-01 | “time to first token” |
| Q1-7 | 같은 발표의 최대 85% 지연 감소는 구형 Claude 3 계열 시기의 설명이다. 위 표는 TTFT이며, Opus 5.5의 전체 요청 시간이나 525k 입력에 적용할 보장치가 아니다. 현재 페이지에는 2025-08-14와 본문 업데이트 2024-12-17이 함께 표시된다. 정확한 벤치마크 모델·환경 주석은 이번 열람에서 확인하지 못했다. | [문서 확인] / [찾지 못함] | [C5] · 2026-10-01 | “latency by up to 85%” |
| Q1-8 | 현재 API 문서는 긴 문서에서 TTFT 개선을 설명한다. 그러나 **Opus 5.5의 캐시 적중/미적중 × 200k·500k·1M에 대한 TTFT·출력 속도·전체 지연 수치나 함수는 찾지 못했다.** 캐시 적중 시 길이 영향이 0이라고도 결론 낼 수 없다. | [문서 확인] / [찾지 못함] | [C2]의 성능 설명 및 [C5] 확인 · 2026-10-01 | C2: “improved time-to-first-token” |
| Q1-9 | Claude 4.6 이후 모델은 1M 전체에서 표준 토큰 단가를 쓴다. Opus 5.5도 **200k 초과에 따른 단가 할증은 없다.** 동일 단가가 동일 지연을 뜻하지는 않으며, 길이별 지연은 별도 미확인이다. | [문서 확인] / [추정] | [C3] · 2026-10-01 | “at standard pricing” |
| Q1-10 | 구독에서도 긴 세션의 과거 대화 재읽기가 사용량을 소비한다. 다만 API의 5% 가격이나 ITPM 제외 규칙을 Pro·Max의 시간/주간 한도 산식으로 바꿀 **공식 환산식은 찾지 못했다.** 구독 잔여량은 `/usage`, 실제 과금 사용량은 해당 결제 방식으로 확인해야 한다. | [문서 확인] / [찾지 못함] | [C6] · 2026-10-01 | “still draws usage for the whole conversation” |

**실측과의 관계 — [추정]:** 메인 328k·14.8초와 다른 레인 140k·8.9초는 작업·출력·생각·도구·캐시 상태가 다른 관측이다. 설계자 525k·13.7초까지 단순 정렬하면 더 큰 입력의 요청이 오히려 짧은 사례도 생긴다. 이는 입력 영향이 없다는 증거도, 있다는 증거도 아니다. TTFT와 요청 종료 시간을 분리하고, 새 입력·캐시 쓰기·읽기를 별도로 측정해야 한다. 실험 항목은 후보 (라)에 정리했다.

### Q2. Claude Code 서브에이전트와 맥락

아래의 «새로 호출»은 **일반 custom subagent**를 뜻한다. 현재 문서의 `fork` 유형은 부모 대화를 물려받으므로 별개다.

| ID | 주장·답 | 표지 | 출처·확인일 | 짧은 원문 인용 |
|---|---|---|---|---|
| Q2-1 | 재개는 이전 도구 호출·결과·reasoning까지 유지한다. 완료된 에이전트에 `SendMessage`를 보내면 같은 ID로 새 실행을 시작한다. 따라서 20회 재개가 과거 입력 누적을 유지했다는 관찰과 부합한다. | [문서 확인] | [C7] · 2026-10-01 | “full conversation history” |
| Q2-2 | 재개 첫 요청은 원래 실행이 만든 캐시를 읽을 수 있다. 다만 TTL 만료·접두부 변경이 있으면 적중을 보장하지 않는다. 새 일반 서브에이전트는 부모와 프롬프트·도구가 달라 부모 캐시를 읽지 않고 자체 캐시를 형성한다. | [문서 확인] | [C1] · 2026-10-01 | “can read the cache” |
| Q2-3 | 새 일반 서브에이전트에는 자체 프롬프트·환경, 위임 메시지, CLAUDE.md 계층, git 상태, `skills`에 지정한 스킬 전문, 조건부 형제 에이전트 목록이 들어간다. 부모 대화·이미 읽은 파일·호출했던 스킬 이력은 자동 복사되지 않는다. | [문서 확인] | [C7] · 2026-10-01 | “Preloaded skills” |
| Q2-4 | custom agent는 보통 CLAUDE.md를 받는다. Explore·Plan 및 `omitClaudeMd`에는 예외가 있다. 사용할 도구는 에이전트 정의에 따른다. **모든 초기 입력의 고정 토큰 수**, 비-fork 자식에 전달되는 일반 스킬 카탈로그의 정확한 범위·크기는 찾지 못했다. | [문서 확인] / [찾지 못함] | [C7] · 2026-10-01 | “CLAUDE.md files”; “omitClaudeMd” |
| Q2-5 | 서브에이전트 compact는 메인과 같은 조건·로직이다. native 1M인 Opus 4.7 이후 등은 기본 약 **967k**에서 compact한다. 약 970k라는 실측과 부합한다. `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`는 해당 세션에서 임계점을 낮추는 용도이며 높이는 값은 무시한다. | [문서 확인] | [C7], [C8], [C9] · 2026-10-01 | C7: “same logic”; C8: “about 967K tokens”; C9: “can’t raise the threshold” |
| Q2-6 | Anthropic은 맥락이 커질수록 정보 회상 정확도가 저하하는 context rot를 설명하고, compaction·외부 메모·집중된 서브에이전트의 새 맥락을 제안한다. **Opus 5.5에서 525k를 넘으면 설계 품질이 얼마나 떨어지는지**의 정량 결과는 이 글에 없다. | [문서 확인] / [찾지 못함] | [C10] · 2026-10-01, 발행 2025-09-29 | “context rot”; “clean context windows” |
| Q2-7 | 장기 작업을 여러 맥락으로 나누되, 진행 상태·남은 요구·작업 산출물을 남겨 다음 세션이 복원하도록 하는 공식 지침이 있다. 새 맥락만 만들면 품질이 유지된다는 주장은 아니며, 인계 실패 사례도 설명한다. | [문서 확인] | [C11] · 2026-10-01, 발행 2025-11-26 | “leaving clear artifacts for the next session” |

**초기 크기의 해석 — [추정]:** `새 에이전트 = 입력 0`이 아니다. 역할 프롬프트·공통 프로젝트 지침·사전 적재 스킬·위임 자료만으로도 클 수 있다. API 가격표의 Opus 5.5 tool-use 시스템 오버헤드 **286토큰**은 도구 정의·메시지·프로젝트 지침을 제외한 값이므로, Claude Code 서브에이전트의 초기 크기로 사용할 수 없다. [문서 확인: C3, 2026-10-01, 원문 “Tool use system prompt tokens”]

### Q3. Codex 하위 에이전트 — 0.159.3 소스

`fork_turns`와 `collaboration.wait_agent`는 이번에 확인한 **MultiAgentV2** 경로다. V1의 `fork_context`, `wait_agent(targets=...)`, 기본 하위 스레드 6개와 섞지 않는다.

| ID | 주장·답 | 표지 | 출처·확인일·위치 | 짧은 원문 인용 |
|---|---|---|---|---|
| Q3-1 | `spawn_agent`에서 `fork_turns` 생략·공백은 `all`. `none`은 부모 대화 없이 시작, `all`은 전체 이력 fork, 양의 정수 **문자열**은 최근 N fork-turn이다. `0`은 오류이고 V2의 `fork_context`도 오류다. | [소스 확인] | [S1] `SpawnAgentArgs::fork_mode`, rL250–291 · 2026-10-01 | `.unwrap_or("all")`; `SpawnAgentForkMode::LastNTurns` |
| Q3-2 | N의 단위는 도구 호출 수가 아니다. 실제 사용자 메시지 또는 `trigger_turn=true`인 에이전트 통신을 경계로 센다. N이 전체보다 커도 pre-turn 시작 맥락은 잘린다. | [소스 확인] | [S2] `fork_turn_positions_in_rollout`, rL62–73; `truncate_rollout_to_last_n_fork_turns`, rL245–265 · 2026-10-01 | “a real user message boundary”; “drops pre-turn startup context” |
| Q3-3 | `none`도 부모의 현재 모델·effort·base instructions 등을 바탕으로 자식 설정을 만든다. 역할·허용된 override가 이를 바꿀 수 있다. **대화 상속 해제와 지침·실행환경 제거는 다르다.** | [소스 확인] | [S3] `build_agent_spawn_config` / `build_agent_shared_config`, rL102–146; [S4] 새 스레드 분기 rL704–734 · 2026-10-01 | S3: `build_agent_shared_config`; `config.base_instructions`; S4: `spawn_new_thread_with_source` |
| Q3-4 | `all`은 부모의 현재 모델 맥락을 읽고 reference context를 가능한 한 보존한다. 다만 이력 필터, developer 지침 교체, compacted history 정리가 있어 **원시 transcript의 byte-exact 복사라는 뜻은 아니다.** 과거 compact 이전의 삭제된 원문 복원도 보장하지 않는다. | [소스 확인] / [추정] | [S4] `spawn_forked_thread`, rL950–1005, rL1077–1187 · 2026-10-01 | `keep_forked_rollout_item`; “Full forks reuse the parent's reference context” |
| Q3-5 | 정식 설정명은 `agents.max_concurrent_threads_per_session`; 구명 `agents.max_threads`는 alias다. 이 값은 **동시에 열린 하위 스레드 수**다. V2 내부 `features.multi_agent_v2.max_concurrent_threads_per_session`은 **루트 포함 수**이며 기본 **4**다. 내부 설정이 우선하고, 없으면 agents 값에 1을 더한다. | [소스 확인] | [S5] `AgentsToml`, rL658–668; [S6] rL247–251, `resolve_multi_agent_v2_config` rL2563–2574 · 2026-10-01 | S5: `#[serde(alias = "max_threads")]`; S6: `.saturating_add(1)` |
| Q3-6 | V2에서 실제 하위 스레드 한도는 루트 포함 값에서 1을 뺀다. 기본이면 **루트 1 + 자식 3**으로, brief의 4슬롯 관찰과 일치한다. V1 fallback은 하위 6개다. 실제 호스트 설정을 조사하지 않았으므로 4를 모든 Codex 실행의 고정 상한으로 일반화하지 않는다. | [소스 확인] | [S6] `effective_agent_max_threads`, rL1490–1501; 기본 상수 rL247–251 · 2026-10-01 | `.saturating_sub(1)`; `Some(6)` |
| Q3-7 | V2 `wait_agent`는 특정 작업 완료만 기다리지 않는다. mailbox 활동 또는 새 사용자 입력으로 일찍 끝나며, timeout도 반환한다. 기본 **30초**, 최소 **10초**, 최대 **3,600초**다. 최소 미만은 올려 잡고 최대 초과는 오류다. 결과는 완료/중단/timeout 상태이며 에이전트 답변 본문 자체가 아니다. | [소스 확인] | [S7] rL47–69, rL116–145, `wait_for_activity` rL171–189; [S6] rL249–251 · 2026-10-01 | S7: “Wait interrupted by new input.”; “Wait timed out.” |
| Q3-8 | 공개 tool spec은 `message`, `task_name`, `fork_turns` 등을 구성하고, 모델·effort override 노출은 설정에 따라 달라진다. 현재 세션의 도구 설명·호스트 제한이 소스의 모든 선택지를 그대로 노출한다고 가정하면 안 된다. | [소스 확인] / [추정] | [S8] `create_spawn_agent_tool_v2`, rL90–111; [S1] rL252–259 · 2026-10-01 | `expose_spawn_agent_model_overrides` |

**AGENTS.md와 `none`:** [문서 확인] Codex는 작업 전 AGENTS.md를 읽는다([O2], 원문 “before doing any work”, 2026-10-01). [소스 확인] 새 자식도 일반 스레드 생성 경로를 타므로 대화 복사 해제를 AGENTS.md 비활성화로 해석할 수 없다([S4], Q3-3). **[찾지 못함]** 이번에는 `none` 자식의 AGENTS.md 재발견·기존 지침 재사용 전 경로를 줄 단위로 완결 추적하지 못했다. 정확한 초기 전문·중복 여부는 실제 요청으로 확인해야 한다.

#### Codex 대화 상속과 OpenAI 캐시

| ID | 주장·답 | 표지 | 출처·확인일 | 짧은 원문 인용 |
|---|---|---|---|---|
| Q3-9 | OpenAI 캐시는 숨은 지침·developer 메시지·도구·대화가 렌더링된 **전체 접두부 일치**를 요구한다. 모델·도구·effort·compact 변경이 적중에 영향을 줄 수 있다. | [문서 확인] | [O4] · 2026-10-01 | “entire rendered prefix to match” |
| Q3-10 | 전체 fork가 공통 접두부를 보존하면 캐시 재사용에 유리할 수 있다. 그러나 Q3-4의 지침·이력 변형과 캐시 라우팅·수명 때문에 **`all`이면 반드시 부모 캐시 적중**, **`none`이면 반드시 더 빠름** 모두 미확정이다. | [추정] | [S4], [O4] · 2026-10-01; 직접 보장 문구는 [찾지 못함] | S4: `preserve_context_baselines`; O4: “doesn’t guarantee a cache hit” |
| Q3-11 | 현재 OpenAI 문서는 `in_memory`가 보통 비활성 5–10분, 최대 1시간; `24h`가 보통 약 30분, 최대 24시간 유지될 수 있다고 설명한다. 모델·조직 정책에 따라 지원·기본값이 달라진다. 이는 Codex 해당 세션의 실효 TTL 확인값은 아니다. | [문서 확인] | [O4] · 2026-10-01 | “5 to 10 minutes”; “up to 24 hours” |
| Q3-12 | OpenAI API에서는 캐시 입력도 TPM에 포함한다. 출력은 매번 새로 생성하며 캐시가 출력 생성 방식을 바꾸지 않는다. Claude API의 cache-aware ITPM 규칙과 다르다. | [문서 확인] | [O4] · 2026-10-01 | “still count”; “does not change” |

#### Codex 자동 compact 조건

| ID | 주장·답 | 표지 | 출처·확인일·위치 | 짧은 원문 인용 |
|---|---|---|---|---|
| Q3-13 | `ModelInfo::auto_compact_token_limit()`은 모델 창의 **90%**와 명시 limit 중 작은 값을 사용한다. 창을 모르면 명시값만 쓴다. 이것만으로 실제 모든 실행의 compact 시점을 90%라고 단정할 수는 없다. | [소스 확인] | [S9] rL495–505 · 2026-10-01 | `(context_window * 9) / 10` |
| Q3-14 | `model_auto_compact_token_limit_scope`가 `Total`이면 전체 맥락, `BodyAfterPrefix`면 최초 prefix 이후 추가 토큰을 센다. fallback buffer가 있으면 scope limit에 더하고, 별도로 모델 창 × `effective_context_window_percent`의 전체 상한을 적용한다. | [소스 확인] | [S10] `context_window_token_status_with_config`, rL53–99 · 2026-10-01 | `BodyAfterPrefix`; `full_context_window_limit_reached` |
| Q3-15 | 턴 도중 후속 처리가 필요하고 토큰 상한 또는 명시적 새 창 요청이 있으면 auto compact를 실행한다. 턴 종료 시에도 `model_post_turn_compact_threshold_percent` 관련 조건이 따로 있다. 따라서 모델 정보·scope·buffer·설정 없이 하나의 고정 토큰 수를 제시할 수 없다. | [소스 확인] | [S11] rL543–598; [S10] rL100–105 · 2026-10-01 | S11: `needs_follow_up`; `run_auto_compact`; S10: `model_post_turn_compact_threshold_percent` |

### Q4. 스킬·참조 문서 로딩과 후보 (다)

| ID | 대상·언제 입력에 들어가는가 | 표지 | 출처·확인일 | 짧은 원문 인용 |
|---|---|---|---|---|
| Q4-1 | **Claude 스킬:** 일반 세션에서는 이름·설명으로 발견하고 본문은 호출 시 적재한다. `disable-model-invocation: true`이면 설명도 상시 입력에서 제외된다. 본문은 메시지로 남으며, 나중 턴마다 파일을 다시 읽는 구조는 아니다. | [문서 확인] | [C12] · 2026-10-01 | “full skill loads when invoked”; “does not re-read” |
| Q4-2 | **Claude 참조 파일:** SKILL.md 밖의 상세 자료는 필요할 때 읽게 할 수 있다. `references/`라는 이름만으로 자동 적재되지는 않는다. 다만 본문이 무조건 읽으라고 지시하거나 다른 경로로 주입하면 지연 로딩 효과가 없어진다. | [문서 확인] / [추정] | [C12] · 2026-10-01 | “only when needed” |
| Q4-3 | **Claude 커맨드:** 사용자 정의 slash command와 스킬은 통합된 메커니즘이다. 호출된 커맨드 본문은 대화에 들어간다. 따라서 본문 아래에 붙어 있는 미사용 분기 설명도 입력이다. | [문서 확인] / [추정] | [C12], [C1] · 2026-10-01 | C12: “merged into skills”; C1: “user messages” |
| Q4-4 | **Claude 에이전트:** 설명은 위임 선택에 쓰이고, 정의의 Markdown 본문은 해당 에이전트의 시스템 프롬프트가 된다. `skills` 필드로 미리 지정하면 그 스킬은 전문을 시작 시 적재한다. CLAUDE.md 여부는 Q2-4와 같다. | [문서 확인] | [C7], [C12] · 2026-10-01 | C7: “body becomes the system prompt”; C12: “injected at startup” |
| Q4-5 | **Claude 도구 정의:** 도구 전체가 언제나 모두 전문으로 실린다고 단정할 수 없다. 현재 문서는 MCP 도구 정의를 기본 지연 로딩하고, 사용 전에는 이름·서버 지침만 소비한다고 설명한다. | [문서 확인] | [C13] · 2026-10-01 | “deferred by default” |
| Q4-6 | **Codex 스킬:** 처음에는 이름·설명·파일 경로가 있고, 사용하기로 하면 SKILL.md 전문을 읽는다. 현재 문서의 초기 목록 예산은 모델 창의 **2%**, 창을 모르면 **8,000문자**다. 이 예산은 본문 크기 제한이 아니다. | [문서 확인] | [O1] · 2026-10-01 | “name and description”; “file path”; “full SKILL.md” |
| Q4-7 | **Codex 플러그인:** 스킬·MCP 등을 묶어 제공하며 스킬은 필요할 때 불러온다. 설치됐다는 이유로 모든 플러그인 SKILL.md·참조 파일의 전문이 자동 입력되는 것은 아니다. 참조를 실제로 읽는지는 선택한 스킬 지침·동작에 달렸다. | [문서 확인] / [추정] | [O3], [O1] · 2026-10-01 | O3: “load them when needed”; O1: “optional scripts and references” |
| Q4-8 | **Codex AGENTS.md:** 전역 지침과 프로젝트 루트→작업 디렉터리 방향의 지침을 조합한다. 프로젝트 문서 결합 상한은 `project_doc_max_bytes`, 기본 **32 KiB**다. SKILL.md에 적용되는 상한이나 토큰 수가 아니다. | [문서 확인] / [소스 확인] | [O2]; [S6] rL243–246 · 2026-10-01 | O2: “32 KiB by default”; S6: `AGENTS_MD_MAX_BYTES` |
| Q4-9 | **Codex 역할과 커맨드 비교:** Claude agents/*.md의 시스템 프롬프트 규칙을 그대로 옮기지 않는다. Codex는 역할 설정 및 developer 지침을 적용하는 별도 구현이다. 이 저장소 코디네이터는 `codex-dddjango/skills/dddjango/SKILL.md`이므로 스킬 적재 규칙이 직접 관련된다. | [소스 확인] / [추정] | [S3] rL122–153; [L2] · 2026-10-01 | S3: `config.developer_instructions`; L2: `name: dddjango` |

**후보 (다)의 적용 범위 — [추정]:** 효과 대상은 **코디네이터를 호출했지만 리팩토링 참조는 읽지 않는 실행**이다. 설치만 된 미호출 세션에는 24KB 전문이 원래 들어가지 않는다. 이미 읽은 대화는 파일 편집으로 과거 입력이 사라지지 않으므로 새 세션끼리 비교한다. [C12], [O1]

현재 워크트리를 읽어 확인한 위치는 다음과 같다. 이는 외부 공식 문서가 아닌 저장소 현황이며 변경은 하지 않았다.

| 로컬 대상 | 확인 위치·범위 | 확인값 | 표지·확인일 |
|---|---|---|---|
| [L1] Claude 코디네이터 | `dddjango/commands/dddjango.md:265`의 `## 리팩토링 모드`부터 EOF | UTF-8 **23,956 bytes** | [소스 확인] · 2026-10-01 |
| [L2] Codex 코디네이터 | `codex-dddjango/skills/dddjango/SKILL.md:283`의 같은 절부터 EOF | UTF-8 **23,825 bytes** | [소스 확인] · 2026-10-01 |

바이트 수를 토큰 수로 환산하지 않았다. 남겨야 할 안내 문구·참조 링크와 실제 토크나이저를 고려해야 순감소량을 알 수 있다. 또한 이 저장소 절에는 graph-owned 영역이 있으므로, 이 보고서는 이동 방법이나 실제 편집을 수행하지 않는다.

### Q5. 그 밖의 공식 속도 수단 — 짧게

| 수단 | 판단·제약 | 표지 | 출처·확인일 | 짧은 원문 인용 |
|---|---|---|---|---|
| 서브에이전트 TTL을 작업 간격에 맞추기 | 5분을 자주 넘기는 재개라면 1시간 TTL로 cold miss를 줄일 여지가 있다. 5분 안에서 계속 호출되는 경우 같은 적중 지연이고 쓰기 요금만 커질 수 있다. **품질 직접 저하 수단은 아님; 비용 영향 있음.** | [문서 확인] / [추정] | [C1], [C2] · 2026-10-01 | Q1-2~3의 원문·근거 참조 |
| 불필요한 모델 왕복·중복 출력 줄이기, 독립 작업 병렬화 | OpenAI는 출력 토큰·요청 횟수 감소와 병렬화를 권한다. 일반적 설명에서 입력 절반 축소의 지연 이득은 1–5%일 수 있다고 하지만 **거대한 맥락은 예외**라고 명시하므로 이번 525k에 이 수치를 적용하면 안 된다. **필수 검토 생략·출력 과도 축약은 품질 영향.** | [문서 확인] | [O5] · 2026-10-01 | “Make fewer requests”; “truly massive context sizes” |
| Claude fast mode | 공식 설명상 같은 모델 품질로 지연을 줄이고 비용을 높인다. 구독은 usage credits 사용 조건이며, 서브에이전트까지 동일하게 적용되는지는 이번 문서에서 확인하지 못했다. **비용 영향**. effort 하향은 별도로 **품질 영향**이 있다. | [문서 확인] / [찾지 못함] | [C14] · 2026-10-01 | “Same model quality”; “potentially lower quality” |

## 3. 후보 함의 표

아래는 **실험 제안 [추정]**이며 실제 변경·실험을 실행하지 않았다. 각 행의 문서 근거와 원문은 연결된 Q항목에 있다.

| 후보 | 문서가 말하는 것 | 판정 | 실험이 필요하면 무엇을 재야 하나 |
|---|---|---|---|
| **(가) 설계자를 개정마다 새로 호출** | 재개는 이력을 유지한다. 새 일반 에이전트는 초기 맥락부터 시작한다. 짧은 맥락·명시적 인계에는 근거가 있지만, 재개 캐시와 기존 판단 근거도 사라질 수 있다. Q2, [C7], [C10], [C11]. | **문서로 결론 남:** 맥락 수명·인계 필요성. **여전히 실험 필요:** 개정마다 초기화의 순속도·품질 효과. | 같은 개정 묶음으로 재개/신규를 비교한다. 모델·effort·도구·리뷰 기준은 고정한다. 최초 요청 및 전체 개정의 입력/읽기/쓰기, TTFT, 종료 시간, 요청 수, 재탐색·재독 시간, compact 횟수·시간, 누락 요구·반복 지적·재작업을 측정한다. 신규에는 최신 명세·미해결 리뷰·결정 이유를 전달하고 그 인계 비용도 포함한다. |
| **(나) Codex 설계자·구현자의 대화 상속 해제** | `none`으로 대화 상속은 끊을 수 있으나 공통 지침·실행 설정은 남는다. 접두부 캐시 이득도 달라질 수 있다. Q3-1~4, Q3-9~12, [S1], [S3], [S4], [O4]. | **문서로 결론 남:** 옵션 의미·기본값. **여전히 실험 필요:** 이 플러그인의 순지연·품질. | `all`/`none`에 같은 승인 스코프·파일·계약을 전달한다. 자식 최초 입력과 `cached_tokens`, 준비/생성 시간, 이후 총 요청·출력·완료 시간을 측정한다. 부모에만 있던 제약 누락·중복 조사·승인 해석 오류도 검수한다. 모델/effort를 함께 바꾸지 않는다. |
| **(다) 리팩토링 전용 약 24KB를 참조 파일로 분리** | 호출 시 본문은 들어가지만 별도 참조는 필요할 때 읽게 할 수 있다. 일반 코디네이터 실행에서 그 절을 실제로 읽지 않으면 입력을 줄일 근거가 있다. Q4, [C12], [O1], [L1], [L2]. | **문서로 결론 남:** 조건부 적재에 따른 본문 제외. **여전히 실험 필요:** 실제 토큰 순감소·지연 및 규칙 누락 여부. | 새 세션의 일반 실행/리팩토링 실행을 각각 전후 비교한다. 최초 입력 토큰·캐시 쓰기/읽기, 참조 Read 유무, 다음 요청들의 입력·TTFT·전체 시간을 기록한다. 일반 경로의 무조건 참조 읽기와 리팩토링 경로의 적재 누락을 함께 확인한다. |
| **(라) 입력 크기→지연 인과** | 캐시는 재처리를 줄이지만 출력·왕복도 지연을 만든다. 현행 모델의 200k–1M 캐시별 곡선은 미확인이다. Q1-6~10, [C2], [C5], [O5]. | **문서로 결론 안 남. 여전히 실험 필요.** 레인 간 평균 비교만으로 인과를 판정할 수 없다. | 동일 작업의 맥락 길이를 달리하고 cold/warm을 구분한다. 입력 140k·328k·525k 등, 같은 모델/effort/출력 목표/도구/동시성으로 반복·순서 교차한다. 입력 총량뿐 아니라 새 입력·쓰기·읽기, 첫 이벤트·첫 모델 토큰·첫 가시 출력·종료 시각, 출력/공개되는 reasoning 토큰, 도구 대기·429/재시도·compact를 기록한다. 요청 단위와 전체 작업 단위의 p50/p95를 따로 비교한다. |

측정 시 추가 주의 — **[추정]**:

- Anthropic의 `input_tokens`만 전체 입력으로 쓰면 캐시를 제외한 수치가 된다. Q1-5의 세 범주 합과 원래 brief의 «평균 입력» 정의를 먼저 맞춰야 한다. OpenAI의 캐시 입력은 전체 입력 안의 상세치이므로 같은 방식으로 덧셈하면 안 된다. [C4], [O4]
- TTFT의 시작·끝을 고정해야 한다. 스트림 첫 이벤트, 생각 시작, 사용자에게 보이는 첫 글자는 서로 다를 수 있다. TTFT 감소와 전체 완료 시간 감소를 각각 보고한다.
- «재개 20회»와 «모델 요청 1,455회»는 다른 단위다. 재개 전후 최초 요청만 빨라져도 전체 요청·도구·생각 시간이 그대로면 개정 전체 이득은 작을 수 있다.
- warm 여부는 시간 간격만으로 선언하지 말고 응답의 캐시 토큰으로 판정한다. 한 번의 `all`/`none` 또는 분리 전후 실행만으로 원인을 확정하지 않는다.
- 초기화의 이득은 compact 감소와 재탐색 증가를 함께 포함한 **동일 품질 달성까지의 전체 시간**으로 평가한다. 이 보고서는 임의의 통과 기준이나 품질 동등성을 가정하지 않는다.

## 4. 출처 목록

모두 **2026-10-01 확인**. 날짜가 따로 없는 문서는 계속 갱신되는 현행 문서이며 로컬 버전 전용 스냅샷은 아니다. 표의 `[C…]`, `[O…]`, `[S…]`는 아래 URL로 연결된다.

### Claude 공식 문서·발표

- [C1] **How Claude Code uses prompt caching** — 자동 적용·TTL·서브에이전트 캐시. TTL 설정은 v2.1.242 이상.
- [C2] **Prompt caching** — Claude API의 TTL·TTFT 설명. `docs.anthropic.com`에서 `platform.claude.com`으로 이동.
- [C3] **Pricing** — Opus 5.5 표준·캐시 단가, 1M 가격, tool-use 오버헤드.
- [C4] **Rate limits** — cache-aware ITPM 및 입력 사용량 필드.
- [C5] **Prompt caching with Claude** — 과거 TTFT 사례. 현재 리다이렉트 페이지 표시는 **2025-08-14**, 본문 GA 업데이트는 **2024-12-17**이며 구형 Claude 3 계열 내용이다. 날짜 불일치를 해소하지 못했으므로 최신 벤치마크로 취급하지 않았다.
- [C6] **Manage costs effectively** — 긴 대화가 구독 사용량에도 미치는 영향·사용량 확인.
- [C7] **Create custom subagents** — 초기 맥락·재개·compact·fork. 일부 기능에는 문서 내 버전 조건이 있다.
- [C8] **Model configuration** — native 1M의 약 967k compact 기본값·설정별 예외.
- [C9] **Environment variables** — `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` 적용 조건.
- [C10] **Effective context engineering for AI agents** — **2025-09-29 발행**.
- [C11] **Effective harnesses for long-running agents** — **2025-11-26 발행**, Opus 4.5/Agent SDK를 예로 든 장기 작업 지침.
- [C12] **Extend Claude with skills** — 스킬·커맨드·참조 파일의 적재 수명.
- [C13] **How Claude Code works** — 맥락 관리와 도구 지연 로딩.
- [C14] **Speed up responses with fast mode** — 속도·가격·품질 및 사용 조건.

### OpenAI 공식 문서

- [O1] **Build skills** — `developers.openai.com/codex/skills`에서 공식 Learn 문서로 이동. 점진적 적재·초기 목록 예산.
- [O2] **Custom instructions with AGENTS.md** — 지침 탐색·`project_doc_max_bytes`.
- [O3] **Plugins** — 플러그인 제공 스킬의 필요 시 적재.
- [O4] **Prompt caching** — 렌더링 접두부, 모델별 차이, TTL·캐시 토큰·TPM. 구형 OpenAI 설명을 일괄 적용하지 않고 현행 문서에서 확인했다. Codex 구독 한도 산식의 출처로 사용하지 않았다.
- [O5] **Latency optimization** — 입력·출력·왕복·병렬화의 일반적 지연 지침. 거대 맥락 예외를 명시한다.

### Codex 고정 소스

아래 파일은 모두 `openai/codex`의 **`rust-v0.159.3` / `01fc69f4026735edfdf6789820549727a4867b11`**이다. 링크는 그 커밋의 raw 소스를 가리킨다. 확인 줄은 Q3의 `rL` 표기를 참조한다.

| ID | 파일 경로·주요 확인 내용 |
|---|---|
| [S0] | `releases/tag/rust-v0.159.3` — 태그·커밋 연결 |
| [S1] | `codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs` — 옵션 파싱·기본값 |
| [S2] | `codex-rs/core/src/thread_rollout_truncation.rs` — fork-turn 경계·최근 N턴 |
| [S3] | `codex-rs/core/src/agent/child_config.rs` — 자식 설정·지침 상속 |
| [S4] | `codex-rs/core/src/agent/control/spawn.rs` — 신규/전체 fork 경로·이력 정리 |
| [S5] | `codex-rs/config/src/config_toml.rs` — agents 설정명·alias |
| [S6] | `codex-rs/core/src/config/mod.rs` — 슬롯·wait 기본값·설정 우선순위 |
| [S7] | `codex-rs/core/src/tools/handlers/multi_agents_v2/wait.rs` — 대기·중단·timeout |
| [S8] | `codex-rs/core/src/tools/handlers/multi_agents_spec.rs` — 호스트별 도구 옵션 노출 |
| [S9] | `codex-rs/protocol/src/openai_models.rs` — 모델별 compact 기본 limit 계산 |
| [S10] | `codex-rs/core/src/session/context_window.rs` — 실제 토큰 scope·상한 계산 |
| [S11] | `codex-rs/core/src/session/turn.rs` — 턴 중 auto compact 실행 조건 |

### 로컬 확인

- [L1] `dddjango/commands/dddjango.md` — 현재 워크트리의 265행부터 EOF.
- [L2] `codex-dddjango/skills/dddjango/SKILL.md` — 현재 워크트리의 283행부터 EOF 및 frontmatter.
- 실측·설치 버전의 출처는 같은 폴더의 [brief.md](brief.md)다. 공식 성능 수치와 섞지 않았다.

## 5. 확신이 낮은 것·못 찾은 것

1. **[찾지 못함] 현행 모델의 지연 곡선:** Opus 5.5의 200k–1M에서 cached/uncached별 TTFT·decode 속도·전체 지연. 85%나 구형 100k 사례로 외삽하지 않았다.
2. **[찾지 못함] 구독의 정확한 사용량 환산:** Claude cache read 토큰을 Pro·Max 시간/주간 한도에 몇 배로 계산하는지. API 5% 가격과 API ITPM 제외를 구독 공식 산식으로 취급하지 않았다.
3. **[찾지 못함] 실제 첫 프롬프트의 크기:** Claude 신규 서브에이전트·Codex `none` 자식의 초기 토큰 수, 일반 스킬 목록·도구 정의·프로젝트 지침의 정확한 합. 모델·활성 도구·역할·호스트에 따라 달라 실제 요청 확인이 필요하다.
4. **[찾지 못함] 캐시 적중 보장:** Codex `all` 첫 요청의 부모 캐시 적중률 및 이 환경의 실효 TTL. Claude 재개 또한 TTL·prefix 조건부다.
5. **[찾지 못함] 버전 완전 일치:** Claude 2.1.286 내부 구현을 고정 소스로 대조하지 못했다. 현행 공식 문서와의 비교다. Codex 공개 0.159.3 소스는 고정했으나 실제 호스트 override를 조회하지 않았다.
6. **[찾지 못함] GitHub 원본 줄번호:** 웹 raw 표시 줄과 원본의 차이를 해소하지 못했다. 경로·커밋·함수·rL은 확인했으며 원본 줄번호를 꾸며 넣지 않았다.
7. **[찾지 못함] `none`과 AGENTS.md의 전체 초기화 경로:** 대화 복사와 설정 상속은 확인했지만 지침 재발견·재사용의 끝까지는 추적하지 못했다.
8. **[찾지 못함] 후보별 순효과:** 매 개정 신규 설계자, Codex 상속 해제, 24KB 분리가 이 플러그인의 동일 품질 완료 시간을 얼마나 줄이는지. 이번 작업은 공식 자료 조사이며 변경·성능 실험은 수행하지 않았다.

실측과 명백히 어긋나는 결과는 발견하지 않았다. **970k compact와 Codex 4슬롯은 각각 현행 문서·V2 기본값과 부합**한다. 다만 «이어 깨우면 항상 cache hit», «Codex all은 원시 대화의 완전 복사», «캐시 입력은 무료», «1M는 반드시 할증» 같은 확대 해석은 위 근거와 맞지 않는다.

Serena·Graphify·서브에이전트는 조사 지시서에 따라 사용하지 않았다. 결과물은 이 `research.md` 하나이며 코드·플러그인 문서·설정 변경, 커밋·push는 수행하지 않았다.

[C1]: https://code.claude.com/docs/en/prompt-caching
[C2]: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
[C3]: https://docs.anthropic.com/en/docs/about-claude/pricing
[C4]: https://docs.anthropic.com/en/api/rate-limits
[C5]: https://www.anthropic.com/news/prompt-caching
[C6]: https://code.claude.com/docs/en/costs
[C7]: https://code.claude.com/docs/en/sub-agents
[C8]: https://code.claude.com/docs/en/model-config
[C9]: https://code.claude.com/docs/en/env-vars
[C10]: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
[C11]: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
[C12]: https://code.claude.com/docs/en/skills
[C13]: https://code.claude.com/docs/en/how-claude-code-works
[C14]: https://code.claude.com/docs/en/fast-mode
[O1]: https://developers.openai.com/codex/skills
[O2]: https://developers.openai.com/codex/guides/agents-md
[O3]: https://developers.openai.com/codex/plugins
[O4]: https://platform.openai.com/docs/guides/prompt-caching
[O5]: https://developers.openai.com/api/docs/guides/latency-optimization
[S0]: https://github.com/openai/codex/releases/tag/rust-v0.159.3
[S1]: https://raw.githubusercontent.com/openai/codex/01fc69f4026735edfdf6789820549727a4867b11/codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs
[S2]: https://raw.githubusercontent.com/openai/codex/01fc69f4026735edfdf6789820549727a4867b11/codex-rs/core/src/thread_rollout_truncation.rs
[S3]: https://raw.githubusercontent.com/openai/codex/01fc69f4026735edfdf6789820549727a4867b11/codex-rs/core/src/agent/child_config.rs
[S4]: https://raw.githubusercontent.com/openai/codex/01fc69f4026735edfdf6789820549727a4867b11/codex-rs/core/src/agent/control/spawn.rs
[S5]: https://raw.githubusercontent.com/openai/codex/01fc69f4026735edfdf6789820549727a4867b11/codex-rs/config/src/config_toml.rs
[S6]: https://raw.githubusercontent.com/openai/codex/01fc69f4026735edfdf6789820549727a4867b11/codex-rs/core/src/config/mod.rs
[S7]: https://raw.githubusercontent.com/openai/codex/01fc69f4026735edfdf6789820549727a4867b11/codex-rs/core/src/tools/handlers/multi_agents_v2/wait.rs
[S8]: https://raw.githubusercontent.com/openai/codex/01fc69f4026735edfdf6789820549727a4867b11/codex-rs/core/src/tools/handlers/multi_agents_spec.rs
[S9]: https://raw.githubusercontent.com/openai/codex/01fc69f4026735edfdf6789820549727a4867b11/codex-rs/protocol/src/openai_models.rs
[S10]: https://raw.githubusercontent.com/openai/codex/01fc69f4026735edfdf6789820549727a4867b11/codex-rs/core/src/session/context_window.rs
[S11]: https://raw.githubusercontent.com/openai/codex/01fc69f4026735edfdf6789820549727a4867b11/codex-rs/core/src/session/turn.rs
[L1]: ../../../dddjango/commands/dddjango.md
[L2]: ../../../codex-dddjango/skills/dddjango/SKILL.md

REPORT-DONE
