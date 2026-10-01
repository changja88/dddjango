# 운영자 확인 — Codex 공식 자료 조사(research.md) 원문 대조 · 새 후보 실측 (2026-10-01 20시)

## 1. 원문 대조(운영자가 직접 열람 · 2026-10-01)
| research.md 주장 | 원문 | 판정 |
|---|---|---|
| Q1-2 서브에이전트 기본 TTL 5분(구독에서도) · 메인은 구독 한도 안에서 1시간 | code.claude.com/docs/en/prompt-caching «Subagents fall outside the main-conversation TTL bucket, so they get five minutes even on a subscription until you choose a longer one» · TTL 표(Main 1h / Everything else 5m) | 맞음 |
| Q1-3 `subagentPromptCacheTtl` · `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL` · v2.1.242+ | 같은 문서 «Choose the TTL yourself» | 맞음. 우선순위: `FORCE_PROMPT_CACHING_5M` > 환경 변수 > 설정 > 서브에이전트 frontmatter `experimental.cacheTtl` > `ENABLE_PROMPT_CACHING_1H` > 기본값 |
| Q2-1 SendMessage 재개 = 대화 전체 유지 · 원래 실행이 데운 캐시를 읽을 수 있음 | code.claude.com/docs/en/sub-agents «Full conversation history» · «the resumed run can keep reading the prompt cache the original run warmed» | 맞음 |
| (research.md 에 없음) 플러그인 에이전트의 `experimental` 필드 | 같은 문서 «Plugin-provided subagents do not support the `experimental` field» | **플러그인 frontmatter 로는 TTL 을 못 바꾼다** — 사용자·프로젝트 설정 또는 환경 변수만 |

## 2. 새 후보 C13 — 서브에이전트 캐시 TTL 1시간(실측 · 8-C-0 설계자 기록)
- 자료: `~/.claude/projects/-Users-hyun--herdr-worktrees-spring-dream-server-lane-8-C-0/e3cf6de3-…/subagents/agent-a3a3f1f9205297541.jsonl`(읽기만 · 레인 진행 중이라 분석 때 1,455 → 지금 2,253 요청).
- 캐시 쓰기 32.2M 토큰 **전부 5분 TTL**(1시간 0). 쓰기 10만 토큰 넘는 요청 40회 = **재개 때 대화 전체 재기록**(회당 14만~93만 · 합 24.6M). 그 직전 공백: 5분 이하 1 · **5분~1시간 32** · 1시간 넘음 7.
- 시간: 25만 토큰 넘는 요청의 첫 응답(기록상 첫 블록까지) 중앙값 — 재기록 10.2초 · 캐시 적중 3.4초 → 32회 × 약 7초 ≈ **레인당 약 4분**(작다).
- 사용량: API 단가 비율(Opus 5.5 쓰기 5분 1.25 · 1시간 2.0 · 읽기 0.05 · 출력 5)로 환산하면 설계자 몫 **−13.7%**(1시간 쓰기 단가 상승 포함). 구독 한도 환산식은 공식 자료에 없다(research Q1-10) → 방향만 확실하다.
- 품질: 영향 없음(같은 대화 · 캐시만).
- 적용: 플러그인 안에서는 불가(위 1). 사용자 설정 한 줄 `"subagentPromptCacheTtl": "1h"`(사용자 `~/.claude/settings.json` 또는 현장 프로젝트 `.claude/settings.json`) 또는 환경 변수. 사용자 결정 사항.

## 3. research.md 후보 함의 — 운영자 요약
- (가) 설계자 새로 부르기 · (나) Codex `fork_turns="none"` · (다) 리팩토링 절 분리 · (라) 입력 크기 → 지연: 문서로 옵션 뜻·기본값은 확정, 순효과는 모두 실험 필요(research §3). 배포 뒤 첫 레인 실측 → 실험 순서 유지.
- Codex `fork_turns` 기본 = `all`(소스 `rust-v0.159.3`) — 우리 관찰(대화 통째 상속)과 일치. 동시 슬롯 기본 루트 포함 4 — K5b 와 일치. `wait_agent` 기본 30초(최소 10 · 최대 3,600) — K5(5분)와 모순 없음.
