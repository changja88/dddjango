수정 대상: skill

# workflow role-map Idempotency-Key Minor 계획

## 수정 범위

- 수정: `dddjango/skills/workflow-dddjango-subagents/references/role-map.md`
- runtime sync: installed `dddjango-local` cache의 동일 reference

## 절차

1. API Agent row에 `Idempotency-Key API behavior`를 추가한다.
2. runtime cache role-map을 canonical source와 동기화한다.
3. skill docs validator로 role-map parity를 확인한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`

## 완료 조건

- API Agent role-map row가 idempotency API behavior ownership을 직접 드러낸다.
- source/cache role-map이 일치한다.
