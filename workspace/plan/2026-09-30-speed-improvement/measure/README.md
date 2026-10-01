# 레인 실측 — 배포한 버전의 첫 레인을 옛 버전 기준과 비교 (2026-10-01 준비)

도구: `workspace/tools/lane_metrics.py`(읽기 전용 — 세션 기록만 읽고, `--repo` 를 주면 레인 워크트리에서 `git log`·`git cat-file` 만 쓴다).

## 1. 새 레인이 끝나면 — 명령 두 줄

```bash
# core(Claude Code) 레인: 프로젝트 기록 폴더 = ~/.claude/projects/ 아래 레인 워크트리 경로를 '-' 로 바꾼 이름
python3 workspace/tools/lane_metrics.py claude ~/.claude/projects/-Users-hyun--herdr-worktrees-spring-dream-server-<레인> \
    --since <G0 시작> --until <착륙> --repo ~/.herdr/worktrees/spring_dream_server/<레인> --out new-core.json
python3 workspace/tools/lane_metrics.py compare workspace/plan/2026-09-30-speed-improvement/measure/base-8C0-core-2.18.4.json new-core.json --md compare-core.md

# web(Codex) 레인: 레인 워크트리 경로로 ~/.codex/sessions 의 rollout 을 고른다
python3 workspace/tools/lane_metrics.py codex ~/.herdr/worktrees/spring_dream_server/<레인> \
    --since <G0 시작> --until <착륙> --repo ~/.herdr/worktrees/spring_dream_server/<레인> --build <빌드 폴더> --out new-web.json
python3 workspace/tools/lane_metrics.py compare workspace/plan/2026-09-30-speed-improvement/measure/base-P1-web-1.1.25.json workspace/plan/2026-09-30-speed-improvement/measure/base-P2-web-1.1.25.json new-web.json --md compare-web.md
```

- `--session` 을 주지 않으면 창 안에 사건이 있는 메인 세션을 모두 합친다(세션을 새로 열며 이어 간 레인도 한 번에 잰다).
- 결과의 `plugin_versions` 로 새 레인이 실제로 새 판(dddjango 2.19.0 · dddjango-web 1.2.0)을 썼는지 먼저 확인한다(가장 많이 나온 판이 실제 판).

## 2. 기준(옛 버전) — 도구가 분석 문서 수치를 재현하는지 확인함

| 지표 | 8-C-0 core 2.18.4(Claude) | P1 web 1.1.25(Codex) | P2 web 1.1.25(Codex) | 분석 문서 수치 |
|---|---|---|---|---|
| 벽시계(분) | 1084.5 | 1049.2 | 1099.2 | 1,086 · 1,061 · 1,132(착륙까지) |
| 작업(분) | 973.1 | 642.3 | 887.8 | 973.5 · 641.7 · 887.9 |
| 사용 한도 대기(분) | 98.5 | — | — | 98.5 |
| 메인 요청 · 평균 입력(k) | 525 · 335.9 | 2716 · 139.6 | 3221 · 135.7 | 8-C-0 525 · 328k |
| 설계자 요청 · 평균 입력(k) | 1455 · 536.6 | 294 · 135.7 | 314 · 121.5 | 8-C-0 1,455 · 525k |
| 메인 모델(분) | 129.2 | 403.5 | 445.0 | 8-C-0 129.4 · P1 403 |
| 리뷰 라운드 | 14 | — | — | 8-C-0 Phase 1 10 + G1′ 2 + G1″ 2 |
| 메인 pre-gate 전경 | 36회 73.2분 | — | — | 72.5분 |
| 메인이 옮겨 적은 노트(바이트) | 581243 | — | — | 574KB |
| 명세 판 · KB | 18 · 180→610 | 15 · 71→93 | 10 · 111→111 | 8-C-0 184→625KB(20판) |
| wait_agent 시간 초과 | — | 441 | 619 | P1 폴링 65 · P2 44 모델분 |
| inputs 검사 | — | 152 | 200 | P1 163 · P2 175 |

차이(작음): 평균 입력은 이 도구가 «새 입력 + 캐시 읽기 + 캐시 쓰기» 합의 요청 평균이라 분석 문서보다 2~3% 높다. 8-C-0 은 분석 창(09-30 03:41~21:47)만 잰다 — 레인은 그 뒤에도 옛 판으로 계속 돌았다.

## 3. 어떤 지표가 어떤 개선을 보나

| 지표 | 개선 | 기대 방향 |
|---|---|---|
| 메인 pre-gate 회·분(전경) · 백그라운드 | C1 검사기 고속화 · C2 리뷰와 동시 | 1회 6~11분 → 약 1.5~2.5분 · 전경 분 크게 감소 |
| 리뷰 라운드 · «전원 집행 가능 → G1» | C3 재리뷰 멈춤 기준 | nit 확인 라운드(8-C-0 r8~r10) 없어짐 |
| 메인이 옮겨 적은 노트(바이트) | C4 리뷰어 직접 기록 | 0 에 가깝게 |
| 명세 판 크기 · 설계자 평균 입력 | C5 처분 표 분리 | 명세 약 −83KB · 설계자 입력 감소 |
| 보고에 나온 TREE_CONTRACT_MISMATCH · G1′ · ARRANGE_BLOCKED | C7 G1 전 인수 점검 | Phase 2 발 설계 반송 → G1 전 ARRANGE_BLOCKED 로 앞당김 |
| wait_agent 시간 초과 | K5 Codex 대기 5분 | 수백 회 → 수십 회 |
| 서브가 돌린 게이트 | (C6 · 미채택) | 참고 |
| 설계자 재처리 횟수 | C13 서브에이전트 캐시 1시간(사용자 설정) | 설정하면 1시간 안 재개분이 0 |
| W8 대조 회·분 · 발주자 «반송» 수 | web W8 작은 판(배포 뒤) | G2 시각 반송 감소 |
| 작업 · 벽시계 · 모델 시간 합 | 전부 | 감소(레인 모양이 달라 절대값보다 단계별로 본다) |

## 4. 주의
- 레인마다 요청 크기·슬라이스 수가 달라 벽시계만으로 비교하지 않는다. 같은 단계(G0 · Phase 1 · Phase 2 · G2) 안의 지표와 위 개선별 지표로 본다.
- Codex 레인의 하위 스레드는 역할 대신 작업 이름으로 남아 이름으로 역할을 묶는다(`coarse_role`). 묶음이 틀리면 `threads` 칸에서 원래 이름을 본다.
- Codex 기록에는 사용 한도 대기가 없다(—).
