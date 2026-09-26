# 로드맵 4 — graph-owned 규범 매핑표 (2026-09-27 · 설계 v4 §3)

- 개정 원칙(로드맵 3 과 같다): 배포된 규범의 뜻이 바뀌면 새 Expression `@2026-09-27`. 미배포 규범(R-3470~R-3501 · R-0309 · R-0442 · `@2026-09-27` Expression)은 제자리 편집. 이번 편집은 배포 규범의 뜻을 바꾸지 않는다 — 새 문장은 모두 새 규범이 진술하고, 기존 문장 수정은 미배포 규범(R-3493·R-3494·R-3498)의 블록뿐이다.
- 신설 7: R-3502~R-3508. 규범 하나는 블록 하나가 진술한다(현행 전건 1:1 — 중복 진술 0).
- 새 검사기 개체 `c/behavior_guard.py`(wiring/registry.ttl) — design_pregate 선례. 연쇄: `rulepack_smoke` 명부 · `reverse_coverage` 설명.

## Coordinator — `ontology/rules/command-dddjango.ttl`

| # | 블록 | 문장 | 규범 · 처리 | Codex `dddjango/SKILL.md` |
|---|---|---|---|---|
| C1 | s007/b3 | 0T/0C 분할 · 테스트 쪽 분류 · 이동은 분류 중립 · 두 쪽 본문 = 동작 불변 불가 | **R-3502** 신설(Obligation · delegatedTo Coordinator) | Phase 2 3번 같은 문장 |
| C2 | s007/b3 (끝에 하위 항목) | 동작 보존 창: open(앵커 뒤 · 열린 창 거부) → 마지막 보고 → close → red 면 철회·재실행 · 장치 오탐 = ⓐ 재상정(플러그인 결함) · exit 1 파견 금지 · 창 종류 입력 · 병렬은 창 안만 · 잇기 verify 1회 · close 보고 → 5번 감사 입력 · `--python` · `behavior/` 기계 기록 | **R-3503** 신설(Obligation · enforcedBy `c/behavior_guard.py`) | 같은 하위 항목 |
| C3 | s007/b57 | G2 차단 목록에 동작 보존 불비 · `동작 보존: <요약>` 1행(verify `요약:`) | **R-3504** 신설(Obligation · enforcedBy `c/behavior_guard.py`) | 7번 G2 배너 |
| C4 | s009/b4 | 수정 모드 3번 상속: 0T/0C 분할·동작 보존 창(첫 창 전 앵커) · G2 동작 보존 1행·차단 | R-3493 제자리(라벨 갱신) | 수정 모드 3번 |
| C5 | s011/b5 | 기계 기록 열거에 `behavior/` 창 기록 | R-3494 제자리(라벨 갱신) | 경계 |
| C6 | s006/b11 | 재상정 절이 받는 STOP 에 «동작 보존 장치 오탐» | R-3498 제자리(라벨 그대로 — «오탐 STOP» 일반) | 슬라이스 0 STOP |

## coder — `ontology/rules/agent-coder.ttl`

| # | 블록 | 문장 | 규범 | Codex `dddjango-coder/SKILL.md` |
|---|---|---|---|---|
| K1 | s006/b6 (새 · 경계 끝) | 0C: 옮긴·개명한 코드를 따라가는 테스트 치환(import·문자열 경로·이름)은 소유 무관 coder · 로직·단언 무변 · 판정 close | **R-3505** 신설(Permission · enforcedBy `c/behavior_guard.py`) | 경계 끝 |
| K1 | 〃 | 0T: ⓐ 수리 테스트 편집만(새 case·제품 편집 금지) · 반대쪽 본문 필요 → 편집 말고 보고 | **R-3506** 신설(Obligation · enforcedBy `c/behavior_guard.py` · delegatedTo DR) | 〃 |

## discipline-reviewer — `ontology/rules/agent-discipline-reviewer.ttl`

| # | 블록 | 문장 | 규범 | Codex `dddjango-discipline-reviewer/SKILL.md` |
|---|---|---|---|---|
| D1 | s005/b5 | 0C 창 close green 치환 hunk = 일반 `retain` 무편집의 예외(치환이 명세 이동·개명과 맞는지만) | **R-3507** 신설(Exception · delegatedTo DR) | Phase 2 hunk 대조 |
| D1 | 〃 | 0T 창 테스트 편집 hunk 는 ⓐ 항목과 대조해 전후 보호 동등(단언 약화·같은 이름 재작성 — close 사각) · close 보고는 감사 입력 | **R-3508** 신설(Obligation · delegatedTo DR) | 〃 |

## 범위 밖(설계 v4 §3)

- acceptance-tester 무변(§5-1) · `accepted.txt` 없음(장치 오탐은 기존 `ⓐ 재상정`) · 창별 감사 신설 없음(close 보고는 기존 감사 입력).

## 보정 (구현 리뷰 J 반영 · 제자리)

- C2(R-3503): «각각 창 하나» → «종류마다 하나 이상» · 승인 머지만 유입 · exit 1 = 철회 또는 STOP · 재개 verify «창 누락» 무시 조건 · 감사 반영 = 같은 종류 창 재open (J-M3·J-M7·J-m12).
- C4(R-3493): «Phase 2 6번» 명시(J-m12).
- K1(R-3506): 0T 편집은 테스트 소유 무관 · 케이스 개명 금지 · 루트 pytest 설정 절은 테스트 쪽(J-m8·J-m10·J-M4).
- D1(R-3508 블록): 치환 hunk 예외의 기계 출처 `green_files` · close 사각 열거(J-m9·J-m11).
