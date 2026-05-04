# dddjango

`dddjango` packages Python and Django development standards as reusable agent skills for Claude Code and OpenAI Codex. It focuses on DDD, clean architecture, relational database design, Django 5.x, Django Ninja APIs, pytest, TDD, and clean code review.

The plugin is intentionally opinionated: Django REST Framework is not used. API design and implementation guidance should use Django Ninja.

## What Is Included

- `skills/architecture-*`: DDD, implementation patterns, database design, and API design guidance
- `skills/implementation-*`: Python, Django, Django Ninja, Django web, pytest, TDD, and clean code implementation guidance
- `commands/`: Claude Code slash command workflows for API, feature, refactor, test, and web work
- `workspace/`: development notes and evaluation artifacts; this is not part of the published plugin surface

## Claude Code

For local development, load this repository as a plugin directory:

```bash
claude --plugin-dir .
```

Inside Claude Code, validate the plugin before sharing:

```text
/plugin validate .
```

When distributing through a Claude Code marketplace, point the marketplace entry at this repository and install it with:

```text
/plugin marketplace add changja88/dddjango
/plugin install dddjango@dddjango
```

This repository includes `.claude-plugin/marketplace.json`, so it can act as its own Claude Code marketplace after it is published.

## OpenAI Codex

This repository includes a Codex manifest at `.codex-plugin/plugin.json` and a repo-local marketplace at `.agents/plugins/marketplace.json`.

For local testing, open the Codex plugin directory, select the `dddjango Local` marketplace, and install `dddjango`. Restart Codex after changing plugin files so the local install picks up the latest version.

If you prefer CLI marketplace registration, use this repository root as the local marketplace source:

```bash
codex plugin marketplace add .
```

For Git-backed distribution, publish the repository and pin users to a release tag:

```bash
codex plugin marketplace add changja88/dddjango --ref v0.1.2
```

## Evaluation

This repository has no build step. Validation is based on plugin structure checks and skill behavior evaluations.

Recommended checks before a release:

1. Validate Claude plugin metadata with `/plugin validate .`.
2. Install the Codex plugin from `.agents/plugins/marketplace.json`.
3. Run representative prompts in both platforms:
   - `Django Ninja API를 DDD 기준으로 설계해줘.`
   - `이 Django 모델과 서비스 코드를 리뷰해줘.`
   - `pytest와 TDD 방식으로 Django 기능을 구현해줘.`
4. Confirm the response is Korean-first.
5. Confirm DRF patterns are rejected or rewritten as Django Ninja patterns.
6. Compare with and without the plugin for trigger accuracy, quality, token usage, and duration.

Raw evaluation outputs under `workspace/*/test/` are ignored. Commit evaluation seeds, reusable tooling, and summary reports only.

## Release Checklist

- Update `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` to the same version.
- Update `.claude-plugin/marketplace.json` to the same plugin version.
- Validate Claude local plugin loading.
- Validate Codex local marketplace installation.
- Run representative dual-platform prompts.
- Tag the release, for example `v0.1.2`.
- Update marketplace entries to the release version or tag.

You can prepare the local release commit and tag with:

```bash
make release
```

The release command prompts for `patch`, `minor`, or `major`, updates plugin versions, runs metadata validation, creates a `chore: release vX.Y.Z` commit, and creates the local release tag. It does not push; publish manually after review:

```bash
git push
git push origin vX.Y.Z
```

## License

MIT
