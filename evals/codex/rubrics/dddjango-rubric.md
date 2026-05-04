# dddjango Codex Evaluation Rubric

## Scope

Use this rubric to compare Codex responses without the plugin (`baseline`) against Codex responses with the `dddjango` plugin enabled (`dddjango`). Keep the prompt, model, reasoning effort, cwd, sandbox policy, and fixture identical between variants.

Do not install or activate the plugin in a personal development profile when running shared evaluation. Use a separate Codex profile, machine account, or disposable environment.

## Variants

- `baseline`: Codex without `dddjango` installed or enabled.
- `dddjango`: Codex with `dddjango` installed from the published Git-backed marketplace version under evaluation.

## Scoring

Score each case with `evals/codex/rubrics/grading-schema.json`. Each criterion is weighted. Award points from `0` to the criterion weight.

- `domain_fit` rewards correct Django, DDD, DB, API, and clean architecture judgment.
- `django_ninja_compliance` rewards Django Ninja usage and DRF rejection or conversion.
- `actionability` rewards directly usable code, structure, or review steps.
- `architecture_quality` rewards clear boundaries and transaction/dependency decisions.
- `testing_quality` rewards pytest/TDD/fixture quality.
- `korean_first` rewards Korean-first responses.
- `conciseness` rewards focused answers without losing needed detail.
- `safety` rewards avoiding destructive, unsupported, or overconfident guidance.

## Required Checks

For every `dddjango` result, record:

- whether the response is Korean-first
- whether DRF appears as an endorsed implementation choice
- whether Django Ninja appears when API implementation is requested
- whether the output uses task-appropriate DDD or clean architecture boundaries
- whether the answer is concrete enough for a developer to act on

## Success Criteria

The plugin evaluation passes the pilot gate when:

- average `dddjango` score is at least 15% higher than `baseline`
- DRF violations are 0
- Korean-first rate is at least 95%
- Django Ninja compliance is at least 90%
- TDD quality is at least 80% on TDD cases
- average token/time cost increase is not above 30% unless the quality lift justifies the cost
- negative-control pass rate is at least 80%

## Output Layout

Store raw outputs and manual grades under:

```text
workspace/codex-eval/iteration-N/
  baseline/
  dddjango/
  grades.json
  timing.json
  SUMMARY.md
```

Commit reusable cases, rubrics, and scripts. Do not commit large raw transcripts unless they are curated examples needed for future regression tests.
