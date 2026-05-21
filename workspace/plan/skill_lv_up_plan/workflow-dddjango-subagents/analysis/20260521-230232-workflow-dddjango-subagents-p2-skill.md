수정 대상: skill

# workflow-dddjango-subagents P2 skill analysis

## 범위

- 대상 skill: `dddjango/skills/workflow-dddjango-subagents/`
- source reference: `workspace/reference/workflow-dddjango-subagents/reference/final.md`
- metadata 기준: `/Users/hyun/.codex/skills/.system/skill-creator/references/openai_yaml.md`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents/`

## 근거

- Source reference는 사용자 명시 trigger로 `role decomposition`, `role map`, `parallel review`, `sequential fallback`, `서브에이전트`, `역할 분해`, `역할 맵`, `병렬 검토`를 둔다.
- Source reference는 실제 subagent 실행 승인 경계로 `subagent`, `delegation`, `parallel agent work`를 구분한다.
- `SKILL.md` frontmatter는 trigger 판단에 쓰이는 표면이므로 본문이나 bundled reference에만 있는 실제 사용자 표현을 숨기면 안 된다.
- `agents/openai.yaml`은 `display_name`, `short_description`, `default_prompt`만 포함해야 하며, `default_prompt`는 `$workflow-dddjango-subagents`를 명시하는 짧은 prompt여야 한다.

## 평가

- 목적: `SKILL.md`는 coordination skill 목적, 실제 subagent 승인 경계, sequential fallback, handoff, integration을 설명하므로 source 목적과 대체로 일치한다.
- Trigger: `role map`, `delegation`, `parallel agent work`, `responsibility split` 같은 영어 사용자 표현이 frontmatter에 부족했고, loaded routing과 bundled delegation reference도 source의 한영 trigger 세트를 완전히 반영하지 않았다.
- 제외 조건: simple single-file changes, field rename, answer-only/tiny direct answers, decorative role-map-only, explicit opt-out이 frontmatter와 본문에 있어 source와 일치한다.
- Metadata: `agents/openai.yaml`은 optional interface field를 추가하지 않았지만 `default_prompt`가 두 문장으로 다소 길었고 `role map` trigger를 직접 드러내지 않았다.
- Role map: source의 Domain Agent 책임은 `bounded context`, `ubiquitous language`인데 runtime table은 `context`, `language`로 축약되어 축소 오해 여지가 있었다.
- Reference: dedicated source reference는 P2 판단 축을 충분히 다루므로 별도 reference 후속 분석은 필요하지 않다.
- Cache: 수정 전 source skill과 runtime cache는 `diff -qr` 기준 동일했다. skill 수정 후 runtime-sync 분석/계획과 cache sync가 필요하다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real subagent 2개를 read-only로 실행했다.

skill-creator 리뷰: `SKILL.md` 목적 명확성, frontmatter trigger, progressive disclosure, `agents/openai.yaml` 정합성을 점검했다.

독립 P2 리뷰: source reference와 runtime skill, metadata, bundled references, cache sync 위험을 비교했다.

## 리뷰 결과

리뷰 결과: Blocker 0, Major 1, 열린 Minor 2

- Major: source reference와 body/reference에 있는 실제 trigger 표현이 frontmatter와 runtime routing에 충분히 반영되지 않았다.
- Minor: `agents/openai.yaml` default prompt가 길고 두 문장이다.
- Minor: canonical role table 중 Domain Agent 책임이 source보다 축약되어 보일 수 있다.
- Note: `SKILL.md`와 bundled `role-map.md`의 role table 중복은 core runtime guidance로 유지한다. Drift risk는 validator와 runtime/cache parity로 관리한다.

## 수정 필요성

Blocker는 없지만 Major가 있어 P2 종료 조건을 만족하지 못한다. Trigger coverage, metadata prompt, Domain Agent canonical wording을 좁게 수정한 뒤 재평가해야 한다.

## 수정 후 재평가

- Frontmatter `description`에 source reference의 실제 한영 trigger 표현인 `role map`, `delegation`, `parallel agent work`, `responsibility split`, `parallel review`, `sequential fallback`, `서브에이전트`, `역할 분해`, `역할 맵`, `병렬 검토`가 노출됐다.
- `Routing`과 `references/delegation-rules.md`의 explicit trigger 목록이 frontmatter와 source reference의 trigger family를 반영한다.
- Domain Agent 책임은 `bounded context`, `ubiquitous language`를 포함해 source canonical role wording과 맞췄다.
- `agents/openai.yaml`은 optional interface field 없이 `display_name`, `short_description`, `default_prompt`만 유지하며, `default_prompt`는 `$workflow-dddjango-subagents`를 포함하는 한 문장으로 positive scope와 simple/tiny/opt-out guard를 함께 담는다.
- `SKILL.md`의 canonical role table은 `validate_skill_docs.py`가 요구하는 runtime-visible core guidance로 유지했고, `role-map.md`를 bundled parity reference로 명시했다.
- Source reference 자체는 P2 판단 축을 충분히 다루므로 `reference_lv_up_plan/workflow-dddjango-subagents/analysis/`에 새 P2 reference 후속 분석을 만들지 않았다.

## 검증 결과

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`: 통과, `OK: plan constraints passed`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`: 통과, `Ran 23 tests ... OK`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: 통과, `OK: validation passed with 0 warning(s)`
- `diff -qr dddjango/skills/workflow-ddjango-subagents /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents`: 통과, 출력 없음

## 최종 리뷰 결과

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

- skill-creator 관점 final re-review: 이전 trigger Major, metadata Minor, progressive-disclosure Minor가 닫혔다. Validator가 `SKILL.md` role table을 요구하므로 role table duplication은 open Minor가 아니라 runtime-visible core guidance와 bundled parity reference의 의도적 중복으로 판단했다.
- 독립 P2 final re-review: 이전 trigger Major, Domain Agent wording Minor, `agents/openai.yaml` negative-routing Minor가 닫혔다.
- 실행하지 않은 검증, eval, browser check, Serena 사용은 완료로 기록하지 않았다.
