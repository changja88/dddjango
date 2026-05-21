수정 대상: skill

# architecture-implementation-patterns P3 skill 수정 계획

## 수정 이유

P3 평가에서 target `SKILL.md`의 핵심 구조와 progressive disclosure는 적절하지만, concrete implementation handoff가 source handoff table보다 추상적이고 source/reference audit handoff가 직접 드러나지 않는 Minor가 확인됐다. Skill 간 책임 충돌을 줄이기 위해 routing 문장만 좁게 보강한다.

## 수정 범위

- `dddjango/skills/architecture-implementation-patterns/SKILL.md`

## 수정하지 말아야 할 범위

- Bundled references는 이미 세부 판단을 보관하고 1단계 직접 링크로 발견 가능하므로 수정하지 않는다.
- `agents/openai.yaml`은 skill purpose와 정렬되어 있으므로 수정하지 않는다.
- `workspace/reference/architecture-implementation-patterns/reference/final.md`는 dedicated source reference로 충분하므로 수정하지 않는다.
- Neighboring skills, eval pack, validators는 이번 P3 target 수정 범위가 아니므로 수정하지 않는다.
- 본문에 source reference path를 runtime-facing allowed reference처럼 추가하지 않는다.

## 작업 체크리스트

- [ ] `SKILL.md` routing에서 concrete implementation handoff target을 명시한다.
- [ ] `SKILL.md` routing에서 source/reference audit, metadata, runtime cache sync, leakage, validation coverage, eval traceability handoff를 `source-reference-audit`로 명시한다.
- [ ] `SKILL.md`가 500줄 미만이고 bundled references가 1단계 직접 링크로 유지되는지 확인한다.
- [ ] Source/runtime cache diff가 생기면 별도 runtime-sync 분석/계획을 작성하고 cache를 동기화한다.
- [ ] 독립 리뷰 결과를 통합해 target-skill Blocker 0, Major 0, 열린 Minor 0인지 재평가한다.

## 검증 명령

- `wc -l dddjango/skills/architecture-implementation-patterns/SKILL.md`
- `diff -qr dddjango/skills/architecture-implementation-patterns /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-implementation-patterns`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- 직접 책임과 handoff 기준이 `SKILL.md`에서 명확하다.
- `architecture-implementation-patterns`가 DDD, DB, API, concrete implementation, test, source audit, workflow 책임을 침범하지 않는다.
- `SKILL.md`는 핵심 routing과 runtime rule 중심이며 bundled references는 필요한 때만 직접 발견 가능하다.
- Source skill과 runtime cache가 동일하다.
- Target-skill 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
- 검증 명령 결과를 실제 출력 기준으로 보고한다.
