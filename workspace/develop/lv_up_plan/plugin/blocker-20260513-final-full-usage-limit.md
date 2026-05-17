# Blocker: Final Full Plugin Eval Usage Limit And Cache Sync

## Status

The plugin bucket goal is not complete.

## Why This Blocks Completion

The complete hard gate requires a latest full plugin bucket eval against the current source/cache state, with no failed, blocked, unscored, or missing artifacts.

After try 13:

- Targeted `case-plugin-cache-source-mismatch` passed and scored `with-ddjango = 5 / 5 pass`.
- Adjacent `case-plugin-leakage-sentinel` passed and scored `with-ddjango = 4 / 5 pass`.
- Deterministic validation passed locally.
- A fresh full bucket run was started as `20260513-final-full-plugin-try13`.
- The first case completed, but all later cases exited `1` because model-backed `codex exec` hit the usage limit.

Because the current-state full bucket run has missing/failed raw artifacts and cannot be scored, the complete hard gate is not satisfied.

## Evidence

- Final full run id: `workspace/develop/eval/plugin/runs/20260513-final-full-plugin-try13`
- Raw validation command:
  - `python3 workspace/scripts/validate_eval_run.py --bucket plugin --run-id 20260513-final-full-plugin-try13 --skip-oracle`
  - Result: fail, because all cases after `case-plugin-agents-metadata` exited `1`.
- Representative raw event:
  - `raw/case-plugin-cache-source-mismatch-baseline-events.jsonl`
  - Message: usage limit hit; retry after `6:28 AM`.
- Current local time when blocker recorded:
  - `2026-05-13 05:03:25 KST`

## Passing Evidence Before Blocker

- Try 13 targeted:
  - Run: `20260513-try13-source-runtime-no-boundary-evidence`
  - Case: `case-plugin-cache-source-mismatch`
  - Result: validated, `with-ddjango = 5 / 5 pass`
- Try 13 adjacent:
  - Run: `20260513-try13-adjacent-leakage`
  - Case: `case-plugin-leakage-sentinel`
  - Result: validated, `with-ddjango = 4 / 5 pass`
- Local checks after try 13:
  - `python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: pass
  - `python3 workspace/scripts/validate_eval_bucket_pack.py --bucket plugin`: pass
  - `git diff --check`: pass
  - `diff -rq dddjango /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`: pass
  - Leakage scan for exact forbidden/eval-specific phrases: no matches

## Next Step

Before completion, restore source/runtime cache sync, then after the new usage-limit reset time reported by `codex exec`, rerun the current-state full bucket with a new run id:

```bash
rsync -a dddjango/ /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/
diff -rq dddjango /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10
python3 workspace/scripts/run_eval_bucket.py --bucket plugin --run-id 20260516-final-full-plugin-try13c --timeout-seconds 1800 --rerun
python3 workspace/scripts/validate_eval_run.py --bucket plugin --run-id 20260516-final-full-plugin-try13c --skip-oracle
python3 workspace/scripts/evaluate_eval_run.py --bucket plugin --run-id 20260516-final-full-plugin-try13c --timeout-seconds 1800 --rerun
python3 workspace/scripts/validate_eval_run.py --bucket plugin --run-id 20260516-final-full-plugin-try13c
```

Do not mark the goal complete until that fresh full run scores successfully and the final completion audit has no open findings.

## Resume Attempt Before Reset

- Checked local time on resume: `2026-05-13 05:04:47 KST`.
- The usage-limit event says retry after `6:28 AM`, so the model-backed full eval was not retried.
- The goal remains incomplete and blocked on the fresh full bucket run.
- Checked local time on next resume: `2026-05-13 05:05:31 KST`.
- Still before the usage-limit reset time, so the model-backed full eval was not retried.
- Checked local time on next resume: `2026-05-13 05:06:02 KST`.
- Still before the usage-limit reset time, so the model-backed full eval was not retried.
- Checked local time on next resume: `2026-05-13 05:06:31 KST`.
- Still before the usage-limit reset time, so the model-backed full eval was not retried.

## Post-Reset Attempt

- Checked local time before retry: `2026-05-13 06:29:13 KST`.
- Started fresh full raw run: `20260513-final-full-plugin-try13b`.
- Raw runner exited `0`, but raw artifact validation failed:
  - Command: `python3 workspace/scripts/validate_eval_run.py --bucket plugin --run-id 20260513-final-full-plugin-try13b --skip-oracle`
  - Failed exits:
    - `case-plugin-provisional-overclaim` `with-ddjango`
    - `case-plugin-reference-split` baseline and `with-ddjango`
    - `case-plugin-trigger-routing` baseline and `with-ddjango`
- Representative failed events:
  - `raw/case-plugin-provisional-overclaim-with-dddjango-events.jsonl`
  - `raw/case-plugin-reference-split-baseline-events.jsonl`
  - `raw/case-plugin-reference-split-with-dddjango-events.jsonl`
  - `raw/case-plugin-trigger-routing-with-dddjango-events.jsonl`
  - Message: usage limit hit; try again at `May 16th, 2026 12:24 PM`.
- Current local time when this blocker was updated: `2026-05-13 06:41:50 KST`.
- Because the current-state full bucket raw run still has failed artifacts and cannot be scored, the complete hard gate remains blocked.

## Try 14 Source/Runtime Cache Sync Blocker

- Local review time: `2026-05-13 06:55:15 KST`.
- New try documents:
  - `workspace/develop/lv_up_plan/plugin/analysis/try-14-source-runtime-cache-resync.md`
  - `workspace/develop/lv_up_plan/plugin/plan/try-14-source-runtime-cache-resync.md`
- Source/runtime diff command:
  - `diff -rq dddjango /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10`
- Result:
  - `dddjango/skills/source-reference-audit/agents/openai.yaml` differs from the runtime cache copy.
- Direct diff scope:
  - Only `short_description` and `default_prompt` differ.
  - Source has the newer provenance/gaps/traceability/validation-coverage/source-runtime boundary wording.
  - Runtime cache still has older trigger metadata.
- Attempted correction:
  - `rsync -a dddjango/ /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/`
  - Escalation request was rejected by the automatic approval reviewer with the same usage-limit reset message.
- Current local deterministic checks after this finding:
  - `python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: pass
  - `python3 workspace/scripts/validate_eval_bucket_pack.py --bucket plugin`: pass
  - `git diff --check`: pass
  - Exact forbidden/eval-specific leakage scan: no matches
  - Source/runtime cache diff: not clean
- Because source/runtime cache sync is a complete hard gate and the cache write could not be performed, completion remains blocked even apart from the full model-backed eval quota.
