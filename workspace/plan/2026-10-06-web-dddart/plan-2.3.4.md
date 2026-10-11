# dddjango-web 2.3.4 — Codex 일꾼 기다리기는 긴 대기 한 번 (10-11)

## 바탕
- 바탕: R main `a73dfadc`(dddjango-web 2.3.3). 2.3.4 는 패치 — Codex Coordinator `SKILL.md` 「Codex 실행 모델」 절에 문단 하나만 더한다. Claude 쪽 글 · 역할 · references · scripts · 검사 86종은 그대로다(Claude 런타임에는 `wait_agent` 가 없다). 매니페스트 판은 `make release-web` 이 올린다.
- 사본: `<S>/web-wait-1`. `<S>` = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad`. 시험 기록 `<S>/loadab/`(`criteria-wait.md` · `w/measure.json`).
- 사용자 결정: 10-11 «이거 두개는 수리가 가능한지 확인해줘» → 시험 → «우선 배포는 바로해» · «우선 고칠수 있는것은 수리 진행해».

## 근거(측정)
- 현장 web 레인 넷: 일꾼이 끝났는지 계속 확인 14.5h / 164.6h(8.8% · 2,864번 · 걸음당 18초). 플러그인 · 레인 지침에 기다리는 시간 규칙 0. Codex 0.160 기본 안내에 «prefer longer waits (minutes)» 가 있는데도 레인이 고른 대기는 10 ~ 60초.
- 공지 목록 A/B(B1b): `wait_agent` 39번 · 10초 8 · 50초 31 · 39번 모두 «Wait timed out.» 로 돌아옴 — 작은 일감에서도 재현.
- 작은 시험(실행 전 기준 고정 · `criteria-wait.md`):
  - 상한 확인: `wait_agent` `timeout_ms` 600000 한 번 → 152초 뒤 «Wait completed.» — 긴 대기를 막는 상한 없음.
  - 일꾼 4분 일: 안내 글 없음 = 대기 5 · 5 · 9번(10 ~ 60초) / 안내 글 있음 = 1 · 1 · 1번(600000) · 답 6/6 · 벽시계 263 vs 265초 → 재현 · 효과(−80%) · 정답 · 시간 기준 모두 통과.

## 넣은 것
| 자리 | 글 |
|---|---|
| `codex-dddjango-web/skills/dddjango-web/SKILL.md` 「Codex 실행 모델」 목록 셋째 | **일꾼 기다리기**: `wait_agent`는 `timeout_ms`를 길게(600000 이상) 준다 — 일꾼이 끝나면 그 전에 돌아온다. 시간이 다 돼 돌아와도(`timed_out`) 실패가 아니니 같은 긴 시간으로 다시 기다리고, 기다리는 사이에 다른 확인을 끼워 넣지 않는다. |
| `AGENTS.md` | dddjango-web 단락 «2.3.4부터 …» 한 문장 · 정본 목록에 이 문서 |

## 넣지 않은 것
- «오래 걸리는 명령은 길게 한 번에 기다리기»(1초 간격 들여다보기 · 현장 12.3h · 7.5%): 작은 시험에서 1초 간격이 재현되지 않아(안내 글 없이도 20 ~ 50초 간격 3번) 기준상 판정 보류 — 신호는 3 → 1. 현장에서 생긴 워크트리 기록으로 재현을 따로 검토한다(사용자 10-11 «1초 간격 들여보기는 재현을 다시 해봐»).
- dddjango(core) Codex 판의 같은 문단: 이번 요청 범위 밖(후보).

## 검증
| 실행 | 결과 | 증거 |
|---|---|---|
| `make verify-web` |  |  |
| `make verify` |  |  |
| 독립 검토(Codex · Claude) |  |  |
