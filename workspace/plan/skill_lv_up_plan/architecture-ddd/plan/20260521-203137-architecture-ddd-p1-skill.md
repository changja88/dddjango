# architecture-ddd skill 수정 계획

## 수정 이유

P1 평가와 real-subagent 리뷰에서 source reference 부족은 없었지만, skill 반영도에 초기 Major 1건과 초기 Minor 3건이 발견됐다. reference 결정을 skill과 bundled reference가 약하게 표현하면 runtime에서 DDD 모델링 판단이 source reference와 다르게 유도될 수 있다.

## 수정 범위

- `dddjango/skills/architecture-ddd/SKILL.md`
- `dddjango/skills/architecture-ddd/references/tactical-patterns.md`
- `dddjango/skills/architecture-ddd/agents/openai.yaml`

## 수정하지 말아야 할 범위

- `workspace/reference/architecture-ddd/**`는 이번 skill 반영 수정에서 바꾸지 않는다.
- eval case, answer oracle, evaluator는 P1 범위에서 수정하지 않는다.
- architecture-implementation-patterns, implementation-django 등 다른 skill의 정책은 이번 범위에서 바꾸지 않는다.

## 작업 체크리스트

- [x] frontmatter 중복 표현을 제거한다.
- [x] Django mapping rule을 source reference의 계층+DIP/pure domain 기본 결정에 맞춘다.
- [x] entity guidance를 aggregate boundary 중심으로 명확히 한다.
- [x] `agents/openai.yaml`이 context map, entity/value object, domain service, consistency boundary 범위를 포함하도록 보강한다.
- [x] source skill 수정 후 runtime cache sync 분석/계획에 따라 cache를 동기화한다.
- [x] 검증 명령과 재평가를 실행한다.

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
diff -qr dddjango/skills/architecture-ddd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd
```

## 완료 조건

- skill 반영도 재평가에서 Blocker 0, Major 0, 열린 Minor 0이다.
- bundled reference가 source reference의 entity, aggregate, Django mapping 결정을 약화하지 않는다.
- `agents/openai.yaml`이 skill 목적과 충돌하지 않는다.
- source skill과 runtime cache가 동기화되어 있다.
