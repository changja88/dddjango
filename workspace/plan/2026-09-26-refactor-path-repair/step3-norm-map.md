# 로드맵 3 — graph-owned 규범 매핑표 (2026-09-27 · 검토 H-M4·H-M5 · 결정 7 반영)

- 개정 원칙: 이미 배포된 규범은 새 Expression `@2026-09-27`(revisionKind 명시). 09-26 에 새로 낸 규범과 09-26 에 새 Expression 을 받은 규범(미배포 — R-3470~R-3499 · R-0309 · R-0442)은 제자리 편집(rev 유지).
- 신설 2: **R-3500**(Prohibition — 포트·조회 계약 인자 `_in` 금지 · enforcedBy `c/design_pregate.py`·`c/check-port-adapter-pairing.py`) · **R-3501**(Obligation — 포트·조회 계약 반환 `_in` · 결정 7 · delegatedTo `a/agent-discipline-reviewer`). 둘 다 houserules final 새 블록 s011-3/b3.
- R-3445 amendment vs 신설: ②③ 의 새 의무(승인 유입 동반 · 발주 `--base` 불수용 · 기준선 행 대조 · digest skip)는 모두 «재발화 판형·최신성» 한 규범의 판형 변경이라 **R-3445 amendment**. `pre-gate 기준선`·실행 경계 행 기록은 실행 규범 **R-3482(제자리)**.
- **검토 I 반영(09-27)**: 기준선 값은 실행 줄이 아니라 `pregate-report.md` 의 `- pre-gate 기준선 — <SHA> · <UTC>` 행에 한 번 기록한다(첫 파견 직전). check-report 가 이 행으로 플래그 없이 기준선을 대조한다(I-M1 — `--base` 를 뺀 HEAD 판형 재발화도 «기준선 치환»). `--expect-base` 는 선택 플래그로 남고 규범은 요구하지 않는다. 선언 확정 #574 의 filtered 는 check-report 가 불인정한다(I-m4).

## Coordinator — `ontology/rules/command-dddjango.ttl`

| # | 블록 | 문장 | 규범 · 처리 | Codex `dddjango/SKILL.md` |
|---|---|---|---|---|
| C1 | s002/b8 | 헤더 병기에 실행 트리 digest · 새 실행 G0 승인 때 `- 실행 경계 —` 행 append | R-3438 amendment rev4 | 산출물 위치 pregate-report 행 |
| C2 | s002/b9 | 승인 머지 목록 소비자에 pre-gate 재발화 추가 | R-3439 amendment rev2 | 산출물 위치 approved-merges 행 |
| C3 | s003/b10 | G1 배너 부재 사유에 툴체인 stale·기준선 치환·기준선 대조 누락 · Phase 2 G1′ check-report `--expect-base` (H-M5 ⑤) | R-3437 amendment rev4 | 배너 절 |
| C4 | s005/b13 | 실행 줄에 `· pre-gate 기준선 <SHA>`(값 규칙 · override 재실행 뒤) · G0 승인 때 실행 경계 행 (H-M2 · H-M3 · H-M5 ①) | R-3482 제자리 | 실행과 앵커 |
| C5 | s006/b9 | deferred 증거 문면(재발화는 오버레이 생략 — E m8) · 선언 확정 #574 filtered 금지 + 도구 오탐 STOP(F M-4 · H-m3) · S2 문면(H-M5 ④) | R-3433 amendment rev6 | pre-gate 문단 |
| C6 | s006/b10 | ① digest skip 조건·skip 행 digest 칸 ② `--base <실행 줄 pre-gate 기준선>` · `--approved-merge-file` 동반 · 발주 `--base` 불수용 · 오버레이 생략 문면 ③ `--expect-base` 상시(Phase 2) · 앞 실행 예보 정합 · 한정 «이번 실행» | R-3445 amendment rev3 | 캐시 skip·재발화 판형 |
| C7 | s007/b6 | 재진술 → «② 의 플래그 전부» (F M-6) | R-0287 clarification rev4 | 5번 감사 |
| C8 | s007/b12 | 앵커 기록 때 `pre-gate 기준선` 동반 (H-M5 ①) | R-0309 제자리 | 6번 백스톱 |
| C9 | s007/b59 | 최신성 행 check-report 에 `--expect-base` · 앞 실행 예보 머리 (H-M5 ⑥) | R-3444 amendment rev2 | G2 최신성 |
| C10 | s009/b3 | 재진술 → «② 의 플래그 전부» (F M-6) | R-0419 clarification rev4 | 수정 모드 2번 |
| C11 | s009/b5 | G1′ 생략 때 pre-gate 기준선·최신성 (H-M5 ⑥) | R-0425 clarification rev2 | 수정 모드 생략 |
| C12 | s010/b6 | 재진술 → «② 의 플래그 전부» (F M-6) | R-0442 제자리 | Contract mismatch |
| C13 | s011/b5 | 기계 기록 열거에 pre-gate 기준선 · 실행 경계 행 append (H-M5 ①) | R-3494 제자리(라벨 갱신) | 경계 |
| — | s002/b2 | 열거 없음 — 변경 없음 (H-M5 ① 의 18행) | — | — |

## design-architect — `ontology/rules/agent-design-architect.ttl`

| # | 블록 | 문장 | 규범 · 처리 | Codex `dddjango-design-architect/SKILL.md` |
|---|---|---|---|---|
| A1 | s005/b33 | 선언 확정 #574 의 뜻·처분·filtered 불가 (H-M5 ③) | R-3424 amendment rev3 | 기계 채널 |
| A2 | s005/b34 | 태그 실존 = 기준선 ⊕ 승인 유입 · 승인 유입 add 충돌 (H-M5 ②) | R-3425 amendment rev5 | 파일 계획 |
| A3 | s005/b35 | 포트 메서드 인자·반환 이름 포인터(houserules §3) + `djr:restates` hr s011-3/b3 | R-3426 amendment rev7 | 공개 심볼 |
| A4 | s005/b36 | «격리 사본» 문면(승인 유입 · 오버레이 조건) (E m8) | R-3427 clarification rev7 | 경계 import |

## houserules final — `ontology/rules/discipline-houserules-final.ttl`

| # | 블록 | 문장 | 규범 | 미러 |
|---|---|---|---|---|
| H1 | s011-3/b3 (새) | «포트 자료의 방향» — 인자 `_in` 금지(#574) · 반환 `_in`(결정 7) · 중계 예외 · 옛 `_out` 반환 = 의미 빚 · #573 교차 | R-3500 · R-3501 신설 | 소스 미러 수동 교체 → `corpus_mirror_sync --write`(Codex houserules final 포함) |

## 그래프 밖

- `#236` 정정(결정 7): `workspace/design/2026-08-08-tree-revision-spec.md` 행 236 «내보내는 자료» → «돌려주는 자료» · 근거 «트리 54행» → «트리 55행» · 검사기 `check-port-adapter-pairing.py` 메시지·docstring 같은 뜻으로(byte 미러).
- 산문: REQUEST_GUIDE §4 1행(Claude·Codex byte) · `docs/DEVELOPMENT.md` §6 릴리즈 창 1행.

## 절차

ttl 편집(rdflib + canon) → `ontology_gate` → render(command-dddjango · agent-design-architect · discipline-houserules-final) → LEDGER → target-counts(Norm/Work +2 · Expression +2 신설 +11 개정) → q4 → 소스 미러 교체 + `corpus_mirror_sync --write` → `make rulepack` → Codex 의미 미러 → 산문 → 픽스처 · 구현 리뷰 · 조감도 · `make verify` · `make verify-mutation` · 커밋 → 봉인 chore.
