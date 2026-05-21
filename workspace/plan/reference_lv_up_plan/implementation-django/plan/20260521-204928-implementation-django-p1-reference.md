수정 대상: reference

## 수정 이유

`implementation-django` skill이 transaction/consistency, risky write, service/selector, migration rollout, caching/security/performance guidance를 정확히 반영하려면 source reference가 먼저 충분해야 한다. 현재 source는 Django 전반 내용을 포함하지만 transaction/consistency 판단 기준과 REST API boundary가 P1 기준에 부족하다.

## 수정 범위

- `workspace/reference/implementation-django/reference/final.md`
  - DRF 섹션을 greenfield 권장처럼 보이지 않게 API boundary/legacy DRF 유지보수 기준으로 수정한다.
  - service layer 도입 기준을 파일 크기보다 변경 이유, orchestration, transaction, side effect, 반복 흐름 기준으로 보정한다.
  - transaction/consistency subsection을 추가해 `atomic`, `on_commit`, locking, idempotency/constraint, isolation/retry, risky write checklist, test expectation을 source reference에 반영한다.

## 수정하지 말아야 할 범위

- `workspace/develop/eval/**` eval case, answer, evaluator는 수정하지 않는다.
- sibling skill의 routing과 reference는 이번 reference gap을 닫는 데 필요한 경우가 아니면 수정하지 않는다.
- DRF 내용을 전부 삭제하지 않는다. 기존 DRF 유지보수와 migration review 근거는 남기되 greenfield 권장으로 읽히지 않게 제한한다.

## 작업 체크리스트

- [x] REST API/DRF boundary 문구 수정
- [x] service layer 도입 기준 보정
- [x] transaction/consistency source guidance 추가
- [x] reference 수정 후 skill 반영 부족 여부 재평가
- [x] eval 문제 발견 시 P1에서 수정하지 않고 `eval_lv_up_plan/<bucket>/analysis/` 후속 대상으로 분류

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- source reference가 Django model, ORM, QuerySet/Manager, service/selector, migration, transaction, settings, caching, security, performance, integration test acceptance 기준을 판단하기에 충분하다.
- DRF guidance가 `implementation-django-ninja` routing과 충돌하지 않는다.
- reference gap에 대한 Blocker 0, Major 0, 열린 Minor 0 상태를 재평가로 확인한다.
