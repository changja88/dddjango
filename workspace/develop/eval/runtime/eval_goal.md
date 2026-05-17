# Runtime Eval Goal

## Goal

`runtime` 평가는 설치되거나 cache된 `dddjango` plugin이 실제 Codex runtime에서 최신 skill metadata, reference routing, role map, packaging boundary를 노출하고, baseline에는 그 정보가 섞이지 않는지 평가한다.

핵심 목표는 workspace canonical source와 runtime cache가 같은 책임 계약을 유지하는지, 그리고 runtime visibility가 평가를 오염시키지 않으면서 `with-dddjango`에만 필요한 정보를 제공하는지 확인하는 것이다.

## Reference Basis

평가 case는 다음 source를 함께 반영해야 한다.

- `workspace/docs/plugin-structure.md` runtime sync 기준
- `workspace/docs/workflow.md` canonical role map
- `workspace/docs/validation-plan.md` runtime role-map sync, skill folder validation, provisional handling
- `workspace/docs/skill-authoring.md` metadata/default prompt 기준
- `workspace/reference/*/reference/{final,internal,external,review}.md`
- runtime `dddjango/skills/*/SKILL.md`, `agents/openai.yaml`, `references/*.md`
- installed plugin cache path under `plugins/cache/dddjango` or equivalent runtime cache

## Case Families

- Prompt-input exposure: `with-dddjango` prompt-input에 요청과 관련된 `dddjango:*` skill metadata, description, reference hints가 최신 상태로 노출되는가.
- Baseline isolation: baseline은 `--ignore-user-config`, `--ignore-rules`, sanitized workspace로 plugin metadata, cache path, canonical source path, answer oracle을 보지 못하는가.
- Role-map sync: runtime `workflow-dddjango-subagents` `SKILL.md`와 `references/role-map.md`가 `workspace/docs/workflow.md`의 roles, responsibilities, related skills를 축소하지 않는가.
- Reference loading boundary: runtime references are one-level, directly linked from `SKILL.md`, and do not point to workspace-only source paths as final instructions.
- Cache/source consistency: cache 보정이 있었다면 같은 의도가 canonical `dddjango/` source와 `workspace/docs`에 반영되어 있는가.
- Provisional visibility: provisional skills expose fallback status and do not claim dedicated source references exist.
- Evaluation contamination: public case, `answer/` oracle, prior run artifacts, private scoring notes do not appear in runtime prompt-input or bundled references.

## Minimum Coverage

완성된 runtime eval pack은 prompt-input exposure, baseline isolation, stale cache, missing skill metadata, wrong routing despite metadata, private-material request, answer leakage sentinel을 각각 독립 case로 덮어야 한다. 단순 runtime smoke command 하나로 이 bucket을 완료 처리하지 않는다.

Runtime checks는 모든 installed/cached skill에 대해 다음을 확인한다.

- bundled reference files match the split plan in `plugin-structure.md`
- positive triggers, negative routing, and cross-skill precedence are exposed consistently
- provisional skills do not imply dedicated source references exist
- DRF content is legacy/migration/comparison only, not greenfield standard
- no workspace-only source path, public eval packet, `answer/` oracle, or private evaluator material appears in runtime references

## Answer Oracle

각 runtime case는 `answer/case-*.yaml`에 evaluator-only oracle을 둔다.

`answer`는 최소한 다음을 담는다.

- expected runtime paths and canonical source paths
- required and forbidden prompt-input patterns
- required role-map responsibilities and related skills
- required cache/source sync evidence
- expected baseline isolation fields
- leakage patterns for `answer/`, prior runs, private evaluator text, workspace-only source paths
- hard gates for evaluator leakage, prompt-input exposure mistakes, unsupported command claims, and unsupported subagent claims
- `control_case` label when safety, honesty, or restraint behavior makes baseline pass acceptable
- `expected_outcomes` for baseline, `with_dddjango`, expected delta, and whether baseline pass is acceptable

## Evidence To Capture

- `codex debug prompt-input` output or runner prompt-input artifact
- baseline isolation JSON
- runtime skill folder/cache snapshot
- canonical source vs cache comparison
- `validate_skill_docs.py --phase runtime` output
- answer oracle evaluation notes

## Non-Goals

- runtime smoke 결과만으로 skill authoring 품질 전체를 통과 처리하지 않는다.
- cache-only hotfix를 최종 완료로 보지 않는다.
- baseline output/operator prompt에 `dddjango` skill metadata가 등장하면 유효한 비교로 보지 않는다.

## Completion Gate

Runtime eval은 `workspace/develop/eval/runtime/cases/plugin/public/`에 하나 이상의 `case-*.md`가 있고, 같은 id의 `answer/case-*.yaml`이 존재할 때만 완료 후보가 된다.

`python3 workspace/scripts/validate_skill_docs.py --phase runtime`은 smoke gate로 사용하되, 그것만으로 완료하지 않는다. 하나 이상의 실제 eval case에서 `with-dddjango` prompt-input artifact가 현재 `dddjango:*` skill metadata와 workflow role-map exposure를 포함하는지 확인해야 한다.

동시에 baseline output/operator prompt에는 skill metadata, cache path, canonical plugin source path, `answer/` oracle이 없어야 한다. 현재 runner가 runtime bucket을 first-class로 실행하지 못하면 dedicated runtime validator/runner를 추가하거나 `cases`, `answer`, `fixtures`, `runs`를 실제로 소비하는 manual run protocol을 남겨야 한다.

`baseline-isolation.json`의 `pass`가 `true`이고, protocol validation과 workspace source/generated plugin 검증이 runtime/baseline 요구사항을 덮으며, `answer/` oracle 판정 결과가 남아야 통과다. Runtime validator는 prompt-input artifact를 파싱해 exposed skill ids/descriptions/reference hints/role-map을 canonical `dddjango/skills`와 `workspace/docs/workflow.md`에 대조해야 한다.
