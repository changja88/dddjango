# P0 Goal Prompt - Inventory Freeze

```text
너는 dddjango Codex 플러그인 재구축 계획의 P0 Inventory를 수행한다.

목표:
현재 남아 있는 Codex plugin 본체와 source reference를 수정 없이 inventory하고, 이후 P1-P8의 기준점으로 사용할 현재 자산 목록을 repo 산출물로 고정한다.

대상:
- plugin root: dddjango/
- manifest: dddjango/.codex-plugin/plugin.json
- skills: dddjango/skills/*/
- source references: workspace/reference/*/reference/final.md
- plan governance: workspace/plan/

허용 수정 범위:
- workspace/plan/phases/p0-inventory/evidence/
- workspace/plan/indexes/artifact_index.md
- workspace/plan/status/phase_status.md
- 필요 시 workspace/plan/indexes/evidence_index.md

금지:
- dddjango/** 본문 수정 금지.
- workspace/reference/** 본문 수정 금지.
- eval runner, skill, reference, manifest 문제를 발견해도 고치지 말고 unknown/missing/provisional/issue로 기록한다.
- 과거 chat log, 과거 eval run, HTML report를 P0 완료 근거로 쓰지 않는다.

해야 할 일:
1. dddjango/.codex-plugin/plugin.json의 필수 필드, name, paths, Codex local/private 기준을 inventory한다.
2. plugin component set을 inventory한다: skills, agents/openai.yaml, references, scripts, assets, hooks, .mcp.json, .app.json.
3. dddjango/skills/*/SKILL.md 목록을 만들고 각 skill별 bundled resource 존재 여부를 표로 기록한다.
4. workspace/reference/*/reference/final.md 목록을 만든다.
5. skill과 source reference 관계를 known / unknown / missing / provisional로 분류한다.
6. 결과를 workspace/plan/phases/p0-inventory/evidence/<work-item>-inventory.md에 작성한다.
7. artifact_index.md에 산출물을 기록한다.
8. phase_status.md에서 p0-inventory 상태, last evidence, next action을 갱신한다.

필수 검증:
- python3 -B workspace/scripts/validate_plan_governance.py
- git diff --name-only로 P0 허용 범위 밖 수정이 없는지 확인한다.

완료 조건:
- P0 inventory evidence 파일이 존재한다.
- artifact_index.md에 evidence가 기록되어 있다.
- phase_status.md가 현재 상태와 last evidence를 반영한다.
- 모르는 관계는 고치지 않고 unknown/missing/provisional로 기록되어 있다.
- dddjango/**와 workspace/reference/** 본문이 수정되지 않았다.
- validate_plan_governance.py가 통과한다.

권한/승인:
- P0는 외부 model runner 또는 network가 필요 없다. 필요하다고 판단되면 먼저 사유를 기록하고 사용자 승인을 요청한다.
- 권한 문제로 필수 검증을 실행할 수 없으면 complete 금지. phase_status.md에 infrastructure-blocked로 기록한다.

최종 응답:
- inventory 산출물 경로
- artifact_index.md 갱신 여부
- phase_status.md 갱신 여부
- unknown/missing/provisional 요약
- 실행한 검증 명령과 결과
- P0 완료/미완료 판단
- Serena 사용 여부 또는 생략 이유
```
