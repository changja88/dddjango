Slice implemented per the approved `design.md` file list. Report:

## Created / changed files (all inside `web/`)

**New (21) — exactly design.md §12 신규 목록**
1. `web/lab/__init__.py`
2. `web/lab/urls.py` (`app_name = "lab"`, 4 routes)
3. `web/lab/widget/.gitkeep`
4. `web/lab/ui_lab/__init__.py`
5. `web/lab/ui_lab/view/__init__.py`
6. `web/lab/ui_lab/view/ui_lab_view.py` (`ui_lab_view` + 3 fragment functions)
7. `web/lab/ui_lab/view/ui_lab.html`
8. `web/lab/ui_lab/view_model/__init__.py`
9. `web/lab/ui_lab/view_model/ui_lab_view_model.py` (`UiLabViewModel`)
10. `web/lab/ui_lab/state/__init__.py`
11. `web/lab/ui_lab/state/ui_lab_state.py` (5 frozen dataclasses)
12. `web/lab/ui_lab/section/ui_lab_panel.html`
13. `web/lab/ui_lab/section/ui_lab_password_field.html`
14. `web/lab/ui_lab/section/ui_lab_preview.html`
15. `web/lab/ui_lab/section/ui_lab_note.html`
16. `web/static/js/password_visibility.js`
17. `web/static/js/image_preview.js`
18. `web/static/css/ui_lab.css`
19. `web/static/htmx/ui_lab_panel_swap.html`
20. `web/static/htmx/ui_lab_preview_swap.html`
21. `web/static/htmx/ui_lab_note_swap.html`

**Modified (2)**
22. `web/urls.py` — `path("lab/", include("web.lab.urls"))`
23. `web/design_system/foundation/tokens.css` — added `--border-width-hairline: 1px` (design §8 sole new token)

Not created (per §12): `form/`, `client/**`, `motion.js`, components, tests, `base/base.html` edits, fonts/files. Nothing outside `web/` was touched; `__pycache__` artifacts removed.

## Checks actually executed

- `python -m py_compile` on all touched `.py` (state/VM/view/urls, both layers) — exit 0.
- `python manage.py check` — "System check identified no issues (0 silenced)", exit 0. Baseline was zero ⇒ **0 new issues**.
- Temporary in-process render (throwaway `/tmp` script, deleted; no permanent test file):
  - `/lab/ui-lab/` 200; `/lab/ui-lab/fragment/panel/` 200; `.../preview/` 200; `.../note/` 200.
  - Page scripts = exactly 3 external tags: `web/htmx/htmx.min.js` (defer, base), `web/js/password_visibility.js`, `web/js/image_preview.js` (defer). **All three fragment responses contain zero `<script>`** (I11 static side).
  - Regex scan for ` on*=`, `hx-on`, `js:` across all four responses: **0 matches**.
  - Revision markers `rev-<12 hex>` present and different on every request (page: 6 markers; panel fragment 3; preview 2; note 1) — server-generated per response.
  - DOM id contract rendered exactly: `ui-lab-panel-a/b`, `ui-lab-password-a/b(+-input)`, `ui-lab-preview-a/b(+-input)`, `ui-lab-note-a/b`.
  - Trigger placement/flags: page has `hx-target` `#ui-lab-preview-a`, `#ui-lab-note-a`, `#ui-lab-panel-b` only (panel A has no root trigger; panel B preview/note have none) — each trigger renders inside its own swap unit, so panel fragment carries its own panel trigger and preview fragment carries preview+note triggers (I7 repeatability precondition).
  - `<details>/<summary>` rendered once, no JS attached (S3/I10 markup side).
  - `hidden` attributes present on JS-dependent controls (toggle button, clear button, output img, error node).
- `manage.py findstatic` resolved all five assets (`web/css/ui_lab.css`, both `web/js/*.js`, `web/htmx/htmx.min.js`, `design_system/foundation/tokens.css`) to real files.
- `node --check` on both JS files — syntax OK (no linter/type-checker configured in this app; nothing else applicable to run).

## Not executed (explicitly)

- **No browser run.** I did not launch Playwright/any browser, took no screenshots, and make no claim about runtime behavior: I1–I9, I11 network-load counting, I12 console/pageerror are **unverified by me** and remain for the independent Coordinator harness. No screenshots exist to attach.
- Repeated real HTMX swap, object-URL create/revoke accounting, keyboard path, decode-failure injection, and instance isolation are implemented to the §7 mechanism but browser-unverified.

## Mechanism notes (as specified, not invented)

- Cleanup contract in `image_preview.js`: on `htmx:beforeCleanupElement`, revoke only when `detail.elt` is a preview root, contains preview roots, or is/contains `[data-image-preview-output]` of a living owner — a note-node removal triggers no revoke (I8). Idempotent.
- Freshness guard: late `load`/`error` (capture-phase document listeners) apply only when the output's `src` equals the root's current object URL **and** its `data-image-preview-generation` equals the root's current generation.
- Strings written via `textContent` only; server strings reach JS solely through escaped `data-*` attributes (toggle labels) or server-rendered text nodes (empty/error messages).

## Blockers

None. No spec/houserule conflict found, no out-of-slice or out-of-`web/` change needed, no dependency added, and no design.md edit made.