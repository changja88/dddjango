수정 대상: `workspace/plan/phases/p5-individual-eval/`, `workspace/plan/indexes/`, `workspace/plan/status/phase_status.md`

# P5 Model-Backed Installed-Runtime Plan

## Plan

1. Confirm P4.5 runtime parity is complete and the installed `dddjango` plugin is
   discoverable in the local Codex marketplace.
2. Attempt one representative installed-runtime model-backed P5 probe to confirm
   runtime availability before running the full individual matrix.
3. If external model execution requires approval, stop runtime execution and
   record the exact approval boundary instead of trying a workaround.
4. Check local OSS model providers only as a safer local alternative.
5. Add the narrow runner support needed to preserve model-backed command,
   stdout/stderr, final-answer JSON, metadata digests, and scoring output.
6. After explicit user approval, run the installed-plugin P5 affected bucket
   with the existing one-positive/one-negative-per-trigger-family case matrix.
7. Execute targeted model-backed runs twice for all new or modified cases.
8. Execute the affected bucket all-cases run and require pass, `not_scored == 0`,
   missing/malformed oracle JSON `0`, and current-file digest match.
9. Regenerate the report, run `validate-run`, compare raw/report artifacts, and
   only then update P5 closure to complete.

## Executed Commands

Targeted two-iteration installed-runtime run:

```bash
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-model-approved-targeted-with-plugin-v4 model-run-targeted-suite --bucket individual-skills --run-id p5-individual-skills-model-approved-targeted-with-plugin-v4 --iterations 2 --runtime-channel external --work-root /private/tmp/dddjango-p5-model --variants with-plugin
```

Affected bucket all-cases installed-runtime run:

```bash
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-model-approved-bucket-with-plugin-v4 model-run-bucket --bucket individual-skills --run-id p5-individual-skills-model-approved-bucket-with-plugin-v4 --runtime-channel external --work-root /private/tmp/dddjango-p5-model --variants with-plugin
```

Validation:

```bash
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-model-approved-bucket-with-plugin-v4 render-report
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-model-approved-bucket-with-plugin-v4 validate-run
```

## Approval Boundary

External `codex exec` model-backed P5 runs send the P5 case prompt, current
project instructions/context, and installed-plugin runtime context to the
external Codex/OpenAI runtime. This is the required approval phrase before
retrying that channel:

```text
I explicitly approve running P5 model-backed installed-runtime evals with `codex exec`, including sending the P5 case prompts, current project instructions/context, and dddjango installed-plugin runtime context to the external Codex/OpenAI runtime. Approved command shape: `codex -a never exec --json --ephemeral --skip-git-repo-check -C /private/tmp/dddjango-p5-model/<run>/<case-variant-iteration> -s read-only --output-schema <schema.json> -o <final.json> <case prompt>`.
```

## Local Alternative

If the external runtime should not be used, start one local provider and state
which provider to use:

- Ollama: start `ollama serve`.
- LM Studio: start `lms server start`.

The local provider path was not used for completion because the approved
external runtime produced the required model-backed artifacts.
