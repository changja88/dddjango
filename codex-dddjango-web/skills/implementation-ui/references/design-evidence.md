# Design evidence file contract

This reference defines the machine-readable boundary used by
`check_design_evidence.py`. JSON files identify bytes and results. Put the
human comparison, differences, interactions checked, and any remaining doubt
only in `visual-check.md`.

## Command sequence and exits

Run from an installed plugin with explicit absolute or working-directory paths:

```bash
python scripts/check_design_evidence.py --build BUILD --project-root PROJECT --phase inputs
python scripts/check_design_evidence.py --build BUILD --project-root PROJECT --phase visual --fingerprint
python scripts/check_design_evidence.py --build BUILD --project-root PROJECT --phase visual
python scripts/backstop.py PROJECT --diff-base COMMIT --design-build BUILD
```

`--fingerprint` validates inputs and prints calculated `input_digest` and
`implementation_digest`; it never writes or updates an evidence file. Record
those printed values only for a new observation round. Exit 0 means the
declared phase is consistent, 1 means a usage/internal error prevented the
check, and 2 means a defect or insufficient evidence. An interaction document
with a non-null `environment_error` counts as the former, not a defect: the
collection never finished, so every phase (prepare/inputs/visual) exits 1
rather than 2. Re-freezing discards the frozen evidence wholesale and rebuilds it
(`refreeze.py`, see `design-acquisition.md`); it produces no comparison and no
exit code this checker reads. `--phase visual` always
rechecks inputs. `backstop.py --design-build` joins the visual phase to the
existing 26 checks; `--only` cannot disable it. Without `--design-build`, the runner
discovers source-bearing builds under `PROJECT/.dddjango-web/` and validates all
of them. Git index/HEAD paths retain deleted source records as design signals;
deleted config/build-state records are read from the index and then HEAD.
An explicit build selects one discovered project build; an unrelated external
passing folder cannot replace it. External build locations remain supported when
there is no project-local source-bearing build. A `design_source` object of type
`PROJECT` (or a legacy Claude Design pointer without a type) without a discoverable
build requires an explicit build path. `DESIGN_SYSTEM` token pointers alone do not
signal a screen design.

A non-design run may omit `--design-build` without rechecking completed history
only when its valid `--diff-base` resolves to exactly one current state's
`git_snapshot`, that state says `has_design_screen=false`, and its build has no
source markers. Every historical design build must explicitly be `finalize`,
`g2_approved=true`, `implementation_visual=verified`, `design_status=ready`, with
all recorded slices done. Config and other build records must be unchanged since
the base, including deletions and untracked files. The runner prints a skip notice;
missing or ambiguous conditions retain the full design check. Explicit build
selection still identifies the requested build; it does not infer or authenticate
the user's current scope from a folder name. The final blocker total
includes structural and design defects. Completion/CI uses the runner exit code,
never a filtered structural-only output line.

## `design-input.json` version 1

Evidence pointer paths and manifest-list paths are relative to `BUILD` and
remain confined there. `reference_root` is a directory relative to `BUILD`.
Every manifest's `files[].local_path`, `entrypoint`, and every case
`entrypoint.path` are relative to `reference_root`. This supports independently
frozen entrypoints in one unchanged source tree. `host_files`, when present, contains
approved paths relative to `PROJECT`; these bytes join the implementation
digest. Every pointer object has exactly `path` and the lowercase SHA-256 of
the referenced bytes.

```json
{
  "version": 1,
  "reference_root": "design-ref",
  "manifests": [
    "login-source-manifest.json",
    "profile-source-manifest.json"
  ],
  "scope": {"path": "scope.md", "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
  "coverage_review": {"path": "coverage-review.md", "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},
  "host_files": ["config/urls.py"],
  "cases": [
    {
      "id": "login/default",
      "screen": "login",
      "state": "default",
      "viewport": [1280, 720],
      "scope_refs": ["scope.md#login-default"],
      "entrypoint": {"path": "login/screen.html", "sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"},
      "reference_capture": {"path": "captures/login-original.png", "sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"},
      "media": [
        {
          "id": "hero-video",
          "kind": "video",
          "environment": "staging",
          "endpoint": "/api/media/hero",
          "identity_pointer": "/asset/id",
          "source_pointer": "/asset/src"
        }
      ]
    }
  ]
}
```

`cases` and `manifests` are nonempty. Case IDs are unique; viewport values are
positive integer `[width, height]`; `scope_refs` is a nonempty list. The
entrypoint path/hash must match a successful row in one listed manifest. Each static
manifest must be version 1, `source_ready: true`, have a nonempty successful
file list and a valid entrypoint. The checker compares every recorded path,
size and hash with local bytes and rescans supported static dependencies. A
reference capture must be a valid image container. A valid original image may
be both entrypoint and reference capture.

Two more top-level/case fields are allowed beyond this shape. A top-level
`interaction_exclusions` list and a per-case `reached_by` object carry the
interaction-evidence exemptions and case-to-surface bindings defined in full in
"`interactions.json` version 1" below; `reached_by` is required on every
archive HTML/component case and forbidden on a static or image case.
Unrecognized manifest row fields are rejected.

Static collection supports HTML/CSS literal resources, `x-import`, literal ES
imports, literal dynamic imports, `export ... from`, and literal imports in
inline script/module bodies. Comments, quoted strings, inert template chunks,
and regular-expression bodies do not create imports. Imports inside template
interpolations are scanned; malformed/ambiguous template interpolation is
explicitly unsupported. Detected nonliteral imports, JSX `src`/`href`/`poster`
expressions, and bare module specifiers are blocked. There is no JavaScript executor, bundler,
import-map resolver, or claim of complete runtime dependency discovery.
Runtime-only resources require original-browser observation and independent
audit.

For multiple entrypoints, run each collection against the same reference root
and give it a distinct sibling manifest:

```bash
python scripts/freeze_design.py SOURCE/login.html --out BUILD/design-ref --manifest BUILD/login-source-manifest.json
python scripts/freeze_design.py SOURCE/profile.html --out BUILD/design-ref --manifest BUILD/profile-source-manifest.json
```

This is compatible with the existing sibling-manifest convention; no manifest
migration or rewritten `local_path` is required.

## Original engine source archives

For a dynamic design engine/export, follow `design-acquisition.md`. The archive
collector preserves the entire supplied tree without static dependency claims.
An archive manifest has `version: 1`, `collection: "archive"`,
`archive_ready: true`, `source_ready: false`, and the usual entrypoint/source_root/files.
The collector also records `dependencies` for its entrypoint: each row contains
`source_document`, `source`, `kind`, `local_path`, `status`, and `reason`. Status is
`ok` (local file present), `missing` (absent/escaping local path), `inline`,
`external`, or `runtime`. Missing literal local dependencies make collection exit 1;
the copied bytes and report remain available. `archive_ready` only describes byte
preservation. Remote/dynamic references still require original browser observations.
For every case, this checker recomputes local dependencies from frozen bytes, even
for old archives without this report. A matching partial inventory cannot hide a
missing component, stylesheet, script, or asset. Non-case archived screens are not
treated as required rendering entrypoints.
Use exactly one archive manifest for the entire reference_root; cases may point to
different original HTML/JSX rows in it. Do not mix or duplicate per-screen manifests
in the archive path. Its manifest lives outside reference_root. Its full file inventory (except
`.DS_Store`) must exactly match reference_root; symlinks and changed/missing/extra
files fail. Empty non-entry files are preserved. This is an original source archive,
not a successful static source manifest with failures excused. Static manifests
retain every previous byte, type and dependency-closure requirement.

An archive case entrypoint must identify an original HTML/JSX row. Every such case
requires a `source_observation` path/sha256 pointer relative to BUILD. It points to:

```json
{
  "version": 2,
  "archive_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "entrypoint": {"path": "screen.dc.html", "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},
  "case_id": "login/default",
  "screen": "login",
  "state": "default",
  "viewport": [390, 844],
  "url": "http://127.0.0.1:9000/screen.dc.html",
  "observed_at": "2026-09-07T03:30:00Z",
  "capture": {"path": "captures/login-original.png", "sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"},
  "trace": {"path": "captures/login-original-observation.json", "sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"},
  "interactions": {"path": "captures/login-original-interactions.json", "sha256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"}
}
```

`version` is 1 or 2. Version 2 adds the `interactions` pointer shown above,
addressing the collector document defined in "`interactions.json` version 1"
below, and is required for every archive HTML/component case. A version 1
pointer (without `interactions`) still passes only when `backstop.py`'s
discovered-build run allows it as a legacy observation: the build folder is
fully git-tracked and unchanged against `--diff-base` (or `HEAD`) with no
untracked or ignored files in it. That allowance is a property of the specific
`backstop.py` run, not of the build folder by itself, and `check_design_evidence.py`
called directly still requires version 2 unless its own caller passes the same
legacy flag. A build with any local edit, once touched again, needs a fresh
version 2 observation; there is no partial or author-declared exemption.

The archive hash is the hash of the manifest bytes. Entrypoint, case ID, screen,
state, viewport and capture must match the case exactly. The trace is nonempty
actual browser output, not a Coordinator assertion that rendering passed. It
includes the observed URL, browser viewport, selected content boundary/crop,
state transition actions, DOM/style/resource observations and failed requests.
The case viewport describes the implementation comparison viewport; when an
engine canvas contains several screens, record its actual browser viewport and
content crop separately in the trace. Never silently equate them. The independent
reviewer checks the original URL/version, crop/state correspondence, resource
completeness, font fallback and visual content; JSON consistency cannot prove them.
All archive bytes and observation/trace/capture bytes enter the input digest.

Before the independent coverage review, use `--phase prepare`. This validates
source/observation connections and returns a `review_digest` that excludes the
coverage review pointer/content to avoid a circular hash. `coverage_review` may
be null during preparation. **Prepare success never authorizes implementation.**
Give the digest and all actual inputs to the independent reviewer. Preserve their
returned report verbatim with these two standalone lines:

```text
reviewed-input: <review_digest from the preparation command>
review-result: pass
```

A failed independent review returns `review-result: fail`; do not rewrite it.
After preserving the review and updating its pointer, run the actual `inputs`
phase. Archive inputs require a matching reviewed-input and pass result, as well
as the original browser evidence. Changed source/cases/observations require fresh
preparation and independent review. A fingerprint is not a new observation.
The prepare command is usable before web/ implementation exists. The existing
`--fingerprint` behavior still requires valid inputs and web/ implementation.

## `interactions.json` version 1

A version 2 `source_observation.interactions` pointer addresses this document.
It is the collector's own report of every operable control it found under the
frozen archive's root and how it drove them; nobody hand-authors or hand-edits
it.

```json
{
  "version": 1,
  "collector": {"name": "interaction_audit", "snippet_sha256": "…", "driver": "observe_interactions.pw.js", "driver_sha256": "…",
                "path": "node|mcp", "capabilities": {"react_props": true, "cdp_listeners": true}},
  "archive_sha256": "…", "entrypoint": {"path": "screen.dc.html", "sha256": "…"},
  "url": "http://127.0.0.1:9000/screen.dc.html", "browser_viewport": [560, 1040], "content_crop": {"x": 85, "y": 98, "w": 390, "h": 844},
  "root": {"selector": "[data-screen-label=\"관계인\"]", "found": true, "fingerprint": {"tag": "div", "label": "관계인", "descendants": 412, "rect": {"x": 85, "y": 98, "w": 390, "h": 844}}},
  "outside_root": {"count": 0, "sample": []}, "excluded_regions": [],
  "served": {"screen.dc.html": "…", "support.js": "…", "_ds/…/_ds_bundle.js": "…"},
  "declared": [], "declared_unmatched": [],
  "observed_at": "2026-09-13T05:00:00Z",
  "targets": {"a1b2c3d4e5f6": {"role": "menuitem", "name": "배우자", "input_type": "", "owner": "…", "owner_items_hash": "…", "dom_path": "…", "kind": "menuitem", "first_seen_step": 7, "declared": false, "found_by": ["semantic", "react_props"], "live": false},
              "0f0f0f0f0f0f": {"role": "", "name": "", "input_type": "", "owner": "", "owner_items_hash": "…", "dom_path": "div:nth-of-type(3)", "kind": "overlay", "first_seen_step": 3, "declared": false, "found_by": ["structure"], "live": false, "scrim": true}},
  "initial": {"inventory": [{"id": "…", "enabled": true, "checked": null, "face": null, "value_empty": null, "surface": null, "occluded": false, "live": false}], "state_hash": "…", "surface_key": "…", "capture": {"path": "captures/…-initial.png", "sha256": "…"}},
  "steps": [{"n": 1, "path": ["…"], "target": "…", "action": "click", "option": null, "value": null, "context": "…", "status": "executed", "error": null,
             "before": {"inventory": [], "state_hash": "…"}, "after": {"inventory": [], "state_hash": "…", "surface_key": "…", "capture": {"path": "…", "sha256": "…"}},
             "changes": {"added": [], "removed": [], "values": [{"target": "…", "before": "", "after": "검증 입력"}]}, "navigated": null, "discovery": false}],
  "discovery_limits": [], "partial": false, "caps_hit": [], "environment_error": null
}
```

This block is the single source for the field set; `check_design_evidence.py`'s
exact-field check recurses into every nested object against exactly these
fields, including `targets` entries (`value` on a `select` option target,
`scrim` on an overlay target are the only two kind-specific optional fields)
and every `steps[]` row. `after.capture` exists only on `initial` and on a step
whose `changes.added` is nonempty; a `navigated` step (the document/URL changed)
has `after: null` and no capture, because its root no longer exists to crop.
`found_by` lists every detection channel that flagged a target — `semantic`,
`react_props`, `onclick`, `cdp_listener`, `cursor`, `structure`, `declared`.
`live` marks membership in a `role=status`/`aria-live` subtree: a live target
still carries full enumeration and execution obligations, it only drops out of
`state_hash` and `surface_key` inputs so animated status text cannot mint new
surfaces or scramble replay. An inventory entry's `checked` is
`true|false|"mixed"|null` — `"mixed"` is the `aria-checked="mixed"` tri-state
of a select-all header, and the residual counts it as one more observed toggle
state (one `click` unit with `option: "mixed"`), exactly as the snippet does.

`collector.snippet_sha256` and `collector.driver_sha256` must equal this
plugin's own `assets/interaction_audit.js` and `assets/observe_interactions.pw.js`
bytes; a mismatch is a defect no matter what the rest of the document says.
`root.selector` must be exactly `[data-screen-label="<label>"]` whenever
`screen-meta.json`'s `source_sha256` matches this case's entrypoint hash; any
other entrypoint (a multi-screen build's settings screen, an unlabeled
original) records its `--root` as a declared input instead, and the
independent reviewer audits it. The snippet already subtracts every element
matched by an `excluded_regions` declaration from `outside_root.count`, so the
recorded count is the number of outside-root targets no declaration closed:
`outside_root.count` greater than zero is a defect whether or not declarations
are present (fix the declaration and re-run). `content_crop.w`/`.h`
must equal the case `viewport` exactly; `browser_viewport` is the actual
browser window, which can be larger than the cropped root when an engine
canvas holds more than one screen.

`served` records the body bytes of same-origin 2xx responses, excluding
204/205 (no body); keys are paths relative to the entrypoint directory with
the query string ignored. Every key must resolve, through the archive
manifest's file list, to a byte-identical row; a served path escaping the
reference root, a served entrypoint whose bytes disagree with the frozen
entrypoint, or a percent-decoded URL basename that disagrees with the
entrypoint's own basename, are each a defect. External-origin and non-2xx
responses fall outside this comparison.

The residual unit is `(identity, action, option)`. Every unit observed active
in any recorded inventory needs at least one `status: "executed"` step;
`failed`, `unreachable`, and `unclickable` steps never close it. The pure
`interaction_residual` in `check_design_evidence.py` and the snippet's own pure
function compute this independently over the same fixture JSON and must agree
— it is the same computation the collector itself uses to decide what remains
in its queue.

A surface key identifies the set of active identities visible after a step,
independent of their face/checked/value/surface/`owner_items_hash` values, so
two menus that differ only in which sibling row is open still count as one
surface. Every step whose `changes.added` is nonempty introduces a surface, and
`check_design_evidence.py` requires either a case `reached_by` step that
reaches it or a `{surface, scope_ref, approval_quote}` exclusion row for it; a
`removed`-only step (a close, a pick), a value-only step, and a `navigated`
step carry no such obligation. Every archive case itself needs `reached_by:
{"interactions": "<path>", "step": n | "initial"}` naming this document; the
referenced step (or `initial`) must exist and be `executed`, and its
`after.capture.sha256` (or `initial.capture.sha256`) must equal the case's own
`reference_capture.sha256` — the frozen reference image is always driver-saved,
root-cropped bytes, never a hand-made screenshot.

`interaction_exclusions` in `design-input.json` — unit rows
`{target, action, option, scope_ref, approval_quote}` or surface rows
`{surface, scope_ref, approval_quote}` — are the only exemption from a
nonempty residual or an unlinked surface; there is no author-granted waiver
field. `approval_quote` must be at least 10 characters of literal,
whitespace/NFC-normalized scope text found in `scope.md`; `scope_ref` must
resolve to an existing anchor in it; and the combined row count cannot exceed
10% of the active target count across the build's interaction documents. On a
successful `prepare`/`inputs` run, `check_design_evidence.py` writes every
exclusion row, and a one-line notice for any interaction document that
finished `partial`, to stderr as human-facing notices — stdout carries only
the result JSON — so Coordinator can carry them into the G0 banner as a
first-class item, never a silent pass.

`evidence-ledger.json` — the unverified ledger — is the last door, and it is a
**whitelist**: the only findings it admits are the four the checker reaches
*after* computing everything (residual, the 10% exclusion cap, an unlinked new
surface, and a `partial`/`caps_hit` mismatch). Everything else is closed by
default, including «no interaction evidence yet» and a stale `coverage_review`
— observe first, regenerate the review. A deny-list was tried and rejected:
one short-circuit finding (`cases: nonempty list required`) stood in for an
entire subtree the checker never computed, so a single approved row opened
everything. Rows are written only by `ledger.py add`, which runs the checker
itself, takes the finding by index, and re-runs it afterwards to confirm that
finding actually disappeared. A row carries the approval quote (which must sit
inside an H2-or-deeper section of `scope.md`), that section's sha256, the
observation fingerprint, and the magnitude at approval time; it goes stale — and
the wall returns — when the section changes, the observation changes, or the
magnitude grows. Deleting the ledger does not buy passage: the findings block
again, because the record and the right of way are the same file. The checker
consults it where `validate_inputs` and `validate_visual` settle their issue
lists, so `backstop.py` — which calls `validate_inputs` in-process — passes
through the same door, and both digests plus `validate_visual` stay alive.

Manifest rows — in `design-input.json`'s own list and in archive/static source
manifests alike — reject every unrecognized field. Nothing marks a row as
carried forward from an older manifest: re-freezing rebuilds the manifest from
freshly collected bytes, so every row is verified against what was just fetched.

`archive_design.py` exits 0 or 1 only. `refreeze.py` has its own scheme
(0 done · 2 already in progress · 3 incomplete or rewound · 1 error) that
neither `check_design_evidence.py` nor `backstop.py` reads or gates on. See
`design-acquisition.md` for the re-freeze procedure.

## Limits

The static collection path (`freeze_design`) does not collect JavaScript
interaction state at all; this document and its checks apply only to archive
HTML/JSX entrypoints. A target reachable only through a reverse cascade — a
child control that precedes, in document order, the trigger that reveals it —
is not found by the driver's queue ordering; closing that gap is a declared-input
(`--declared`) and independent-reviewer responsibility, not a machine guarantee.
Hover discovery fires once per candidate identity and excludes item-kind
targets (`menuitem`, `option`, `radio`, `checkbox`, `switch`, `tab`); a
two-level menu that only opens by hovering one of those items is not found
this way. Cross-origin iframes and the off-DOM rows of a virtualized list are
not enumerated; `discovery_limits` and `declared_unmatched` surface the gap
when it exists, and the independent reviewer's audit is the remaining
discretionary channel. A `discovery_limits` row's `dom_path` is the
container's child path from the root, and `.` means the root element itself
is the scroll container (a long mobile screen whose root scrolls). Inside a same-origin iframe, an element that is a
target only because it carries a handler — not a semantic control — is not
detected through the CDP listener channel; and on a non-React engine without a
`--cdp` connection, handler detection falls back to the `onclick` attribute and
the cursor heuristic alone, so `collector.capabilities` should be read
alongside `discovery_limits` before trusting a clean residual. `state_hash`
cannot distinguish two states of the same `select`/combobox trigger whose
displayed face text is identical but whose underlying option list differs. An
empty-name container's identity depends on `dom_path`, which is fragile to
portal sibling reordering between runs. The scroll positions a page-by-page
sweep discovers targets at are not themselves recorded, so `--resume` cannot
guarantee reaching the same drifted scroll state again. A target sitting
behind a fixed header or footer surfaces as an `unclickable` residual, which
Coordinator closes only through an actual declaration or an approved
exception, never by assumption. A step whose only effect is a value change (a
toggle's resulting state, for instance) carries no surface-linking obligation.
Neither the provenance of a re-freeze staging folder nor the authenticity of
an `interactions.json` document itself is machine-provable; the collector-sha,
served-byte, root-fingerprint, and mtime records only make a transcript
cross-check possible, not a proof. Extending the static-manifest closure rule
so that any closure containing a script-kind dependency also requires version
2 evidence is recorded only as a future candidate here, not adopted.
Interaction evidence does not change the `motion-notes.md` format; citing a
specific interaction step number in a "measured" provenance row is a
recommendation, not an enforced field.

## `visual-evidence.json` version 1

```json
{
  "version": 1,
  "input_digest": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
  "implementation_digest": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
  "visual_check": {"path": "visual-check.md", "sha256": "1111111111111111111111111111111111111111111111111111111111111111"},
  "cases": [
    {
      "id": "login/default",
      "url": "http://127.0.0.1:8000/login/",
      "viewport": [1280, 720],
      "capture": {"path": "captures/login-implementation.png", "sha256": "2222222222222222222222222222222222222222222222222222222222222222"},
      "result": "pass",
      "media": [
        {
          "requirement_id": "hero-video",
          "response": {"path": "private/hero-response.json", "sha256": "3333333333333333333333333333333333333333333333333333333333333333"},
          "browser": {"path": "private/hero-browser.json", "sha256": "4444444444444444444444444444444444444444444444444444444444444444"}
        }
      ]
    }
  ]
}
```

The visual case set and viewport values must exactly match `design-input.json`;
each case needs a nonempty URL, valid capture, and `result: "pass"`. The
original and implementation captures may have identical bytes after a perfect
match, but they must not be the same file or hardlink. Independent creation is
confirmed from the browser trace by the final auditor.

The implementation digest covers every path and byte under `PROJECT/web`, plus
the declared `host_files`. It includes additions and reflects deletions. The
only exclusions are directories `__pycache__`, `.pytest_cache`, `.mypy_cache`,
`.ruff_cache`; files `*.pyc`, `*.pyo`, and `.DS_Store`. Directory symlinks under
`web/` are rejected; the checker does not traverse them. There is no caller
exclude option.

## Media observations

A media requirement has exactly `id`, `kind` (`image` or `video`),
`environment`, `endpoint`, `identity_pointer`, and `source_pointer`. Pointers
use RFC 6901 path form beginning with `/`, including `~0` for `~` and `~1` for
`/`. Array selectors are canonical nonnegative decimal tokens: `0` or a
nonzero digit followed by digits. Object keys retain literal token semantics.
Pointers must resolve in the response `body` to a nonempty identity and source URL.

Response evidence has exactly:

```json
{"observed_at":"2026-09-06T12:00:00Z","environment":"staging","endpoint":"/api/media/hero","status":200,"body":{"asset":{"id":"hero-42","src":"https://cdn.example/hero.mp4"}}}
```

Browser evidence for video has exactly:

```json
{"observed_at":"2026-09-06T12:00:01Z","current_src":"https://cdn.example/hero.mp4","status":206,"loaded":true,"playback_start":0.0,"playback_end":1.25}
```

For an image, omit `playback_start` and `playback_end`. Observation timestamps
are timezone-aware ISO 8601 strings. API and browser statuses must be 2xx, `loaded` must be
true, response source must equal `current_src`, and video playback values must
be finite numbers with end greater than start. Media observation rows must
match requirements exactly, without omissions, additions, or duplicate IDs.

Do not record request credentials or headers. Keep raw responses containing
sensitive signed URLs in local private evidence; do not commit them to a public
repository. These JSON checks establish correspondence, not the authenticity
of the browser/tool environment or the meaning of the media. HTTP failure,
identity/source mismatch, stopped playback, a seed, or a sample substitute
cannot support `pass`.
