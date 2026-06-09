# dddjango 스킬 연계 타임라인

위 → 아래 시간 흐름. `⛳` = 사용자 승인 게이트, `▶` = 결과/반송 흐름.

## Claude (`dddjango/`)

```
/dddjango
  │
coordinator (command)
  │
  ├─ G0 ⛳
  │
  ├─ Agent → design-architect            ─▶ design-spec(초안)
  │
  ├─ Agent → design-review-ddd ┐
  ├─ Agent → design-review-api ├ 병렬     ─▶ 리뷰노트
  ├─ Agent → design-review-db  ┘
  │
  ├─ Agent → design-architect            ─▶ design-spec(반영)
  │
  ├─ G1 ⛳
  │
  ├─ Agent → acceptance-tester           ─▶ 인수테스트(Red)
  │
  ├─ Agent → coder [슬라이스 1]           ─▶ 구현(Green)
  ├─ Agent → coder [슬라이스 N] …
  │     └ (슬라이스 ≥3) Agent → discipline-reviewer 경량
  │
  ├─ Agent → discipline-reviewer (홀리스틱)
  │
  ├─ 백스톱 16종 (셸)        ── exit 2 ▶ 설계로 반송
  │
  ├─ G2 ⛳
  │
  ▼
검증 보고
```

## Codex (`codex-dddjango/`)

```
/dddjango                       (config: multi_agent = true)
  │
coordinator (skill)
  │
  ├─ G0 ⛳ (평문)
  │
  ├─ spawn→wait: design-architect             ─▶ design-spec(초안)
  │
  ├─ spawn ×3 → wait → close:
  │     design-review-ddd / api / db (병렬)    ─▶ 리뷰노트
  │
  ├─ spawn→wait: design-architect             ─▶ design-spec(반영)
  │
  ├─ G1 ⛳ (평문)
  │
  ├─ spawn→wait: acceptance-tester            ─▶ 인수테스트(Red)
  │
  ├─ spawn→wait: coder [슬라이스 1]           ─▶ 구현(Green)
  ├─ spawn→wait: coder [슬라이스 N] …
  │     └ (슬라이스 ≥3) spawn→wait: discipline-reviewer 경량
  │
  ├─ spawn→wait: discipline-reviewer (홀리스틱)
  │
  ├─ 백스톱 16종 (셸)        ── exit 2 ▶ 설계로 반송
  │
  ├─ G2 ⛳ (평문)
  │
  ▼
검증 보고
```

## 연계 방식 차이 (이것뿐)

- Claude `Agent(역할)`  ↔  Codex `spawn_agent → wait_agent (→ close_agent)` + `multi_agent = true` 필요
