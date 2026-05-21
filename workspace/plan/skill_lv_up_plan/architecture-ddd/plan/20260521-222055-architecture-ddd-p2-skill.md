# architecture-ddd P2 skill 수정 계획

## 수정 이유

P2 평가에서 `SKILL.md` 본문과 bundled reference에 있는 Event Storming, problem/solution space, team-boundary discovery가 frontmatter `description`에 노출되지 않는 문제가 확인됐다. Codex는 frontmatter metadata로 skill routing을 결정하므로 실제 사용자 표현이 body-only trigger로 남으면 skill이 필요한 요청에서 누락될 수 있다.

## 수정 범위

- `dddjango/skills/architecture-ddd/SKILL.md`
- `dddjango/skills/architecture-ddd/agents/openai.yaml`

## 수정하지 말아야 할 범위

- `workspace/reference/architecture-ddd/**`는 충분하므로 수정하지 않는다.
- bundled references는 source reference와 충돌하지 않으므로 이번 P2에서 수정하지 않는다.
- 다른 skill, eval case, answer oracle, evaluator는 이번 범위에서 수정하지 않는다.
- `agents/openai.yaml`에 명시 요청 없는 optional interface field를 추가하지 않는다.

## 작업 체크리스트

- [x] `SKILL.md` frontmatter `description`에 Event Storming trigger를 추가한다.
- [x] `SKILL.md` frontmatter `description`에 problem/solution space와 team-boundary discovery trigger를 추가한다.
- [x] `agents/openai.yaml` `short_description`을 bounded context/context map 의미가 보이도록 수정한다.
- [x] source skill 수정 후 runtime cache 차이를 확인하고 필요하면 `runtime-sync` 분석/계획을 작성한다.
- [x] `skill-creator` 관점 real-subagent 리뷰와 독립 P2 리뷰를 실행한다.
- [x] 검증 명령을 실행하고 Blocker 0, Major 0, 열린 Minor 0 상태로 재평가한다.

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
diff -qr dddjango/skills/architecture-ddd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd
```

## 완료 조건

- `SKILL.md` 목적, trigger, 제외 조건이 frontmatter와 본문 양쪽에서 충돌 없이 드러난다.
- 본문에만 숨은 P2 trigger가 없다.
- `agents/openai.yaml`은 `SKILL.md`와 semantic alignment를 유지하고 optional interface field를 추가하지 않는다.
- source skill과 runtime cache가 동기화되어 있다.
- real-subagent 리뷰와 검증 결과 Blocker 0, Major 0, 열린 Minor 0이다.
