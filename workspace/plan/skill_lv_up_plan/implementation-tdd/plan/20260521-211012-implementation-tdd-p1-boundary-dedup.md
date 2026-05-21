# implementation-tdd P1 boundary guidance 중복 수정 계획

## 수정 이유

`SKILL.md`와 `references/test-list.md`가 boundary-policy 세부 규칙을 중복해 담고 있어 이후 한쪽만 수정될 위험이 있다. P1 종료 조건의 열린 Minor 0을 만족하기 위해 `SKILL.md`를 핵심 실행 규칙 중심으로 줄이고 세부 규칙은 bundled reference에 둔다.

## 수정 범위

- `dddjango/skills/implementation-tdd/SKILL.md`
  - boundary 관련 세부 bullet 3개를 `references/test-list.md`로 연결되는 짧은 필수 규칙으로 축약한다.

## 수정하지 말아야 할 범위

- `dddjango/skills/implementation-tdd/references/test-list.md`는 이미 상세 boundary 기준을 담고 있으므로 수정하지 않는다.
- source reference는 이전 loop에서 보강되었고 이번 수정 대상이 아니다.
- eval case, answer oracle, evaluator는 수정하지 않는다.

## 작업 체크리스트

- [ ] `SKILL.md` Runtime Rules의 boundary 중복을 줄인다.
- [ ] runtime cache diff를 확인한다.
- [ ] runtime cache가 stale이면 runtime-sync 분석/계획을 작성하고 동기화한다.
- [ ] validators를 실행한다.
- [ ] 최종 재평가에서 Blocker 0, Major 0, 열린 Minor 0을 확인한다.

## 검증 명령

- `diff -qr dddjango/skills/implementation-tdd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- boundary details are no longer duplicated in `SKILL.md`.
- `references/test-list.md` remains the detailed source for boundary cases.
- runtime cache is synchronized.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
