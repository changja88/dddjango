수정 대상: `workspace/plan/phases/p5-individual-eval/`, `workspace/plan/indexes/`, `workspace/plan/status/phase_status.md`

# P5 Model-Backed Installed-Runtime Evidence

## Summary

| field | value |
|---|---|
| work item id | `20260523-100711-p5-eval-model-backed-installed-runtime` |
| phase | `p5-individual-eval` |
| intended bucket | `individual-skills` |
| intended run id | `p5-individual-skills-model-approved-bucket-with-plugin-v4` |
| P4.5 runtime parity | complete |
| installed runtime | `dddjango@dddjango-local` installed and enabled |
| model-backed run status | targeted 2x pass and affected bucket all-cases pass |
| P5 completion status | complete for individual skill eval |
| blocker | none for P5; P3b runtime-routing evidence remains deferred by ADR-0004 before P7/P8 |

## Installed Runtime Check

Command:

```bash
codex plugin list --marketplace dddjango-local
```

Observed result:

```text
Marketplace `dddjango-local`
/Users/hyun/Desktop/dddjango/.agents/plugins/marketplace.json

PLUGIN                   STATUS              VERSION  PATH
dddjango@dddjango-local  installed, enabled  0.1.10   /Users/hyun/Desktop/dddjango/dddjango
```

## External Runtime Attempt

Initial representative probe command attempted before the model-runner scaffold
was schema-compatible:

```bash
codex exec --json --ephemeral --skip-git-repo-check -C /private/tmp/dddjango-p5-model/20260523-011456/p5-architecture-api-positive-with-plugin-1 -s read-only -a never -o /private/tmp/dddjango-p5-model/20260523-011456/p5-architecture-api-positive-with-plugin-1/final.txt 'P5 individual eval probe. Use the installed dddjango runtime plugin if the prompt triggers it. User prompt: 주문 생성 API URL, status code, 에러 응답, Idempotency-Key 계약을 정리해줘. Return a concise answer only.'
```

Escalation result:

```text
Rejected("This action was rejected due to unacceptable risk.
Reason: This would invoke an external Codex/OpenAI runtime and send project-specific prompt and session context off the machine, and there is no explicit user approval in this transcript delta for that concrete data export.
The agent must not attempt to achieve the same outcome via workaround, indirect execution, or policy circumvention. Proceed only with a materially safer alternative, or if the user explicitly approves the action after being informed of the risk. Otherwise, stop and request user input.")
```

Classification: infrastructure-blocked pending explicit user approval for this
data export and command shape.

After user approval on 2026-05-23, a corrected representative probe was run:

```bash
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-model-approved-probe model-run-one --case-id p5-architecture-api-positive --variant with-plugin --run-id p5-individual-skills-model-approved-probe --runtime-channel external --work-root /private/tmp/dddjango-p5-model
```

Observed result:

```text
{"status": "pass", "failure_semantics": []}
```

Raw artifacts:

- `workspace/develop/eval/runs/p5-individual-skills-model-approved-probe/raw/one.json`
- `workspace/develop/eval/runs/p5-individual-skills-model-approved-probe/raw/model-answer.schema.json`
- `workspace/develop/eval/runs/p5-individual-skills-model-approved-probe/raw/model-executions/p5-architecture-api-positive.with-plugin.stdout.jsonl`
- `workspace/develop/eval/runs/p5-individual-skills-model-approved-probe/raw/model-executions/p5-architecture-api-positive.with-plugin.stderr.txt`

This proved only one representative model-backed installed-runtime case. It was
not P5 completion evidence by itself because targeted two-iteration and affected
bucket all-cases model-backed runs had not yet passed.

The full targeted suite command was then attempted:

```bash
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-model-approved-targeted model-run-targeted-suite --bucket individual-skills --run-id p5-individual-skills-model-approved-targeted --iterations 2 --runtime-channel external --work-root /private/tmp/dddjango-p5-model
```

Escalation result:

```text
Rejected("This action was rejected due to unacceptable risk.
Reason: This broader targeted suite would export many project-specific prompts plus current instructions/context and installed-plugin runtime context to an untrusted external Codex/OpenAI service, which tenant policy denies for private workspace data despite general user approval to proceed.
The agent must not attempt to achieve the same outcome via workaround, indirect execution, or policy circumvention. Proceed only with a materially safer alternative, or if the user explicitly approves the action after being informed of the risk. Otherwise, stop and request user input.")
```

Classification: historical infrastructure block. The user later explicitly
approved the bulk P5 export boundary, so the model-backed installed-runtime
targeted suite and affected bucket were executed.

## Approved Model-Backed Targeted Suite

Command:

```bash
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-model-approved-targeted-with-plugin-v4 model-run-targeted-suite --bucket individual-skills --run-id p5-individual-skills-model-approved-targeted-with-plugin-v4 --iterations 2 --runtime-channel external --work-root /private/tmp/dddjango-p5-model --variants with-plugin
```

Observed result:

```text
{"status": "pass", "iterations": 2, "variance_status": "stable-pass"}
```

Targeted suite artifact:

- `workspace/develop/eval/runs/p5-individual-skills-model-approved-targeted-with-plugin-v4/raw/targeted-suite.json`
- `workspace/develop/eval/runs/p5-individual-skills-model-approved-targeted-with-plugin-v4/raw/targeted-run-1.json`
- `workspace/develop/eval/runs/p5-individual-skills-model-approved-targeted-with-plugin-v4/raw/targeted-run-2.json`

Targeted suite digest:

```text
targeted_suite=6eb41df11cb3080f429320376d06a04ce34aa4de425a54cc099838fb896cd158
metadata_digest=502cb2b7fc183d42a9e88e5606a808cff7e73bc70a504bb58db985b93ae44bfd
```

Classification: the model-backed installed-runtime targeted suite is stable
across two iterations for the affected installed-plugin variant.

## Approved Affected Bucket All-Cases Run

Command:

```bash
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-model-approved-bucket-with-plugin-v4 model-run-bucket --bucket individual-skills --run-id p5-individual-skills-model-approved-bucket-with-plugin-v4 --runtime-channel external --work-root /private/tmp/dddjango-p5-model --variants with-plugin
```

Observed result:

```text
{"status": "pass", "status_counts": {"pass": 26, "partial": 0, "fail": 0, "not-scored": 0}}
```

Report and validation:

```bash
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-model-approved-bucket-with-plugin-v4 render-report
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-model-approved-bucket-with-plugin-v4 validate-run
```

Observed result:

```text
{"status": "pass", "failures": []}
```

Raw artifacts:

- `workspace/develop/eval/runs/p5-individual-skills-model-approved-bucket-with-plugin-v4/raw/run.json`
- `workspace/develop/eval/runs/p5-individual-skills-model-approved-bucket-with-plugin-v4/raw/targeted-suite.json`
- `workspace/develop/eval/runs/p5-individual-skills-model-approved-bucket-with-plugin-v4/report/report.json`
- `workspace/develop/eval/runs/p5-individual-skills-model-approved-bucket-with-plugin-v4/report/report.html`
- `workspace/develop/eval/runs/p5-individual-skills-model-approved-bucket-with-plugin-v4/validation/validate-run.json`

Digest evidence:

```text
runner=7db3628e4a243f84c9de8963288eef5dd86933773ca37f520e44fb0c90945b6b
tests=3e0007bb69b84680107535e7de65326d5043b3adade0e0d0484e59e47609fd8a
cases=b5a53b96a15d887d13c74b232d31de8d59fa7de989b1b31369513b988c47376a
bucket_raw=f66fd2fa9536a9946bd312380b26a131e389cc6cacb68c29b19c44dc55e09160
bucket_report=edf3c3d3937295ea045e84f09be0832a498bad7323f8eef76353e891ce8a2d69
bucket_validation=28a2cd7be0943cc069319717f10a7612a21166ef79eb01613b1f079cf2fc2756
raw_digest=f6885d5f421141dce1c484a8f013955d217af7d321e60a641feedc47659a958e
metadata_digest=502cb2b7fc183d42a9e88e5606a808cff7e73bc70a504bb58db985b93ae44bfd
```

The validation artifact records `case_count=26`, `result_count=26`,
`model_backed=true`, `status_counts.pass=26`, `status_counts.not-scored=0`,
`failures=[]`, and matching current-file metadata digest.

## Runner Scaffold Evidence

The P5 runner now exposes model-backed installed-runtime commands:

- `model-run-one`
- `model-run-bucket`
- `model-run-targeted-suite`

The command builder uses structured final-answer JSON via `--output-schema`,
stores stdout/stderr/final-answer paths, records model-backed metadata, and
scores the final answer against the existing P5 oracle dimensions.
The targeted suite command records the required two-iteration model-backed gate
shape and variance status when a runtime channel is available.

Related unit tests:

```text
test_model_answer_json_scores_against_existing_oracle ... ok
test_model_answer_accepts_oracle_acceptable_loaded_skills ... ok
test_model_answer_accepts_process_skill_plus_expected_loaded_skill ... ok
test_model_run_one_uses_installed_runtime_command_for_with_plugin ... ok
test_model_targeted_suite_records_two_model_backed_iterations ... ok
test_validate_run_accepts_model_bucket_with_stable_targeted_suite_proof ... ok
test_validate_run_rejects_single_pass_model_backed_raw_as_completion_evidence ... ok
```

The validator now fails model-backed `raw/run.json` artifacts that still record
`flake_history.variance_status=single-pass provisional` or fewer than two
iterations unless a matching model-backed targeted-suite proof in the same raw
folder records `status=pass`, `iterations>=2`, and `variance_status=stable-pass`.
This prevents a one-off model-backed pass from satisfying P5 completion.

## Local Provider Attempts

Ollama command:

```bash
codex --oss --local-provider ollama -a never exec --json --ephemeral --skip-git-repo-check -C /private/tmp/dddjango-p5-model/20260523-011456/p5-architecture-api-positive-with-plugin-1 -s read-only -o /private/tmp/dddjango-p5-model/20260523-011456/p5-architecture-api-positive-with-plugin-1/final-ollama.txt 'P5 individual eval local OSS probe. User prompt: 주문 생성 API URL, status code, 에러 응답, Idempotency-Key 계약을 정리해줘.'
```

Observed result:

```text
WARNING: proceeding, even though we could not update PATH: Operation not permitted (os error 1)
Error: OSS setup failed: No running Ollama server detected. Start it with: `ollama serve` (after installing). Install instructions: https://github.com/ollama/ollama?tab=readme-ov-file#ollama
```

LM Studio command:

```bash
codex --oss --local-provider lmstudio -a never exec --json --ephemeral --skip-git-repo-check -C /private/tmp/dddjango-p5-model/20260523-011456/p5-architecture-api-positive-with-plugin-1 -s read-only -o /private/tmp/dddjango-p5-model/20260523-011456/p5-architecture-api-positive-with-plugin-1/final-lmstudio.txt 'P5 individual eval local OSS probe. User prompt: 주문 생성 API URL, status code, 에러 응답, Idempotency-Key 계약을 정리해줘.'
```

Observed result:

```text
WARNING: proceeding, even though we could not update PATH: Operation not permitted (os error 1)
Error: OSS setup failed: OSS setup failed: LM Studio is not responding. Install from https://lmstudio.ai/download and run 'lms server start'.
```

Classification: local model-backed alternative unavailable in the current
environment.

## Local Model-Run CLI Probe

Command:

```bash
python3 -B workspace/scripts/p5_individual_eval.py --fixture-root workspace/develop/eval/fixtures/individual-skills --output-dir workspace/develop/eval/runs/p5-individual-skills-model-local-probe model-run-one --case-id p5-architecture-api-positive --variant with-plugin --run-id p5-individual-skills-model-local-probe --runtime-channel ollama --work-root /private/tmp/dddjango-p5-model
```

Observed result:

```text
{"status": "not-scored", "failure_semantics": ["model-runner-error"]}
```

Raw artifacts:

- `workspace/develop/eval/runs/p5-individual-skills-model-local-probe/raw/one.json`
- `workspace/develop/eval/runs/p5-individual-skills-model-local-probe/raw/model-answer.schema.json`
- `workspace/develop/eval/runs/p5-individual-skills-model-local-probe/raw/model-executions/p5-architecture-api-positive.with-plugin.stdout.jsonl`
- `workspace/develop/eval/runs/p5-individual-skills-model-local-probe/raw/model-executions/p5-architecture-api-positive.with-plugin.stderr.txt`

The raw artifact records `model_backed=true`, `run_mode=model-backed-installed-runtime`,
`status=not-scored`, and `failure_semantics=["model-runner-error"]`. This is not
P5 completion evidence because no model final answer was produced.

## Individual Eval Matrix

| trigger family | positive case | negative case |
|---|---|---|
| REST API contract | `p5-architecture-api-positive` | `p5-architecture-api-negative` |
| Relational DB integrity and rollout | `p5-architecture-db-positive` | `p5-architecture-db-negative` |
| Domain modeling and invariants | `p5-architecture-ddd-positive` | `p5-architecture-ddd-negative` |
| Implementation architecture patterns | `p5-architecture-implementation-patterns-positive` | `p5-architecture-implementation-patterns-negative` |
| Maintainability review and refactor | `p5-implementation-cleancode-positive` | `p5-implementation-cleancode-negative` |
| Django ORM/service/migration implementation | `p5-implementation-django-positive` | `p5-implementation-django-negative` |
| Django Ninja API implementation | `p5-implementation-django-ninja-positive` | `p5-implementation-django-ninja-negative` |
| Django server-rendered web | `p5-implementation-django-web-positive` | `p5-implementation-django-web-negative` |
| Python language and typing implementation | `p5-implementation-python-positive` | `p5-implementation-python-negative` |
| TDD workflow | `p5-implementation-tdd-positive` | `p5-implementation-tdd-negative` |
| pytest and Django test mechanics | `p5-implementation-test-positive` | `p5-implementation-test-negative` |
| Source/reference governance | `p5-source-reference-audit-positive` | `p5-source-reference-audit-negative` |
| Coordinated dddjango workflow | `p5-workflow-dddjango-subagents-positive` | `p5-workflow-dddjango-subagents-negative` |

## P5 Gate Status

| gate | status |
|---|---|
| targeted model-backed run 2x | pass: `p5-individual-skills-model-approved-targeted-with-plugin-v4`, `variance_status=stable-pass` |
| affected bucket all-cases model-backed run | pass: `p5-individual-skills-model-approved-bucket-with-plugin-v4` |
| affected bucket not scored | `0` |
| missing/malformed oracle JSON | `0` |
| validate-run for model-backed run | pass, `failures=[]` |
| report regenerate and raw artifact comparison | pass; report `source_raw_digest` matches raw digest |
| current-file digest and run metadata digest match | pass; validation metadata digest `502cb2b7fc183d42a9e88e5606a808cff7e73bc70a504bb58db985b93ae44bfd` |
