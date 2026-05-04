# dddjango

`dddjango` packages Python and Django development standards as reusable agent skills for Claude Code and OpenAI Codex. It focuses on DDD, clean architecture, relational database design, Django 5.x, Django Ninja APIs, pytest, TDD, and clean code review.

The plugin is intentionally opinionated: Django REST Framework is not used. API design and implementation guidance should use Django Ninja.

## What Is Included

- `skills/architecture-*`: DDD, implementation patterns, database design, and API design guidance
- `skills/implementation-*`: Python, Django, Django Ninja, Django web, pytest, TDD, and clean code implementation guidance
- `commands/`: Claude Code slash command workflows for API, feature, refactor, test, and web work
- `workspace/`: development notes and evaluation artifacts; this is not part of the published plugin surface

## OpenAI Codex

This repository includes a Codex manifest at `.codex-plugin/plugin.json`, a packaged Codex plugin at `plugins/dddjango`, and a repo-local marketplace at `.agents/plugins/marketplace.json`.

For users, install the published Git-backed marketplace pinned to the latest release tag:

```bash
codex plugin marketplace add changja88/dddjango --ref v0.1.6
```

This registers the `dddjango-local` marketplace from the published repository. Then open the Codex plugin directory, select the `dddjango Local` marketplace, and install `dddjango`.

To update an existing installation after a new release:

```bash
codex plugin marketplace upgrade dddjango-local
```

For local development from this checkout:

```bash
codex plugin marketplace add .
```

## Codex Distribution Checklist

- Keep `.codex-plugin/plugin.json` and `plugins/dddjango/.codex-plugin/plugin.json` valid and versioned.
- Keep `.agents/plugins/marketplace.json` pointing at `./plugins/dddjango` with plugin name `dddjango`.
- Run `make test-release`.
- Run `make release` to update versions, commit, tag, and push the branch plus tag.
- Verify a clean Git-backed install from another environment with `codex plugin marketplace add changja88/dddjango --ref vX.Y.Z`.
- Run representative Codex prompts:
  - `Django Ninja API를 DDD 기준으로 설계해줘.`
  - `이 Django 코드를 클린 아키텍처 관점에서 리뷰해줘.`
  - `pytest와 TDD로 Django 기능을 구현해줘.`
- Confirm responses are Korean-first, reject DRF patterns, and use Django Ninja.

## Claude Code

For local development, load this repository as a plugin directory:

```bash
claude --plugin-dir .
```

Inside Claude Code, validate the plugin before sharing:

```text
/plugins validate .
```

When distributing through a Claude Code marketplace, point the marketplace entry at this repository and install it with:

```text
/plugins marketplace add changja88/dddjango
/plugins install dddjango@dddjango
```

The same operations can also be run from a shell:

```bash
claude plugin validate .
claude plugin marketplace add changja88/dddjango
claude plugin install dddjango@dddjango
```

This repository includes `.claude-plugin/marketplace.json`, so it can act as its own Claude Code marketplace after it is published.

## Evaluation

This repository has no build step. Validation is based on plugin structure checks and skill behavior evaluations.

Codex evaluation assets live under `evals/codex/`:

- `cases/pilot.jsonl`: 8-case pilot set for baseline vs `dddjango` comparison
- `rubrics/grading-schema.json`: 100-point weighted scoring schema
- `rubrics/dddjango-rubric.md`: manual grading rules and pass thresholds
- `scripts/init_iteration.py`: creates prompt files, answer keys, and grading templates
- `scripts/run_prompts.py`: runs generated prompts with `codex exec` and captures outputs
- `scripts/grade_outputs.py`: summarizes manual grades for `baseline` and `dddjango`
- `scripts/render_report.py`: renders a static HTML comparison dashboard

Use a separate Codex profile, machine account, or disposable environment for shared evaluation. Do not install or activate the plugin in a personal development profile when collecting comparable baseline data.

Recommended checks before a release:

1. Validate Claude plugin metadata with `/plugins validate .` or `claude plugin validate .`.
2. Run the Codex pilot evaluation from `evals/codex/cases/pilot.jsonl` against both `baseline` and `dddjango`.
3. Create an iteration workspace:

   ```bash
   python3 evals/codex/scripts/init_iteration.py --output workspace/codex-eval/iteration-1
   ```

4. Run each generated prompt in the matching `baseline` and `dddjango` environment. Prompt files intentionally exclude expectations and scoring focus to avoid evaluation leakage.

   ```bash
   python3 evals/codex/scripts/run_prompts.py --variant baseline --dry-run
   python3 evals/codex/scripts/run_prompts.py --variant baseline
   python3 evals/codex/scripts/run_prompts.py --variant dddjango --profile dddjango-eval
   ```

   Baseline runs use `--ignore-user-config` by default and execute from `/private/tmp/dddjango-codex-eval` to avoid this repository's `AGENTS.md` leaking dddjango guidance into the control group.

5. Grade outputs with `evals/codex/rubrics/grading-schema.json` and the generated `answer-key/` files.
6. Summarize manual grades:

   ```bash
   python3 evals/codex/scripts/grade_outputs.py workspace/codex-eval/iteration-1/grades.json
   ```

7. Render the browser report:

   ```bash
   python3 evals/codex/scripts/render_report.py workspace/codex-eval/iteration-1
   ```

   Open `workspace/codex-eval/iteration-1/report.html` in a browser to compare scores, duration, verdicts, notes, and raw output links.

8. Run representative prompts in both platforms:
   - `Django Ninja API를 DDD 기준으로 설계해줘.`
   - `이 Django 모델과 서비스 코드를 리뷰해줘.`
   - `pytest와 TDD 방식으로 Django 기능을 구현해줘.`
9. Confirm the response is Korean-first.
10. Confirm DRF patterns are rejected or rewritten as Django Ninja patterns.
11. Compare with and without the plugin for trigger accuracy, quality, token usage, and duration.

Raw evaluation outputs under `workspace/*/test/` are ignored. Commit evaluation seeds, reusable tooling, and summary reports only.

## Release Checklist

- Update `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` to the same version.
- Update `.claude-plugin/marketplace.json` to the same plugin version.
- Validate Claude local plugin loading.
- Validate Codex local marketplace installation.
- Run representative dual-platform prompts.
- Tag the release, for example `v0.1.6`.
- Update marketplace entries to the release version or tag.

You can create and publish a release with:

```bash
make release
```

The release command prompts for `patch`, `minor`, or `major`, updates plugin versions, runs metadata validation, creates a `chore: release vX.Y.Z` commit, creates the release tag, then pushes the current branch and release tag to `origin`.

## License

MIT
