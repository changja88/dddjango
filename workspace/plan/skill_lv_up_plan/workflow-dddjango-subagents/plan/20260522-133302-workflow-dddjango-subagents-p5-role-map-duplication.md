수정 대상: skill

# P5 workflow role-map 중복 정책 수정 계획

## 수정 범위

- `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
- runtime cache sync가 필요한 경우 active plugin cache의 같은 skill 파일

## 순서

1. `SKILL.md`의 Canonical Roles section에서 detailed role table을 제거하고 `role-map.md` owning reference를 명확히 한다.
2. P5 관련 guardrail인 Django web ownership, source-governance handoff, workflow-local parity evidence는 짧게 유지한다.
3. workflow validator와 skill doc validator로 role-map shrink가 없는지 확인한다.
4. cache/source parity가 깨지면 cache sync 후 `diff -qr`로 확인한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- workflow bucket validator
- role-map 관련 targeted eval 영향이 있으면 `case-workflow-cache-sync` targeted eval 재실행

## 완료 조건

- exact role responsibilities는 `role-map.md`가 소유한다.
- `SKILL.md`는 routing summary와 required handoff guardrail만 보유한다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
