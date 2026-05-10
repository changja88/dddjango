# Plugin Eval Goal

## Goal

`plugin` 평가는 `dddjango` 플러그인 패키지가 Claude Code와 Codex에서 공통으로 사용할 수 있는 skill bundle인지, 그리고 `skill-creator` 원칙과 dddjango reference source를 모두 지켜 작성되었는지 평가한다.

핵심 목표는 skill folder, frontmatter trigger, progressive disclosure, `agents/openai.yaml`, bundled `references/`, plugin manifest, marketplace entry, runtime/cache 동기화가 하나의 책임 계약을 유지하는지 확인하는 것이다.

## Reference Basis

평가 case는 다음 source를 함께 반영해야 한다.

- `/Users/hyun/.codex/skills/.system/skill-creator/SKILL.md`
- `workspace/docs/plugin-structure.md`, `skill-authoring.md`, `skill-contracts.md`, `skill-hierarchy.md`, `reference-index.md`, `validation-plan.md`
- `workspace/reference/*/reference/{final,internal,external,review}.md`
- `dddjango/skills/*/SKILL.md`, `dddjango/skills/*/agents/openai.yaml`, `dddjango/skills/*/references/*.md`
- `dddjango/.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `plugins/dddjango`

## Case Families

- Skill trigger quality: each `description` contains positive triggers, negative routing, Korean trigger vocabulary, and precedence without hiding trigger rules only in the body.
- Skill boundary fidelity: each skill follows `skill-contracts.md`; DDD, DB, API, Django, Ninja, Web, Python, TDD, Test, Clean Code, Workflow responsibilities do not bleed into each other.
- Progressive disclosure: `SKILL.md` stays concise, links directly to one-level `references/`, and does not copy source reference chapters into runtime instructions.
- Provisional handling: `architecture-implementation-patterns`, `implementation-django-ninja`, and `implementation-django-web` clearly state provisional/fallback source status and do not imply dedicated source references exist.
- Agents metadata: `agents/openai.yaml` `display_name`, `short_description`, and `default_prompt` semantically match the corresponding `SKILL.md`.
- Packaging: `dddjango/.codex-plugin/plugin.json`, marketplace entry, `plugins/dddjango` symlink/equivalent entry, and canonical `dddjango/` source are coherent.
- Runtime safety: no skill, reference, or metadata contains public eval packet text, `answer/` oracle content, prior run findings, or workspace-only source paths as final runtime references.

## Minimum Coverage

완성된 plugin eval pack은 위 Case Families마다 최소 하나 이상의 case를 가져야 한다. 특히 stale `agents/openai.yaml`, missing reference link, provisional overclaim, marketplace/symlink mismatch, leaked `answer` text, cache/source mismatch를 각각 독립 case로 덮는다. 단순 command audit 하나로 이 bucket을 완료 처리하지 않는다.

`skill-creator` 관점의 case는 다음을 구조화해 평가한다.

- Trigger description: positive signals, negative routing, Korean trigger terms, cross-skill precedence, body-only trigger rule 금지, 과도한 길이는 근거 필요.
- Skill folder shape: folder name exactly matches frontmatter `name`, and `SKILL.md` frontmatter contains only `name` and `description`.
- Agents metadata: `display_name`, 25-64 character `short_description` target or justified exception, one-sentence prompt shape, exact `$skill-name` in `default_prompt`, quoting/format validity, stale UI copy check.
- Skill body quality: actionable runtime rules, concise body, clear boundaries, conditional reference loading, no duplicated source material, honest verification reporting.
- Reference-routing matrix: every `references/*.md` maps to at least one prompt condition and at least one negative condition where it should not be loaded or used.
- Provisional per-field metadata: provisional/fallback status is visible in `SKILL.md` and user-facing metadata without implying complete dedicated source coverage.
- Runtime reference split content: each skill has the expected reference files from `plugin-structure.md`, not only one-level folder shape.
- DRF guardrail: any DRF-derived runtime reference is marked legacy/migration/comparison and never greenfield standard.
- Auxiliary docs ban: no README/install/changelog-style files inside skill folders.

## Answer Oracle

각 packaging/skill case는 `answer/case-*.yaml`에 evaluator-only oracle을 둔다. `answer`는 평가자가 볼 정답과 판정 기준이며 skill runtime, public prompt, plugin package에 포함되면 실패다.

`answer`는 최소한 다음을 담는다.

- target skill or package component
- required source references and expected responsibility boundaries
- required metadata fields and semantic match checks
- field-level `agents/openai.yaml` checks for display/short/default prompt values
- allowed provisional wording and forbidden overclaim wording
- reference-routing matrix expectations
- required validation commands
- packaging files that must exist and files that must not be introduced

## Evidence To Capture

- plugin tree and skill tree snapshots
- `SKILL.md` frontmatter/body review notes
- `agents/openai.yaml` semantic review notes
- reference link inventory and one-level reference check
- provisional skill status matrix
- plugin manifest, marketplace entry, symlink/equivalent entry
- validation command output

## Non-Goals

- README, installation guide, changelog 같은 보조 문서를 skill 안에 추가해 평가를 통과시키지 않는다.
- runtime cache만 고치고 canonical `dddjango/` source와 `workspace/docs` 근거를 비워 두지 않는다.
- `answer/` oracle이나 prior run finding을 skill 또는 plugin runtime 문서로 복사하지 않는다.

## Completion Gate

Plugin eval은 `workspace/develop/eval/plugin/cases/plugin/public/`에 하나 이상의 `case-*.md`가 있고, 같은 id의 `answer/case-*.yaml`이 존재할 때만 완료 후보가 된다.

구조 검증은 `python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`를 통과해야 한다. 별도 증거로 `dddjango/.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `plugins/dddjango` symlink 또는 동등한 packaging entry가 존재하며 canonical `dddjango/` source와 일치하는지 확인한다.

완료 판정은 validation command만으로 하지 않는다. 현재 runner가 plugin bucket을 first-class로 실행하지 못하면 dedicated validator/runner를 추가하거나 `cases`, `answer`, `fixtures`, `runs`를 실제로 소비하는 manual run protocol을 남겨야 한다.

`answer/`는 evaluator-only로 excluded workspace에 있어야 한다. Oracle은 skill-creator 원칙, field-level metadata, source reference coverage, trigger routing, reference-routing matrix, provisional handling, runtime reference split, packaging path/version consistency, leakage 방지를 모두 판정하고 그 결과가 `runs/<run-id>/analysis/` 또는 동등한 평가 산출물에 남아야 통과다.
