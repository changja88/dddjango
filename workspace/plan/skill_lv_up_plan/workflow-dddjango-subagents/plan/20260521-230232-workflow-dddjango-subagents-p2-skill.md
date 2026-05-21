수정 대상: skill

# workflow-dddjango-subagents P2 skill plan

## 수정 이유

Source reference가 실제 사용자 표현으로 둔 `role map`, `delegation`, `parallel agent work`, `responsibility split` 등이 `SKILL.md` frontmatter에 충분히 노출되지 않아 trigger 판단이 body/reference 로딩 이후에만 가능해질 위험이 있다. P2 종료 조건의 목적, trigger, 제외 조건, metadata 정합성을 맞추려면 runtime-facing trigger surface를 보강해야 한다.

## 수정 범위

- `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
  - frontmatter `description`에 source reference의 실제 한영 trigger 표현을 반영한다.
  - `Routing` 첫 항목에도 같은 trigger 표현을 반영한다.
  - Domain Agent 책임을 source canonical role wording과 맞춘다.
- `dddjango/skills/workflow-dddjango-subagents/references/delegation-rules.md`
  - explicit user request trigger 목록을 frontmatter와 source reference에 맞춘다.
- `dddjango/skills/workflow-dddjango-subagents/references/role-map.md`
  - Domain Agent 책임을 source canonical role wording과 맞춘다.
- `dddjango/skills/workflow-dddjango-subagents/agents/openai.yaml`
  - optional interface field를 추가하지 않고 `default_prompt`를 한 문장으로 짧게 정리한다.

## 수정하지 말아야 할 범위

- Source reference 자체는 충분하므로 `workspace/reference/workflow-dddjango-subagents/reference/final.md`는 수정하지 않는다.
- 다른 dddjango skills, eval case, answer oracle, evaluator, generated eval run artifacts는 수정하지 않는다.
- 실제 subagent 실행 정책, handoff field, integration checklist의 의미는 바꾸지 않는다.
- `agents/openai.yaml`에 icon, brand color, dependencies, policy 등 명시 요청 없는 optional field를 추가하지 않는다.

## 체크리스트

- [ ] Frontmatter에 `role map`, `delegation`, `parallel agent work`, `responsibility split`, `parallel review`, `sequential fallback` 등 source trigger가 노출된다.
- [ ] Routing과 delegation reference가 한영 trigger 세트를 일관되게 표현한다.
- [ ] Domain Agent 책임이 `bounded context`, `ubiquitous language`를 포함한다.
- [ ] `agents/openai.yaml` default prompt가 `$workflow-dddjango-subagents`를 포함하고 한 문장으로 유지된다.
- [ ] Runtime cache가 workspace canonical source와 동기화된다.
- [ ] Validators와 diff parity가 통과한다.
- [ ] 재평가 결과 Blocker 0, Major 0, 열린 Minor 0이다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/workflow-dddjango-subagents /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents`

## 완료 조건

- `SKILL.md` 목적, trigger, 제외 조건이 source reference와 일치한다.
- 본문 또는 bundled reference에만 숨은 실제 trigger 표현이 남지 않는다.
- `agents/openai.yaml`이 `SKILL.md`와 충돌하지 않고 optional interface field를 추가하지 않는다.
- Source skill과 runtime cache가 같은 내용을 가진다.
- 검증 명령이 통과하고 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
