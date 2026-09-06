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
check, and 2 means a defect or insufficient evidence. `--phase visual` always
rechecks inputs. `backstop.py --design-build` joins the visual phase to the
existing 26 checks; `--only` cannot disable it. Omitting `--design-build`
preserves the non-design invocation.

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
entrypoint path/hash must match a successful row in one listed manifest. Each
manifest must be version 1, `source_ready: true`, have a nonempty successful
file list and a valid entrypoint. The checker compares every recorded path,
size and hash with local bytes and rescans supported static dependencies. A
reference capture must be a valid image container. A valid original image may
be both entrypoint and reference capture.

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
