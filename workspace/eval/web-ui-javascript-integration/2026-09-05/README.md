# Controlled native UI JavaScript integration evaluation

This directory preserves the frozen requirements, independent browser/backstop harnesses, minimal generated apps, native role reports, and replay evidence for Task 3. Raw native JSONL traces remain under `/tmp/dddjango-web-js-integration-20260905/`; their paths and SHA256 hashes are recorded in each lane's `native-load-evidence.json`. Raw thinking, credentials, user profiles, staged skill duplicates and Python caches are not included in the app snapshots.

The external harness acts as Coordinator. Each lane executes native architect → independent design reviewer → coder → independent discipline reviewer roles, with real findings returned to their owning phase. This proves controlled role/skill execution. It does not prove marketplace installation, a full `/dddjango-web` Coordinator command, production integration, statistical model reliability, or all-browser compatibility.

The Claude lane uses the repository plugin through native `claude --plugin-dir ... --agent dddjango-web:<role>`. The Codex lane uses a byte-staged copy of the current distribution's `skills/` tree under the temporary app's `.agents/skills/` and explicit role skill invocation through `codex exec`. Neither lane installs a global plugin or changes user configuration. Per-call `*.command.json`, `*.launcher.json`, prompts and reports preserve actual configuration and path deviations; `runtime-versions.json` records CLI/Python/package versions.

## Replay the preserved apps without models

No model generation or authentication is needed to replay browser checks. The preserved app includes the actual generated `web/` source, minimal `host/` fixture, and pinned HTMX core. Core SHA256 is `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de`, from `https://raw.githubusercontent.com/bigskysoftware/htmx/v2.0.10/dist/htmx.min.js`. The host serves the `web` and `design_system` static namespaces and an empty `/favicon.ico` response; no server business API exists.

Tested dependencies: Python **3.14.7**, Django **5.2.17**, Playwright **1.62.0**, installed Google Chrome **152.0.7977.82** on macOS **26.6.2 arm64**. PyYAML **6.0.3** was available to native role checks but is not required by the browser harness itself. The test uses the installed Chrome executable and a fresh Playwright profile, never a user browser profile.

From the repository root, using a fresh temporary replay directory:

```bash
python3 -m venv /tmp/web-ui-eval-replay-venv
/tmp/web-ui-eval-replay-venv/bin/python -m pip install Django==5.2.17 playwright==1.62.0
export DDDJANGO_WEB_EVAL_ROOT=/tmp/web-ui-eval-replay
export DDDJANGO_WEB_EVAL_PYTHON=/tmp/web-ui-eval-replay-venv/bin/python
export DDDJANGO_WEB_EVAL_REPO="$PWD"
export DDDJANGO_WEB_EVAL_CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
eval_artifacts="$PWD/workspace/eval/web-ui-javascript-integration/2026-09-05"
mkdir -p "$DDDJANGO_WEB_EVAL_ROOT"
cp -R "$eval_artifacts/codex" "$DDDJANGO_WEB_EVAL_ROOT/codex"
cp -R "$eval_artifacts/claude" "$DDDJANGO_WEB_EVAL_ROOT/claude"
"$DDDJANGO_WEB_EVAL_PYTHON" "$eval_artifacts/browser_harness.py" codex replay-browser
"$DDDJANGO_WEB_EVAL_PYTHON" "$eval_artifacts/browser_harness_claude.py" replay-browser
"$DDDJANGO_WEB_EVAL_PYTHON" "$eval_artifacts/backstop_harness.py" codex replay-backstop
"$DDDJANGO_WEB_EVAL_PYTHON" "$eval_artifacts/backstop_harness.py" claude replay-backstop
```

Set the Chrome executable path for the replay machine. Ports 18751/18752 must be free. Use a new label or fresh replay directory for each backstop run. Each browser command starts and stops its own Django server and records JSON, HTTP logs and screenshots in the temporary lane directory. Browser startup blocked by an enclosing OS sandbox is an environment failure; it must not be reported as an application pass. During the recorded run, scoped automatic approval allowed isolated Chrome execution after an observed sandbox SIGABRT.

`backstop_harness.py` creates an isolated validation copy of `web/`, verifies source/copy hashes, initializes only that temporary copy as a Git repository, and creates a real empty-tree object. The canonical `--all --diff-base <empty-tree>` invocation treats every source file as new, so WS5 is exercised. It creates no commit and never touches the source repository's Git metadata. Plain non-Git `--all` is separately preserved where it ran and explicitly skipped WS5.

## Reading the evidence

- Frozen `evaluation-requirements.md` and `evaluation-oracle.md` are unchanged, with pre-generation hashes in `evaluation-input-hashes.json`. Clarifications are separate in `evaluation-clarifications.md`.
- Per-lane `app/design.md` and `generated-source-hashes.json` identify the exact final generated source. Final design/code audits are native role outputs, not harness-written approvals.
- Browser JSON records actual outgoing HTTP requests, returned HTML/revisions, object URL allocation/revocation, password type assignment counts, console/page errors and labelled injection conditions. A synthetic event is never used as HTTP-swap proof.
- Codex tests dependent-control replacement under a retained preview owner. Claude tests replacement of a preview owner as a dependent child of a retained outer panel. Both also test an independent note within a retained preview owner and a full panel replacement preserving its neighbor. These are distinct coverage boundaries.
- Codex timing injection delays Promise fulfillment after actual native PNG decode. Claude timing injection delays app load-handler delivery after an actual native image load. Both use actual HTTP swaps; the latter is explicitly not a claim about native browser task ordering.
- Failed HTTP 503 is deliberate and its expected console messages are preserved separately. Ordinary console errors are not blanket-filtered.

See `summary.md` for final outcomes, failure/review loops and the limits of this controlled evaluation.
