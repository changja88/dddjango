수정 대상: skill

# architecture-implementation-patterns P1 skill 개선 계획

## 수정 이유

Dedicated source reference가 생성됐으므로 source skill의 fallback/provisional 안내는 더 이상 사실이 아니다. Skill이 source reference의 패턴 선택 기준을 정확히 반영하도록 SKILL.md, bundled references, `agents/openai.yaml`을 갱신한다.

## 수정 범위

- `dddjango/skills/architecture-implementation-patterns/SKILL.md`
- `dddjango/skills/architecture-implementation-patterns/references/pattern-selection.md`
- `dddjango/skills/architecture-implementation-patterns/references/ports-adapters.md`
- `dddjango/skills/architecture-implementation-patterns/references/repository-uow.md`
- `dddjango/skills/architecture-implementation-patterns/references/outbox-acl.md`
- `dddjango/skills/architecture-implementation-patterns/agents/openai.yaml`

## 수정하지 말아야 할 범위

- source reference를 skill stale 상태에 맞춰 되돌리지 않는다.
- runtime cache는 source skill 수정 후 `수정 대상: runtime-sync` 루프에서 별도 동기화한다.
- eval bucket 문제를 발견하더라도 P1에서는 eval 파일을 수정하지 않고 후속 분석 대상으로 분류한다.

## 작업 체크리스트

- [ ] `SKILL.md` frontmatter에서 provisional/fallback 문구를 제거한다.
- [ ] routing에서 `workflow`, `architecture-ddd`, `architecture-db`, `architecture-api`, implementation skills handoff를 유지한다.
- [ ] reference loading 지침이 source reference의 세부 축과 연결되도록 갱신한다.
- [ ] bundled references에서 stale provisional 문구를 제거하고 한글 runtime guidance로 정리한다.
- [ ] `Risky Write Consistency Block`의 pattern-level 판단과 owning skill handoff를 유지한다.
- [ ] `agents/openai.yaml`을 `openai_yaml.md` 제약에 맞게 갱신한다.
- [ ] 수정 후 source skill과 runtime cache 차이를 평가한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- runtime-facing skill 문서가 dedicated source reference와 충돌하지 않는다.
- layered, clean, hexagonal, ports/adapters, dependency direction, repository, UoW, CQRS, event sourcing, saga, outbox, ACL, service layer 판단 기준을 찾을 수 있다.
- SKILL.md가 500줄 미만이며 detailed guidance는 1단계 bundled reference로 연결된다.
- skill-creator 관점 리뷰에서 Blocker 0, Major 0, 열린 Minor 0 상태다.
