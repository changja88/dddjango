# dddjango Codex 이식 — 사전 조사 결과

> 작성 2026-05-28 · 상태: **조사 완료, 빌드 착수 전 결정 대기** · 정본 보강: `workspace/DEVLOG.md`
> 목적: dddjango(현재 Claude Code 전용 v1.0.0)를 **Codex(OpenAI Codex CLI)용으로 동일하게** 만들 수 있는지/어떻게 만들지 결정. 이 문서는 조사·권고이며 구현물은 만들지 않았다.

---

## 0. 요약 (go/no-go)

**GO — 권고: Codex 네이티브 플러그인으로 이식(옵션 A).** 현행 Codex CLI(2026-05)는 과거와 완전히 다르다. **네이티브 서브에이전트(GA·병렬), Skills(SKILL.md), Plugins+Marketplace(`.codex-plugin/plugin.json`), `codex exec`(JSON/스키마), MCP**를 모두 갖춰 Claude Code 구조와 거의 1:1로 대응한다. 과거 Codex 버전이 실패한 이유는 "Codex에 오케스트레이션 메커니즘이 없어서"였는데, **그 메커니즘이 이제 GA로 존재**한다. 자산의 ~65%(지식 코퍼스·파이프라인 개념·subagent 역할 본문)는 그대로 재사용 가능하다.

**단 하나의 실질 격차**: Codex 승인 게이트는 **binary(approve/deny)** 뿐 — Claude `AskUserQuestion`(선택지 제시) 등가물이 없다. dddjango의 G0/G1/G2 게이트(승인/수정 + 배치 선택)는 코디네이터가 **평문 질문 후 사용자 답을 파싱**하는 방식으로 우회해야 한다.

**반복 금지 함정**: 과거의 `workflow-dddjango-subagents` 스킬은 진짜 실행 없이 "sequential fallback(단일 컨텍스트 역할극) + 방대한 거버넌스 보일러플레이트"로 퇴화했다. 새 버전은 이걸 버리고 **네이티브 서브에이전트로 실제 디스패치**한다.

---

## 1. R1 — Codex CLI 현행 역량 매핑 (외부 문서 근거)

조사자 지식 컷오프(2026-01) 이후 Codex가 크게 진화. 아래는 현행 공식 문서 기준.

| Claude Code 메커니즘 | Codex 등가물 (현행) | 출처 | 격차/리스크 |
|---|---|---|---|
| **`Agent` 서브에이전트 디스패치** | **툴 API 존재**: `spawn_agent`/`wait_agent`/`close_agent`(config `[features] multi_agent = true` 필요). 빌트인 `default`/`worker`/`explorer` + 커스텀 에이전트. `/agent`로 관리 | codex/subagents · superpowers `codex-tools.md` | 자연어 트리거 + **툴 호출 둘 다 가능**. superpowers가 `Task→spawn_agent` 매핑을 실제 사용 → 과거 우려보다 결정성 양호. 역할 라우팅은 PoC로 확인 |
| **병렬 Agent 호출** | 네이티브 동시 실행. `agents.max_threads`(기본 6), `agents.max_depth`(기본 1) | codex/subagents · config-reference | depth=1=직속 자식만. **dddjango는 코디네이터→7리프로 flat(depth 1)이라 충분** |
| **비대화형 실행(서브에이전트 본문 실행)** | **`codex exec`**: `--json`(JSONL), `--output-schema`, `-o`, `--sandbox`, `resume`. `--full-auto` deprecated(→`--sandbox`) | codex/noninteractive · cli/reference | 외부 오케스트레이션 백본으로 적합 |
| **`AskUserQuestion`(선택지 게이트)** | **없음**. 승인 정책 `untrusted/on-request/on-failure/never` + `/plan`·`/approve`는 **binary** | codex/agent-approvals-security | ⚠️ **유일한 실질 격차** — 평문 질문+답 파싱으로 우회 |
| **`/dddjango` 슬래시 커맨드(진입점)** | 커스텀 프롬프트(`~/.codex/prompts/`, `/prompts:이름`)는 **deprecated** → **Skills 권장** | codex/custom-prompts · skills | 진입점을 **코디네이터 Skill**로 구현 |
| **Skill(참조 지식 로딩)** | **네이티브 Skills**: `SKILL.md`(frontmatter `name`·`description`) + `references/`·`scripts/`·`assets/`, progressive disclosure. `~/.codex/skills/` 또는 `.codex/skills/` | codex/skills | Claude Skill과 **거의 1:1, 직접 포팅** |
| `AGENTS.md` 프로젝트 지침 | 읽음. home→루트→cwd concat(cwd 우선), `AGENTS.override.md`는 대체. **32 KiB 한도** | codex/guides/agents-md | 큰 지침은 Skill references로 분리 |
| `TodoWrite` 진행 추적 | 등가 UI 미확인 | — | 로그 출력으로 강등(기능 영향 적음) |
| 플러그인 매니페스트 | **`.codex-plugin/plugin.json`**(skills/mcp/apps/hooks 번들 + `interface`). 마켓플레이스 `marketplace.json`@`.agents/plugins/`, `codex marketplace add` | codex/plugins · plugins/build | ✅ **확정: 플러그인은 커스텀 에이전트를 번들 못 함**(매니페스트에 `agents` 항목 없음, `skills/mcpServers/apps/hooks/interface`만). → 7역할은 **스킬로 배포 + 즉석 spawn 인라인 주입**(아래 §6) |
| MCP | **클라이언트 지원**(`[mcp_servers.*]`). Codex-as-MCP-server는 미확정 | codex/mcp · agents-sdk | 확장 경로. 서버모드 불확실 |
| 모델/토큰 | 기본 **GPT-5.5, 1M 창**. API는 `gpt-5.2-codex`. `model_reasoning_effort` 조정 | codex/models | 1M 창=Claude와 유사 운영. 캐싱 세부 미확인 |

### Codex 멀티에이전트 파이프라인 구현 3방법 (성숙도 순)
- **① 네이티브 서브에이전트 + Skill + Plugin** — 성숙도 高. Claude 구조와 최유사. 리스크: NL 트리거 결정성, binary 게이트.
- **② `codex exec` 외부 셸 오케스트레이션** — 성숙도 高, 결정성·게이트 자유도 最高. 리스크: 단일 세션 UX 상실, 세션 격리로 컨텍스트 명시 전달, 토큰 증가.
- **③ MCP + OpenAI Agents SDK** — 성숙도 中·불확실(Codex-as-MCP-server 1차 출처 미확정). 가장 강력하나 복잡.

---

## 2. R2 — 폐기된 Codex 구조 포스트모템 (git `911cd22^`)

삭제 커밋 `911cd22`(2026-05-25 "Remove Codex plugin output and governance; reset to source corpus"). 삭제 직전 트리에서 회수.

### 과거 구조
- `dddjango/.codex-plugin/plugin.json`(v0.1.10) — **형식은 현행 Codex 규격과 일치**(`skills: "./skills/"` + `interface` 객체). 재사용 가능.
- 스킬별 `agents/openai.yaml` — 실은 **인터페이스 디스크립터**(display_name/short_description/default_prompt)일 뿐, **실행 가능한 서브에이전트가 아님**.
- `workflow-dddjango-subagents` 스킬(+`role-map.md`·`delegation-rules.md`·`handoff-contract.md`·`integration-checklist.md`) — 역할맵·핸드오프·통합 체크리스트를 **프롬프트 규약**으로 정의.
- `.agents/plugins/marketplace.json`(name `dddjango-local`, source `local`) — 형식 현행과 일치.
- `workspace/plan/{constraint_rules.md, plugin_build_plan.md, validator/}`, `ADR-0001`(P0-P8 scope), `source-reference-audit` 스킬 — 거버넌스/평가 인프라.

### 결정적 실패 증거 (스모킹건)
`workflow-dddjango-subagents/SKILL.md` 본문에 박힌 자백:
> *"Selecting this workflow does not authorize real subagent execution; without explicit request or approval, use **sequential fallback**."*
> *"`## Sequential Fallback` section은 정확히 이 한 문장으로 시작한다: `Real subagents were not executed; this is sequential fallback in the role order below.`"*

즉 당시 Codex엔 신뢰할 실제 서브에이전트 실행이 없어, 오케스트레이션이 **단일 컨텍스트 안에서 역할을 순차로 흉내내고(sequential fallback)**, 그 모호함을 메우려 **방대한 출력 보일러플레이트(Role Map/Handoff Contract/Integration Checklist/honesty footer/cache-sync report)** 와 **별도 validator·eval 인프라(P0~P8)** 를 쌓았다. 실행 제어 경계가 없으니 거버넌스만 비대해지고 품질이 수렴하지 못함. → Claude 재구축이 **명령형 코디네이터 + 네이티브 서브에이전트**로 갈아타 성공(smoke8 합격, 20/20).

### 가져올 것 / 버릴 것 / 함정
- **가져올 것**: `.codex-plugin/plugin.json`·`.agents/plugins/marketplace.json` **형식**(현행 유효), 스킬 `interface` 메타(default_prompt 한국어 문구 등), 지식 코퍼스(이미 Claude판이 계승).
- **버릴 것**: `workflow-dddjango-subagents`(역할극+보일러플레이트), `delegation-rules`/`handoff-contract`/`integration-checklist` 거버넌스, `source-reference-audit`, validator·eval 인프라.
- **반복 금지 함정**: ① "sequential fallback"으로 후퇴하지 말고 **네이티브 서브에이전트로 실제 디스패치**. ② 실행 모호함을 거버넌스 문서로 덮지 말 것. ③ 정직성 푸터·cache-sync 보일러플레이트로 본문(런타임 프롬프트)을 오염시키지 말 것.

---

## 3. R3 — 자산 인벤토리 분류

| 자산 | 분류 | Codex 이식 작업 |
|---|---|---|
| 코퍼스 11개 `references/final.md`(DDD/구현/규율) | **중립** | 그대로. Codex Skill `references/`로 배치 |
| 파이프라인 개념(G0/G1/G2·역할·이중루프 TDD·수정 모드) | **중립** | 코디네이터 Skill 본문으로 채용 |
| subagent 7개 **본문**(역할 지시) | **중립** | **역할별 Skill로 패키징**(플러그인이 에이전트를 번들 못 하므로). 코디네이터가 worker/explorer를 spawn할 때 해당 역할 Skill 본문을 **인라인 지시문으로 주입** |
| subagent/skill **frontmatter**(`tools`/`skills`) | 부분종속 | Codex 규격(SKILL.md frontmatter / agent TOML)으로 형식 변환 |
| Coordinator 게이트(`AskUserQuestion`) | 부분종속 | 평문 질문+답 파싱으로 재설계 |
| Coordinator `Agent` 디스패치·병렬 | 부분종속 | Codex 네이티브 서브에이전트(명령형 지시)로 재작성 |
| `TodoWrite` 진행 추적 | 부분종속 | 로그 출력으로 강등 |
| `.claude-plugin/plugin.json` 매니페스트 | 완전종속 | `.codex-plugin/plugin.json` + `.agents/plugins/marketplace.json`로 변환(과거 형식 재활용) |

**코퍼스 동기화 메모**: 현재도 배포본(`dddjango/skills/.../final.md`)과 소스 미러(`workspace/reference/.../reference/final.md`)가 완전 byte-identical은 아님(해시 상이; 소스에 `## P1` 헤더 가산 추정). Codex판 추가 시 코퍼스가 **3벌**(Claude 배포본 / 소스 / Codex 배포본)이 되므로, **소스 코퍼스 단일 진실 + 빌드시 양 플러그인으로 생성/동기화** 전략을 빌드 단계에서 확정해야 한다(아래 미해결 질문).

---

## 4. R4 — 아키텍처 옵션 + 권고

### 옵션 비교
| | A. Codex 네이티브 플러그인 | B. `codex exec` 외부 오케스트레이션 | C. P9 유지(보류) |
|---|---|---|---|
| 구성 | 코디네이터 Skill + 7 커스텀 에이전트 TOML + `.codex-plugin` + marketplace | 셸/파이썬이 단계별 `codex exec` 호출, 병렬은 프로세스 병렬 | 현 Claude판만 유지 |
| Claude판 유사성 | **최상** (구조 1:1) | 낮음(외부 조립) | — |
| 결정성/게이트 자유도 | 중(NL 트리거, binary 게이트 우회) | **최상**(스크립트가 게이트 완전 통제) | — |
| UX | Codex 단일 세션, `/스킬` 진입 | 별도 CLI 실행 흐름 | — |
| 비용 | Claude판과 유사 | 세션 격리로 토큰↑ | 0 |
| 성숙도/리스크 | 高 / NL 결정성·subagent 번들 미확정 | 高 / UX·컨텍스트 전달 | 무 |
| 배포 | Codex 마켓플레이스 | 배포물 아님(레포 스크립트) | — |

### 권고: **옵션 A (Codex 네이티브 플러그인)**, B의 게이트 기법을 부분 차용
이유 — 과거 실패의 원인(실행 메커니즘 부재)이 해소됐고, A가 성공한 Claude 아키텍처와 1:1이라 검증된 설계를 재사용한다. 격차는 다음으로 메운다:
- **게이트(최우선)**: 코디네이터 Skill이 G0/G1/G2에서 **평문으로 요약+질문**하고 사용자 답을 파싱(승인/수정, 배치 선택). binary 승인 정책에 의존하지 않음. (B의 "스크립트가 직접 게이트" 발상을 Skill 안의 대화로 차용.)
- **디스패치 결정성**: 코디네이터 본문에 "지금 이 N개 에이전트를 병렬로 spawn하라"를 **명령형**으로 강하게 기술. smoke 런으로 실제 spawn 여부 검증.
- **depth/병렬**: dddjango는 코디네이터→리프로 flat(depth 1)이라 기본값으로 충분. 리뷰 3종 병렬은 `max_threads`(기본6) 내.
- **진행 추적**: TodoWrite 없이 평문 상태 한 줄.

### 후속 빌드 계획 개요 (승인 후 별도 계획) — 사용자 결정 반영
**확정 결정**: ① 레포는 **현 레포와 동일**(별도 레포 분리 안 함, 코퍼스 공유 단순화). ② **게이트 UX는 필수** — 평문 질문+답 파싱 게이트를 반드시 구현. ③ 7역할 배포는 **스킬 + 즉석 spawn**(아래 §6 확정).

1. 레포 내 Codex 플러그인 디렉터리(예: `codex-dddjango/`)를 Claude `dddjango/`와 공존시킴. 소스 코퍼스(`workspace/reference/`)를 단일 진실로 두고 양 플러그인으로 생성/동기화.
2. 코퍼스 11개 → Codex Skill `references/`로 이식(소스 단일 진실에서 생성).
3. subagent 7개 본문 → **역할별 Skill로 패키징**(TOML 에이전트 파일 아님). 코디네이터가 worker/explorer spawn 시 역할 Skill 본문을 인라인 주입.
4. 코디네이터(=`/dddjango` 진입) → 코디네이터 Skill로 작성: 모드 판별 + G0/G1/G2(**평문 게이트 필수**) + 명령형 서브에이전트 디스패치(병렬 리뷰) + 이중루프 TDD + 수정 모드.
5. 매니페스트(`.codex-plugin/plugin.json`) + 마켓플레이스 작성(과거 형식 재활용·갱신).
6. **smoke PoC 먼저**(최소 1기능, 예: "재고 있을 때만 주문 생성")로 핵심 가정 2개 검증: ⓐ 명령형 디스패치+인라인 역할 주입으로 7역할이 실제 분리 실행되는가(역할 라우팅 신뢰성, max_threads=6이라 1개는 큐잉) ⓑ 평문 게이트 UX 동작. PoC 통과 후 전체 이식.

---

## 5. 결정 완료 + 남은 질문

**결정 완료 (2026-05-28)**
1. ✅ **subagent 배포** — 플러그인은 커스텀 에이전트를 번들 못 함이 확정. → **역할 본문을 Skill로 배포 + 코디네이터가 즉석 spawn에 인라인 주입**(§6). 플러그인 1회 설치로 전부 배포됨.
2. ✅ **레포 전략** — **현 레포와 동일**(분리 안 함). 코퍼스 단일 진실 공유.
3. ✅ **게이트 UX** — **필수**. 평문 질문+답 파싱 게이트 구현.

**남은 질문 (PoC/빌드 중 확정)**
- 역할 라우팅 신뢰성: 인라인 주입 spawn으로 7역할이 안정적으로 분리 실행되는지(공식 권장 패턴 명문화 약함, known issue openai/codex#15250·#18823). PoC 핵심 검증 항목.
- `max_threads` 기본 6 — 리뷰 3종 병렬은 여유. 단 전체 7역할 동시 fan-out 시 1개 큐잉(설계상 순차 단계라 문제 적음).
- Codex-as-MCP-server / Agents SDK(옵션 C) — 현 단계 불필요. PoC가 인라인 spawn으로 충분하면 미도입.
- 캐싱/비용 세부 — 비용 비교 필요시 추가 조사.

---

## 6. 7역할 배포 메커니즘 (확정)

Codex 플러그인 매니페스트(`.codex-plugin/plugin.json`)는 `skills/mcpServers/apps/hooks/interface`만 번들하고 **`agents` 항목이 없다**(출처: codex/plugins/build). 커스텀 에이전트는 `config.toml`의 `agents.<name>`로 선언하는 모델이라 플러그인으로 자동 배포되지 않으며, 레포 `.codex/agents/*.toml` 커밋의 자동 인식도 공식 미확정 + 툴-백 세션에선 이름 호출 불가(openai/codex#15250).

→ **채택**: 7역할 지시문을 **Skill(또는 references 파일)로 패키징**해 플러그인에 번들(스킬 배포가 Codex의 1급 공식 경로). 코디네이터가 내장 `worker`/`explorer`/`default`를 spawn할 때 해당 역할 Skill 본문을 **인라인 developer instructions로 주입**한다. 이는 #15250이 기술한 실제 동작 경로와 일치하며, 설치 후 사용자 수작업이 0이다.

트레이드오프: 전용 커스텀 에이전트만큼 역할 격리가 강제되진 않으므로(라우팅이 프롬프트/스킬 description 품질에 의존), 코디네이터 지시를 명령형으로 강하게 쓰고 PoC로 검증한다.

---

## 7. superpowers 참고 — 동일 문제를 이미 푼 레퍼런스 구현

obra/superpowers(Jesse Vincent)는 **하나의 레포에서 스킬 본문을 공유하며 Claude/Codex/Cursor/Gemini/OpenCode/Copilot 멀티 런타임을 지원**한다. 로컬 설치본(`~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/`)을 직접 분석해 우리가 쓸 구체 패턴을 회수했다.

### 7.1 멀티 런타임 동일-레포 모델 (우리 "동일 레포" 결정과 정합)
- 런타임별 매니페스트를 **한 레포에 공존**: `.claude-plugin/`, `.codex-plugin/plugin.json`, `.cursor-plugin/`, `.opencode/`, `gemini-extension.json`. **스킬 본문(`skills/*/SKILL.md`)은 런타임 공유**(단일 진실).
- **배포 채널은 별도**: `scripts/sync-to-codex-plugin.sh`가 자기 레포 → **OpenAI 마켓플레이스 포크 레포 `prime-radiant-inc/openai-codex-plugins`** 의 `plugins/superpowers/`로 rsync 후 PR을 연다. 즉 **저작은 동일 레포, Codex 배포는 OpenAI 마켓플레이스 레포에 PR**. (우리 "동일 레포" 결정은 저작 기준 충족; Codex 배포 채널은 빌드 시 별도 결정 필요.)

### 7.2 Codex 플러그인이 싣는 것 / 안 싣는 것 (sync 스크립트 EXCLUDES 근거)
- **싣음**: `.codex-plugin/plugin.json` + `skills/` + `assets/`. 스킬별 `agents/openai.yaml`(인터페이스 디스크립터, 마켓플레이스가 OpenAI 소유로 보존) — **과거 dddjango Codex 구조의 `agents/openai.yaml`이 현행에서도 유효**함을 확인.
- **안 실음**: `commands/`, `hooks/`, `docs/`, `lib/`, `scripts/`, `tests/`, 루트 ceremony(`AGENTS.md`·`CLAUDE.md`·`GEMINI.md`·`package.json`), 타 런타임 매니페스트.
- 함의: **`/dddjango` 커맨드는 Codex에선 반드시 Skill로**(commands/ 미배포 — R1의 "custom prompts deprecated→Skills"와 정합). **부트스트랩 hook도 Codex엔 안 실림** → 진입 강제는 스킬 description 트리거/AGENTS.md로.

### 7.3 Claude→Codex 툴 어댑터 (superpowers `codex-tools.md` 근거)
스킬 본문은 Claude 툴 이름을 쓰고, 런타임이 등가물로 해석한다. 우리 agent/command 본문 이식 시 그대로 채용:

| Claude(스킬 표기) | Codex 등가 |
|---|---|
| `Task`/Agent 디스패치 | `spawn_agent` (`[features] multi_agent = true`) |
| 병렬 다중 Task | 다중 `spawn_agent` |
| Task 결과 수신 | `wait_agent` |
| Task 종료 | `close_agent`(슬롯 해제) |
| `TodoWrite` | `update_plan` |
| `Skill` 호출 | 네이티브 로드 — 지시만 따름 |
| `Read`/`Write`/`Edit` | 네이티브 파일 툴 |
| `Bash` | 네이티브 셸 |

→ **TodoWrite는 강등이 아니라 `update_plan`으로 1:1 매핑**(앞 §1 표 갱신 필요 없음, 등가 존재). 서브에이전트도 `wait_agent`/`close_agent`로 **결과 수집·슬롯 관리가 명시적**이라 과거의 "sequential fallback" 함정을 피할 실제 메커니즘이 있다.

### 7.4 스킬 저작 관례 (writing-skills, 우리 코어 텍스트 작성에 적용)
- `description`은 **"Use when…" 트리거 중심**(절차 요약 금지 — 요약하면 모델이 본문 대신 description만 따름). 3인칭, ≤500자.
- **Progressive disclosure**: SKILL.md는 가볍게(<500줄), 무거운 레퍼런스(코퍼스 `final.md`)는 한 단계 깊이 `references/`로 분리, 100줄+엔 목차. `@` 강제 로드 금지(컨텍스트 폭증). — 우리 코퍼스 11개 구조와 정합.
- **rigid 스킬엔 회피로 봉쇄 + Red Flags**: dddjango의 "메커니즘 대체 금지" 가드레일은 규칙만 적지 말고 흔한 합리화를 Red Flags로 나열해 차단.
- **스킬을 서브에이전트 압박 시나리오로 TDD 검증**("실패 테스트 없으면 스킬 없음") — 우리 smoke 검증 관행을 스킬 자체 검증으로 정식화 가능.

### 7.5 이식 타임라인 주의 (superpowers 블로그 근거)
superpowers 4(2025-12-18) 시점엔 **Codex가 서브에이전트 미지원**이라 subagent-driven 워크플로 전제가 깨졌다고 기록 — 이후 GA. 우리 R1/R2와 일치하며, **서브에이전트 신뢰성은 버전 의존적이므로 PoC 우선 원칙을 재확인**한다.

---

## 부록 — 근거 경로
- 현 Claude판: `dddjango/`(commands·agents·skills), `.claude-plugin/marketplace.json`(name `changja88`)
- 파이프라인 명세: `workspace/design/2026-05-26-dddjango-plugin-pipeline-design.md`
- 과거 Codex 구조: `git show 911cd22^:dddjango/.codex-plugin/plugin.json`, `...:dddjango/skills/workflow-dddjango-subagents/SKILL.md`, `git show 911cd22^:.agents/plugins/marketplace.json`
- 이력 정본: `workspace/DEVLOG.md`(DR-01 Codex 폐기, P9 이월)
- Codex 공식 문서: developers.openai.com/codex/{subagents, skills, plugins, plugins/build, noninteractive, cli/reference, agent-approvals-security, guides/agents-md, config-reference, models, mcp}
