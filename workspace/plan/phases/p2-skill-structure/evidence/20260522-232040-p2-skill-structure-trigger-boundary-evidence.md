수정 대상: `dddjango/skills/**`, `workspace/plan/phases/p2-skill-structure/**`, `workspace/plan/indexes/**`, `workspace/plan/status/phase_status.md`

# P2 Skill Structure Evidence

## Metadata

| field | value |
|---|---|
| work item id | `20260522-232040-p2-skill-structure-trigger-boundary` |
| phase | `p2-skill-structure` |
| scope | `skill` |
| topic | `structure trigger boundary` |
| raw artifact path | `workspace/plan/phases/p2-skill-structure/evidence/20260522-232040-p2-skill-structure-trigger-boundary-evidence.md` |
| result | P2 skill structure checks passed with a local validator equivalent because upstream skill/plugin validators could not import PyYAML in this shell. |
| current-file match | current at evidence write; final hashes are recorded in `workspace/plan/indexes/evidence_index.md` |

## Inputs Checked

- P1.5 usage card artifact: `workspace/plan/phases/p1-5-usage-cards/cards/20260522-230605-p1-5-skill-usage-cards-evidence.md`
- P2 plan constraints: `workspace/plan/plugin_build_plan.md`
- Scope constraints: `workspace/plan/constraint_rules.md`
- Skill-creator reference: `/Users/hyun/.codex/skills/.system/skill-creator/references/openai_yaml.md`
- Plugin-creator reference: `/Users/hyun/.codex/skills/.system/plugin-creator/references/plugin-json-spec.md`
- Plugin manifest: `dddjango/.codex-plugin/plugin.json`
- Runtime skill roots: `dddjango/skills/*`

## Runtime Changes

| path group | change |
|---|---|
| `dddjango/skills/source-reference-audit/SKILL.md` | Tightened description from 121 to 92 words while preserving source/reference audit routing and application-behavior exclusions. |
| `dddjango/skills/workflow-dddjango-subagents/SKILL.md` | Tightened description from 126 to 114 words while preserving composite/risky workflow and subagent authorization boundaries. |
| `dddjango/skills/implementation-django-web/SKILL.md` | Removed explicit temporary absolute path examples from runtime text; kept repo-relative reporting rule. |
| `dddjango/skills/*/agents/openai.yaml` | Shortened all 13 `interface.default_prompt` values and aligned them with P1.5 usage-card trigger language while preserving explicit `$skill-name` mentions. |

No bundled reference, script, or asset file was moved or removed. No stale/placeholder bundled resource was found.

## Coverage Summary

| check | result |
|---|---|
| skills checked | 13 |
| `SKILL.md` frontmatter keys | all exactly `name`, `description` |
| folder basename/name match | 13/13 |
| description hard limit | 13/13 below 180 words and 1200 chars |
| body size | 13/13 below 500 lines and 3500 words |
| direct bundled reference links | 13/13 pass |
| references over 100 lines | none |
| `agents/openai.yaml` required interface fields | 13/13 pass |
| `default_prompt` mentions `$skill-name` | 13/13 pass |
| `policy.allow_implicit_invocation` conflicts | none; no explicit policy set |
| `dependencies.tools` conflicts | none; no dependencies declared |
| prohibited skill-local auxiliary docs | none |
| stale placeholder markers | none |
| plugin manifest path boundary | pass; skills path is `./skills/` and no `apps`/`mcpServers` companion mismatch exists |
| runtime absolute local path/path traversal/source-tree dependency scan | pass |
| `workspace/reference` runtime dependency | allowed only in `source-reference-audit` as audit target and explicit non-runtime warning |

## Validator Availability

| command | result |
|---|---|
| `python3 -B /Users/hyun/.codex/skills/.system/skill-creator/scripts/quick_validate.py dddjango/skills/architecture-api` | failed before validation with `ModuleNotFoundError: No module named 'yaml'` |
| `python3 -B /Users/hyun/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py dddjango` | failed before validation with `ModuleNotFoundError: No module named 'yaml'` |
| local stdlib-only P2 validator | pass; checked skill-creator-equivalent frontmatter/name rules, P2 size/link/resource rules, `agents/openai.yaml` shape, plugin manifest/path shape, and runtime boundary markers |

The local validator was used instead of installing dependencies because P2 did not require external installation/cache mutation and the objective allows an identical local validator when the quick/plugin validators are not runnable.

## Local P2 Validator Output

```text
LOCAL P2 VALIDATION PASSED
skills_checked=13
skill=architecture-api desc_words=113 desc_chars=912 body_lines=35 body_words=414 refs=4
skill=architecture-db desc_words=108 desc_chars=983 body_lines=35 body_words=596 refs=4
skill=architecture-ddd desc_words=108 desc_chars=841 body_lines=41 body_words=802 refs=4
skill=architecture-implementation-patterns desc_words=106 desc_chars=1010 body_lines=36 body_words=605 refs=4
skill=implementation-cleancode desc_words=85 desc_chars=858 body_lines=38 body_words=554 refs=4
skill=implementation-django desc_words=91 desc_chars=996 body_lines=36 body_words=578 refs=5
skill=implementation-django-ninja desc_words=93 desc_chars=930 body_lines=51 body_words=619 refs=4
skill=implementation-django-web desc_words=79 desc_chars=674 body_lines=35 body_words=492 refs=4
skill=implementation-python desc_words=82 desc_chars=850 body_lines=37 body_words=415 refs=4
skill=implementation-tdd desc_words=106 desc_chars=905 body_lines=39 body_words=592 refs=5
skill=implementation-test desc_words=104 desc_chars=960 body_lines=38 body_words=594 refs=5
skill=source-reference-audit desc_words=92 desc_chars=757 body_lines=69 body_words=819 refs=1
skill=workflow-dddjango-subagents desc_words=114 desc_chars=814 body_lines=79 body_words=1083 refs=4
```

## Runtime File Digests

| path | sha256 |
|---|---|
| `dddjango/skills/source-reference-audit/SKILL.md` | `85c4a4ad84279ccbfc6b91a27709c852ec0cb870c9940a7ca32469ef68a47367` |
| `dddjango/skills/workflow-dddjango-subagents/SKILL.md` | `21794c97017a84385cd792fa07065add00f42327596e14f6f005df7b9481200f` |
| `dddjango/skills/implementation-django-web/SKILL.md` | `20ff3ddf2b6b8ebcd76d3aa0dc68471907fca2dde98121d39806695dfde788bc` |
| `dddjango/skills/architecture-api/agents/openai.yaml` | `d0526cf5c67a48f7787df54798d33eb92b3d504367234e39c261be1d6fa1895a` |
| `dddjango/skills/architecture-db/agents/openai.yaml` | `fe51d4c0882ee433caf8fc531e57a0a4ab46b6d74f4496db097e5d4d19273fd6` |
| `dddjango/skills/architecture-ddd/agents/openai.yaml` | `3990e18f047e909197b1e1050699ff517ca78bbf95a05c10c4fb1f01d1c62a24` |
| `dddjango/skills/architecture-implementation-patterns/agents/openai.yaml` | `3c1e9456eb05534afad60835f8ca4f36ed22d79c49dbdb16c42a37736233c2d7` |
| `dddjango/skills/implementation-cleancode/agents/openai.yaml` | `a7d092afd919704db29adbfe5a0f214c4879adf7ba4c580664843017c692b897` |
| `dddjango/skills/implementation-django-ninja/agents/openai.yaml` | `e6a73ded8279fcf9c7b4d2c2fc6a0453fc3a0cafe2707e9898873dbed80f1a00` |
| `dddjango/skills/implementation-django-web/agents/openai.yaml` | `9a6db6aab378b8daccab857cc053b747ccdbd711b77ebca36d6d769b07d79684` |
| `dddjango/skills/implementation-django/agents/openai.yaml` | `479c1b258252db54ca129711921f7e5a67a92670e789fec4b9ce4ac02585fb1a` |
| `dddjango/skills/implementation-python/agents/openai.yaml` | `bb7d990cf32e068c00da6210c5198762ada9156212f476333770bd4305726065` |
| `dddjango/skills/implementation-tdd/agents/openai.yaml` | `c4dfd1fab34596be8fc8517c9d0708e20db3444c4e339f069ad896013a3301fa` |
| `dddjango/skills/implementation-test/agents/openai.yaml` | `a83083cb49e23b75c978b105c9050f70a39d1df6818589fcbefdcbd2cef99309` |
| `dddjango/skills/source-reference-audit/agents/openai.yaml` | `b82724c3b97713ed6ac1ada9bba8db8746c3451bf117e862606bd3dc5052dd51` |
| `dddjango/skills/workflow-dddjango-subagents/agents/openai.yaml` | `6292b37e28af6bb190c1e7272edcbafe557f8dd352fca53d95d025ed684f0a7a` |
| `dddjango/.codex-plugin/plugin.json` | `38b40eb1b7cd1020c8f6ca8bbca4ea286bd0a02cc90a49ce784b30181451743a` |

## Scope And Boundary

- Modified runtime files are under `dddjango/skills/**`.
- Modified planning files are under P2 phase directories, plan indexes, and phase status.
- No `workspace/reference/**` file was edited.
- No `workspace/develop/eval/**` file was edited.
- No external install/cache command was run.
- Serena was skipped because no Serena MCP tools were exposed in this session; repo root was verified with `pwd -P` and `git rev-parse --show-toplevel`.

## Final Verification

| command | exit | result |
|---|---:|---|
| `python3 -B workspace/scripts/validate_plan_governance.py` | 0 | `OK: plan governance validation passed` |
| local stdlib-only P2 validator | 0 | `LOCAL P2 VALIDATION PASSED`; 13 skills checked |
| `git diff --check` | 0 | no output |
| `git diff --name-only` | 0 | modified files limited to `dddjango/skills/**`, P2 phase index, plan indexes, and phase status; new P2 analysis/plan/evidence/closure files appear as untracked in `git status --short` |
| `git diff -- workspace/reference workspace/develop/eval` | 0 | no output |
| P2 allowed-scope check over `git status --short` | 0 | `P2 SCOPE CHECK PASSED`; 24 changed entries |
| runtime boundary scan with `rg -n '/Users/\|/private/\|/tmp\|/var/\|/home/\|/opt/\|/Volumes/\|\.\./\|workspace/develop/eval\|eval workspace\|source tree' dddjango/.codex-plugin dddjango/skills` | 1 | no matches |
| prohibited skill doc scan with `find dddjango/skills -type f ...` | 0 | no output |
| placeholder scan with `rg -n 'TODO\|PLACEHOLDER\|TBD\|FIXME\|\[TODO:' dddjango/.codex-plugin dddjango/skills` | 1 | no matches |
| `rg -n 'workspace/reference' dddjango/.codex-plugin dddjango/skills` | 0 | matches are only in `source-reference-audit`, where they describe source-reference audit targets and explicitly forbid runtime-facing `workspace/reference/**` use |

`git status --short` showed only the expected P2 runtime/doc/index/status changes:

```text
M dddjango/skills/architecture-api/agents/openai.yaml
M dddjango/skills/architecture-db/agents/openai.yaml
M dddjango/skills/architecture-ddd/agents/openai.yaml
M dddjango/skills/architecture-implementation-patterns/agents/openai.yaml
M dddjango/skills/implementation-cleancode/agents/openai.yaml
M dddjango/skills/implementation-django-ninja/agents/openai.yaml
M dddjango/skills/implementation-django-web/SKILL.md
M dddjango/skills/implementation-django-web/agents/openai.yaml
M dddjango/skills/implementation-django/agents/openai.yaml
M dddjango/skills/implementation-python/agents/openai.yaml
M dddjango/skills/implementation-tdd/agents/openai.yaml
M dddjango/skills/implementation-test/agents/openai.yaml
M dddjango/skills/source-reference-audit/SKILL.md
M dddjango/skills/source-reference-audit/agents/openai.yaml
M dddjango/skills/workflow-dddjango-subagents/SKILL.md
M dddjango/skills/workflow-dddjango-subagents/agents/openai.yaml
M workspace/plan/indexes/artifact_index.md
M workspace/plan/indexes/evidence_index.md
M workspace/plan/phases/p2-skill-structure/index.md
M workspace/plan/status/phase_status.md
?? workspace/plan/phases/p2-skill-structure/analysis/20260522-232040-p2-skill-structure-trigger-boundary-analysis.md
?? workspace/plan/phases/p2-skill-structure/closure/20260522-232040-p2-skill-structure-trigger-boundary-closure.md
?? workspace/plan/phases/p2-skill-structure/evidence/20260522-232040-p2-skill-structure-trigger-boundary-evidence.md
?? workspace/plan/phases/p2-skill-structure/plan/20260522-232040-p2-skill-structure-trigger-boundary-plan.md
```
