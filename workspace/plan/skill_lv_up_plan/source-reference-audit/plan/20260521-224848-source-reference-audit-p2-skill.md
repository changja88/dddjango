# source-reference-audit P2 skill 수정 계획

## 수정 이유

P2는 `SKILL.md` 목적, trigger, 제외 조건, `agents/openai.yaml` metadata가 일치하고 본문에만 숨은 trigger 규칙이 없어야 한다. 현재 skill은 broad scope는 충분하지만 DRF guardrail, cache/package sync, wrong-routing/role-map/reference-routing 같은 구체 trigger가 frontmatter description에 직접 드러나지 않는다.

## 수정 범위

- `dddjango/skills/source-reference-audit/SKILL.md`
  - frontmatter `description`에 DRF guardrail source decision, wrong-routing/role-map/reference-routing, runtime metadata/openai.yaml, source/runtime cache/package sync trigger를 추가한다.
  - Source Loading에서 source-authoring paths를 source evidence/cache parity evidence로만 제한하고 runtime-local reference를 우선 로드하게 한다.
  - 기존 제외 조건은 유지한다.
- `dddjango/skills/source-reference-audit/references/source-governance.md`
  - source/reference role, path-boundary, provenance, metadata/cache, leakage, validation/eval traceability 기준을 runtime-local summary로 둔다.
- `dddjango/skills/source-reference-audit/agents/openai.yaml`
  - `default_prompt`를 runtime metadata/cache sync와 wrong-routing evidence까지 포함하도록 조정한다.
  - `display_name`, `short_description`은 현재 기준에 맞으므로 불필요하게 바꾸지 않는다.

## 수정하지 말아야 할 범위

- source reference 자체는 수정하지 않는다.
- 새 optional interface field(`icon_small`, `icon_large`, `brand_color`, `dependencies`, `policy`)를 추가하지 않는다.
- eval pack과 다른 skill은 수정하지 않는다.
- Source reference의 장문 규칙을 SKILL.md에 복사하지 않는다.
- Source-authoring path를 runtime-facing allowed reference로 제시하지 않는다.

## 작업 체크리스트

- [x] `SKILL.md` frontmatter description에 body-only trigger로 지적된 표현을 추가한다.
- [x] `agents/openai.yaml` default_prompt를 SKILL.md scope와 맞춘다.
- [x] `SKILL.md` Source Loading을 source-authoring evidence-only wording으로 보정한다.
- [x] runtime-local bundled reference를 추가한다.
- [x] source skill 수정 후 runtime cache diff를 확인한다.
- [x] runtime cache가 다르면 runtime-sync analysis/plan을 작성한 뒤 cache를 동기화한다.
- [x] 필수 검증 명령과 source/runtime diff를 실행한다.
- [x] 독립 리뷰 결과를 통합해 Blocker 0, Major 0, 열린 Minor 0인지 재평가한다.

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
diff -qr dddjango/skills/source-reference-audit /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit
```

## 완료 조건

- `SKILL.md` 목적, trigger, 제외 조건이 frontmatter와 본문에서 충돌하지 않는다.
- `agents/openai.yaml` metadata가 `SKILL.md`와 일치하고 optional interface field를 추가하지 않는다.
- source skill과 runtime cache가 diff 없이 일치한다.
- 필수 validators가 통과한다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
