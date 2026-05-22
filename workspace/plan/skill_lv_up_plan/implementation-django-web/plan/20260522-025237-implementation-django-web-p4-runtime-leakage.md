수정 대상: skill

## 목표

`implementation-django-web` runtime guidance에서 eval/validator framing을 제거하고, 제품 기준의 render/static acceptance guidance만 남긴다.

## 수정 순서

1. `dddjango/skills/implementation-django-web/SKILL.md`의 `validator-visible label` 문장을 제품 기준 문장으로 교체한다.
2. `workspace/scripts/validate_skill_docs.py`의 Django Web skill 검증을 exact phrase 강제에서 semantic product-term group 검증으로 바꾼다.
3. 관련 unit test 또는 기존 skill validator를 실행해 runtime skill validation이 계속 동작하는지 확인한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `.venv/bin/python -B workspace/scripts/test_validate_skill_docs.py`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`

## 완료 조건

- runtime skill에는 evaluator/validator framing이 없다.
- skill docs validator는 Django Web 제품 기준 누락을 계속 잡되 exact oracle phrase 노출을 강제하지 않는다.
