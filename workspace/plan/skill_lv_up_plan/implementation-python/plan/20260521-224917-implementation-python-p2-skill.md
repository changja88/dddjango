수정 대상: skill

# implementation-python P2 skill 수정 계획

## 수정 이유

P2는 runtime-facing skill 표면이 실제 사용 조건, trigger, 제외 조건, metadata와 일치하는지 확인한다. 현재 `implementation-python`은 목적과 source 반영은 충분하지만, 본문에만 있는 workflow/subagent routing, 일부 Python-specific trigger coverage, `agents/openai.yaml` short description/default prompt metadata, bundled runtime reference의 source-authoring path 노출 문제가 남아 있다.

## 수정 범위

- `dddjango/skills/implementation-python/SKILL.md`
  - frontmatter `description`에 explicit subagent, role decomposition, parallel review, responsibility splitting 요청은 `workflow-dddjango-subagents`를 우선 사용한다는 routing을 추가한다.
  - `TypedDict`, type narrowing, decorators, `NamedTuple`, `match/case`, context managers, Python-version gates 같은 Python-specific trigger vocabulary를 추가한다.
  - 기존 Python implementation trigger와 adjacent skill routing, 제외 조건은 유지한다.
- `dddjango/skills/implementation-python/agents/openai.yaml`
  - `short_description`을 25-64자 quick-scan blurb로 줄인다.
  - `default_prompt`를 `$implementation-python`을 포함한 짧은 example prompt로 보정한다.
  - `display_name` 의미는 유지하고 optional interface field는 추가하지 않는다.
- `dddjango/skills/implementation-python/references/*.md`
  - runtime-facing bundled reference에서 `workspace/reference/**` source-authoring path를 제거한다.
  - source 근거 요약은 path 없는 문구로 유지한다.

## 수정하지 말아야 할 범위

- `workspace/reference/implementation-python/reference/final.md`는 P2 현재 판정에서 source gap이 없으므로 수정하지 않는다.
- bundled references의 세부 지침과 reference 분할 구조는 수정하지 않는다.
- 다른 dddjango skill, eval pack, validator는 수정하지 않는다.
- runtime cache는 source skill 수정 후 별도 runtime-sync analysis/plan에 따라 동기화한다.

## 작업 체크리스트

- [x] `SKILL.md` frontmatter에 workflow/subagent routing을 반영한다.
- [x] `SKILL.md` frontmatter에 Python-specific trigger vocabulary를 반영한다.
- [x] `agents/openai.yaml` short_description을 metadata 기준에 맞춘다.
- [x] `agents/openai.yaml` default_prompt를 짧은 example prompt로 보정한다.
- [x] bundled references의 source-authoring path 노출을 제거한다.
- [x] source skill과 runtime cache 차이를 확인한다.
- [x] runtime cache가 다르면 runtime-sync analysis/plan을 작성하고 동기화한다.
- [x] validators와 `diff -qr` 검증을 실행한다.
- [x] subagent 리뷰 결과를 통합하고 남은 Blocker/Major/열린 Minor를 닫는다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-python /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python`

## 완료 조건

- `SKILL.md` 목적, trigger, 제외 조건이 frontmatter와 본문에서 충돌하지 않는다.
- 본문에만 숨은 workflow/subagent trigger가 없다.
- `agents/openai.yaml`의 `display_name`, `short_description`, `default_prompt`가 `SKILL.md`와 일치한다.
- optional interface field가 추가되지 않았다.
- source skill과 runtime cache가 동일하다.
- 검증 통과와 리뷰 통합 결과가 Blocker 0, Major 0, 열린 Minor 0이다.

## 완료 확인

- `SKILL.md` frontmatter와 본문 routing이 충돌하지 않는다.
- `agents/openai.yaml` metadata는 `display_name`, `short_description`, `default_prompt`만 포함하며 optional interface field를 추가하지 않았다.
- bundled references의 runtime-facing `workspace/reference/**` path 노출을 제거했다.
- runtime cache 동기화와 검증 명령을 완료했다.
- 리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
