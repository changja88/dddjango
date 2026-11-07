# nit 빠른 길 — 계획(dddjango 2.32.0 후보)

설계: `design.md`. 장부를 읽은 때: 마지막 F4-152(2026-11-07 12:50 판) · F4-146 ~ F4-152 는 이번 판에 넣지 않는다(다음 판 후보 — F4-149 의 retain 재조직 슬라이스 칸은 이 판의 E4 로 드물어진다 · F4-150 ~ F4-152 는 검사기 쪽 항목이다).

## 단위

1. **규칙 개정(그래프)** — `ontology/rules/` 의 코디네이터 · 역할 문서. §3 판정 모드 · §4 절차 · §5 E1~E6 · 사용자 결정(가/나)에 따른 감사 문장.
   - 맡은 곳: 코디네이터 Phase 1 4번(재리뷰 상한 · 새 불릿) · arrange 점검 · Phase 2(G2 nit 길 · 동작 보존 창 문장) · 수정 모드 · 산출물 위치(새 부속 기록 종류) / `design-architect`(빠른 길 입력) / `discipline-reviewer`(`NIT_DIFF_CHECK` · hunk 대조 예외) / `coder` · `acceptance-tester`(치환 입력 · 0T 절).
   - 확인: `ontology_gate.py` · `ontology_render.py --apply <doc_key>`.
2. **소성물** — LEDGER 재기준선 · `ISSUED` · 계수표 `target-counts.json` · q4 골든 · `make rulepack` · `scope-limit-norms.md` G12 대조.
3. **Codex 미러** — `codex-dddjango/skills/dddjango/SKILL.md` · 역할 스킬 넷을 같은 뜻으로(자동 검사 없음 · 구현 검토 항목).
4. **행동 시험** — `design.md` §8 의 판정 재시험(안 본 사례) · 책상 시험 · 옛 판 대조. 옛 판 = 태그 `dddjango--v2.31.2`.
5. **구현 독립 검토** → 지적 재현 → 고침(차단 0 까지).
6. **검사 · 배포** — 봉인 → 커밋 → `make verify` · `make verify-mutation`(rulepack 변경) → push → 깨끗한 클론 `make release`(minor) → 노트 → 봉인 chore → 판 기록 `plan-2.32.0.md` → 문서 · 요청 가이드 확인 → 진행표 → 임시물 정리 → 보고.

## 맡지 않는 것

- 새 스크립트 · 검사기 변경 · `behavior_guard` 변경 · 내용 nit 의 길 · 내용 회차의 arrange 조건 · `symbols` 범위 · web.

## 멈출 기준

- 판정 재시험에서 동작이 바뀌는 공격을 놓치면 고쳐 다른 사례로 다시 잰다. 세 번 안에 닫히지 않으면 멈추고 묻는다.
- 책상 시험에서 규칙 글을 읽고 지금 길 대신 빠른 길로 잘못 가는 상황이 나오면 고칠 때까지 배포하지 않는다.
- 구현 독립 검토의 차단이 셋째 확인에도 닫히지 않으면 멈추고 묻는다.

## 되돌릴 수 없는 것

없음(판 하나를 되돌리면 지금 길로 돌아간다 · 현장 저장소는 쓰지 않는다).
