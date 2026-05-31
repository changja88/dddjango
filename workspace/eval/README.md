# workspace/eval — dddjango 평가 시스템

`/dddjango` 플러그인이 낸 산출물을 **규칙 준수(DDD·houserules·django-ninja) + 기능 정확성** 기준으로 채점하는 평가 홈. 매 스모크/라이브 평가의 *기준(rubric)* 과 *결과(results)* 를 한곳에서 관리한다.

> 결정성-조사(N=1/2/3) 시절 하니스(PROTOCOL·baseline·reset.sh·runs/·comparison*.html·RESULTS.md 등)는 2026-05-31 정리됨(결론은 DEVLOG DR-13/14 흡수, 필요 시 git 히스토리에서 복구).

## 구조

```
eval/
├── README.md            # 이 인덱스
├── rubric/              # 평가 기준 (정본 — 앞으로 모든 채점의 단일 출처)
│   ├── RUBRIC.md            # 평가 *항목* (무엇을 보나): S-DDD·S-HR·S-NINJA·FC·TIER-Q
│   └── EVAL-METHOD.md       # 평가 *방법* (어떻게 채점·집계·bisect·완료 판정하나)
└── results/             # 평가 결과 (현행 + 앞으로 누적)
    ├── EVAL-p1a-v3-codex.md    # 루브릭 채점 기록 — Codex · p1a-v3 (가장 마지막 스모크)
    ├── EVAL-p1a-v3-claude.md   # 루브릭 채점 기록 — Claude · p1a-v3 (가장 마지막 스모크)
    ├── REMAINING-ISSUES.md     # 라이브 이슈 트래커 (P1a 등 미해결 + C 트랙 인벤토리) — 정본
    ├── LIVEFIRE-RESULTS.md     # 라이브파이어(위반-주입) 채점 결과
    ├── FINAL-SMOKE-PLAN.md     # 최종 수동 스모크 채점 계획(rev3)
    ├── FINAL-SMOKE-INSIGHTS.html
    └── RETEST-HANDOFF.md       # 라이브 재테스트 실행 핸드오프 + §1 고정 게이트 답(규율 정본)

> **채점 기록 명명 규약**: `EVAL-<라운드>-<런타임>.md` (예: `EVAL-p1a-v3-codex.md`). 한 회차의 Claude·Codex는 별도 파일로 기록(직접 비교 시 부록에서 교차참조).
```

## 관리 규약 (앞으로)

1. **채점 기준은 `rubric/`이 단일 출처.** 새 평가는 항상 `rubric/RUBRIC.md`(항목)로 보고 `rubric/EVAL-METHOD.md`(방법)로 채점·집계한다. 기준 변경은 *채점 전*에만(사후 합리화 금지, EVAL-METHOD §5 사전등록).
2. **고정 입력 규율은 `results/RETEST-HANDOFF.md` §1**(런 리셋·게이트 답)을 따른다 — 런 간 입력이 흔들리면 비교가 오염된다.
3. **평가 결과는 `results/`에 누적.** 한 회차 = 무엇을·어떤 fixture로·어떤 판정인지. 라이브(위반-주입) 채점은 `LIVEFIRE-RESULTS.md`, 미해결/추적은 `REMAINING-ISSUES.md`에 갱신.
4. **정직 경계**: 저장 fixture 정적 채점은 "구조적 준수 + 기능 정확성"까지. "게이트 라이브 발화"는 fresh 위반-주입 런으로만 확인(정적 통과 ≠ 라이브 발화 — DR-21). baseline 대비 차별가치는 *안 잰다*(규칙 준수가 핵심).

## 평가 대상 fixture (레포 밖)

저장 산출물은 `~/Desktop/dddjango-*` (git 미포함, 레포에 복사하지 않음). 태스크B(주문생성)·Codex 4점 timeline = `dddjango-final-codexB` → `dddjango-smoke2-codexB` → `dddjango-p1a-livefire-codex` → `dddjango-p1a-v3-codex`. 태스크A(재고예약)·Claude 2점 = `dddjango-final-claudeA` → `dddjango-smoke2-claudeA`. dual = `{p1a-livefire,p1a-v3}-{codex,claude}`.

## 전체 여정·결정 정본

플러그인 전체 작업 이력·DR 원장은 레포 `workspace/DEVLOG.md`. 이 폴더는 *평가 축*만 담는다.
