# dddjango

`dddjango` packages Python and Django development standards as reusable agent skills for Claude Code and OpenAI Codex. It focuses on DDD, clean architecture, relational database design, Django 5.x, Django Ninja APIs, pytest, TDD, and clean code review.

The plugin is intentionally opinionated: Django REST Framework is not used. API design and implementation guidance should use Django Ninja.

## What Is Included

- `skills/architecture-*`: DDD, implementation patterns, database design, and API design guidance
- `skills/implementation-*`: Python, Django, Django Ninja, Django web, pytest, TDD, and clean code implementation guidance
- `skills/workflow-dddjango-subagents`: role-decomposed Django workflow guidance for complex tasks
- `commands/`: Claude Code slash command workflows for API, feature, refactor, test, and web work
- `workspace/`: development notes; this is not part of the published plugin surface

## OpenAI Codex

This repository includes a Codex manifest at `.codex-plugin/plugin.json`, a packaged Codex plugin at `plugins/dddjango`, and a repo-local marketplace at `.agents/plugins/marketplace.json`.

For users, install the published Git-backed marketplace pinned to the latest release tag:

```bash
codex plugin marketplace add changja88/dddjango --ref v0.1.9
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
  - `복잡한 Django 기능을 dddjango subagent workflow로 역할 분해해서 진행해줘.`
- Confirm responses are Korean-first, reject DRF patterns, and use Django Ninja.

`dddjango` supports subagent-driven Django workflows by providing role
decomposition, dddjango skill mapping, handoff contracts, integration rules, and
validation gates. It does not force Codex to spawn subagents. When subagents are
unavailable, the same role-based workflow can run sequentially.

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

## Release Checklist

- Update `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` to the same version.
- Update `.claude-plugin/marketplace.json` to the same plugin version.
- Validate Claude local plugin loading.
- Validate Codex local marketplace installation.
- Run representative dual-platform prompts.
- Tag the release, for example `v0.1.9`.
- Update marketplace entries to the release version or tag.

You can create and publish a release with:

```bash
make release
```

The release command prompts for `patch`, `minor`, or `major`, updates plugin versions, runs metadata validation, creates a `chore: release vX.Y.Z` commit, creates the release tag, then pushes the current branch and release tag to `origin`.

## License

MIT
