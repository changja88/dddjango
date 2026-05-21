# implementation-tdd P1 reference 수정 계획

## 수정 이유

`implementation-tdd` source reference가 TDD 핵심 절차 대부분은 충분히 다루지만, boundary cases 기준은 runtime skill이 요구하는 수준만큼 일반화되어 있지 않다. P1 순서에 따라 skill을 고치기 전에 source reference의 판단 기준을 먼저 보강한다.

## 수정 범위

- `workspace/reference/implementation-tdd/reference/final.md`
  - `5.1 테스트 목록` 아래에 boundary/decision-axis 테스트 목록 규칙을 추가한다.
  - 정책 경계, nearest outside/complement case, 독립 결정축, 유효 기간/만료일 예시를 포함한다.

## 수정하지 말아야 할 범위

- eval case, answer oracle, evaluator는 이번 P1 reference gap의 수정 대상이 아니다.
- `dddjango/skills/implementation-tdd/**`는 reference 수정 후 별도 skill 반영도 평가에서 부족할 때만 수정한다.
- runtime cache는 source skill과 다를 때만 runtime-sync 분석/계획 후 동기화한다.

## 작업 체크리스트

- [ ] `final.md`의 테스트 목록 섹션에 boundary cases 일반 규칙을 추가한다.
- [ ] reference 보강 후 `SKILL.md`, bundled references, `agents/openai.yaml` 반영도를 재평가한다.
- [ ] source skill과 runtime cache 차이를 확인한다.
- [ ] real subagent 리뷰 결과를 통합해 Blocker, Major, 열린 Minor가 남으면 추가 루프를 수행한다.
- [ ] validators를 실행한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- reference gap이 닫혀 `boundary cases` 기준을 source reference에서 직접 확인할 수 있다.
- skill 반영도와 runtime sync 재평가에서 Blocker 0, Major 0, 열린 Minor 0이다.
- 지정 validators가 통과한다.
