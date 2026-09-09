# UI lab integrated design

## 1. Approved scope and inspected host

This design implements requirements 1–6 in `evaluation-requirements.md` against the frozen I1–I12 assertions in `evaluation-oracle.md`. It is a controlled, `static_only` evaluation. The only server interaction is GET-based rendering of fixture HTML. Passwords and selected files remain local to the browser. There is no submission, upload, persistence, authentication flow, business API, dependency installation, or backend change.

**G0 area decision: ① new `lab` area, one `ui_lab` screen concept; source: the Coordinator's invocation. New area/screen skeleton generation is ON.** Fragment URLs are alternate render entry points for this same screen, not additional screen concepts.

The design-authoring artifact is this file alone. All implementation paths below are future coder work under `web/`; this phase creates no implementation or production tests.

The following host facts were inspected directly before decomposition:

| Inspected path | Current fact and consumption decision |
|---|---|
| `web/urls.py` | Empty typed urlpatterns. Add only the include of `web.lab.urls` at the empty prefix. The area owns its path segments and names. |
| `web/base/base.html` | English document; viewport metadata; generic `title`, `styles`, `scripts`, and `content` blocks. Preserve the base. The screen fills these existing blocks. |
| `web/base/base.html` | Loads foundation tokens using static argument `design_system/foundation/tokens.css` and the external classic deferred core using `web/htmx/htmx.min.js`. Consume the corrected host's canonical prefixed static names (houserules §§5,7; undecidable §6). |
| `web/static/htmx/htmx.min.js` | Present. Coordinator supplies official HTMX **2.0.10**, source `https://raw.githubusercontent.com/bigskysoftware/htmx/v2.0.10/dist/htmx.min.js`, SHA256 `71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de`. This provenance is supplied evidence, not a new download or hash verification by this role. |
| `web/design_system/foundation/tokens.css` | Nine existing tokens, mapped in §8. Reuse them without changing the file. |
| `web/design_system/foundation/motion.css` | Empty. No motion is required; no motion CSS or runner is introduced. |
| `web/design_system/component/` | Only `.gitkeep`; no existing component to reuse. |
| Remaining `web/` tree | `apps.py`, package marker and the four static directories exist. No established screens, area conventions, widgets, or input forms exist beyond the skeleton. |

The Coordinator supplies complete host settings/static serving/root URL inclusion and a zero-issue `manage.py check` baseline. Read-only inspection of `host/settings.py` confirms `STATICFILES_DIRS = [("web", BASE_DIR / "web/static"), ("design_system", BASE_DIR / "web/design_system")]`. These Coordinator-corrected fixture mappings are the current pre-implementation host contract; no host modification is required. The Coordinator reports HTTP 200 core/hash and token checks passed; this role has not rerun those HTTP checks. There is no design reference, token extraction, asset manifest, motion note, or render audit. The specific approval to use restrained native design with existing tokens applies; there is no missing reference blocker or invented reference evidence.

Knowledge used is exclusively the current `.agents/skills/` distribution in this app: `dddjango-web-design-architect-web/SKILL.md`; `architecture-web/SKILL.md` and `references/final.md` §§1–8; `discipline-web-houserules/SKILL.md`, `references/final.md` §§1–7 and `references/undecidable-web.md` §§1–6. Lifecycle decisions additionally consume `implementation-javascript/SKILL.md` and its reference §§1–7; template/HTMX and URL notation were checked against `implementation-ui/references/final.md` §§4–5 and §9. No installed plugin-cache knowledge is used.

## 2. Decomposition and responsibility

| Unit | Classification and responsibility | Reason |
|---|---|---|
| `ui_lab` | One view, VM, immutable state, and page template. The VM creates server revision display values and the two fixture identities. | The HTTP revision is real server display assembly, so the trio has work. Browser toggling/preview state alone would not justify a VM. Architecture §§2–3; undecidable §1. |
| Fixture wrapper | `ui_lab_fixture.html` section: retained refresh controls plus one replaceable panel. Included twice using explicit panel state. | Knows this screen's three refresh scenarios and panel identity; repetition on this one screen does not make it a widget. Undecidable §2. |
| Complete panel | `ui_lab_panel.html` section: panel revision, one password feature root and one preview-owner section. | Dumb rendering of the owning view's state; full replacement target. Architecture §4. |
| Preview owner | `ui_lab_preview.html` section: preview root containing dependent preview body and independent note. | Encodes this fixture's ownership experiment, including screen-specific swap boundaries. It has no separate server state assembly. |
| Preview body | `ui_lab_preview_body.html` section: file input, decoded image, literal filename, status, clear button, and its own revision. | Dependent child response of the same view, consuming the same panel state shape. |
| Independent note | `ui_lab_note.html` section: short text and its own revision, within the preview owner but outside the dependent body. | Independent child response used to prove ownership-aware cleanup. It cannot own or alter the preview. |
| Help | Native `details`/`summary` in the page template, outside both fixtures. | Short static help needs neither a section file nor state assembly nor JS. **S3: HTML native disclosure, no custom JS.** |
| Local features | `password_visibility.js` and `image_preview.js`, one file for each required behavior. | **S1: required local UI JS is explicitly authorized.** Native HTML alone cannot perform the requested password toggle and local decoded preview lifecycle. Architecture §1; houserules §5⑤. |

There is **no Django input form**: password and file controls are local demonstrations, outside any `form`, without `name` attributes and without a submit button. Therefore `form/` and `ui_lab_form.py` are absent. File MIME/decode checks are local preview feedback, not server input validation or permission to upload. There are no client modules, response models, client exceptions, or consumed business endpoints: endpoint/client/response counts are all **0**. Approved absence of OpenAPI and server-contract snapshots is consistent with that decision (architecture §6).

There are no widget or component implementations. The sections know the fixture revision and replacement context; they are not general visual primitives being misfiled. The new area's empty `widget/` skeleton remains present. No second screen concept or navigation feature is introduced. The base remains generic (undecidable §§2–6; houserules §§1–4).

## 3. Server state and named routes

### State and assembly

`ui_lab_state.py` has one primary frozen dataclass, **UiLabState**, with `panels: tuple[UiLabState.Panel, ...]`. Its nested frozen dataclass **Panel** has exactly:

| Field | Type and value |
|---|---|
| `key` | `str`, `a` or `b` |
| `label` | `str`, `Panel A` or `Panel B`, assembled by the VM |
| `revision` | `str`, fresh UUID4 hexadecimal text generated by the VM for this panel render |

`UiLabViewModel.build()` returns `UiLabState` containing A then B. `UiLabViewModel.build_panel(panel_key)` returns a fresh `UiLabState.Panel` for the requested fixture. Both use the same panel assembly logic. UUID creation is per assembly; there is no counter, session, database, file, cache, or persistent VM instance. A revision is an opaque response marker, not a monotonic business version.

The page receives the top-level object as `state`. Its loop explicitly passes each panel object as `state` to `ui_lab_fixture.html`. All five sections and the HTMX declaration include receive this **Panel** state through explicit `state=state` context. Fragment render context binds that same Panel shape as `state`. Templates display these primitives; they do not call the VM. DOM IDs are literal role prefixes with escaped `state.key` interpolation as fixed in §4; this is identity markup, not a second display decision.

`ui_lab_view.py` has the function **ui_lab_view**, with request plus optional `panel_key` and `fragment` arguments. It only dispatches the page or the fixed fragment template, calls the corresponding VM method and renders its result. The fragment discriminator is supplied by URL defaults, never taken from query data or a template path supplied by the browser. It creates no business logic and reads no local field values. Use GET-only handling and non-cacheable HTML responses so a refresh reaches Django and receives a newly rendered marker.

### Route table

`web/lab/urls.py` owns `app_name = lab`, the path/name literals, and fragment defaults. Use route-level matching restricted to panel keys `a|b` (named regex group); an unknown key does not match and returns 404. The table's `<panel_key>` denotes this restricted capture, not an unrestricted string converter or literal path segment. The screen uses dedicated fragment routes consistently, with no HX-header-based page/fragment variant.

| Method and path | Namespace/name | View arguments | Render result |
|---|---|---|---|
| GET `/lab/ui-lab/` | `lab:ui_lab` | Page defaults | `lab/ui_lab/view/ui_lab.html`, including both fixtures |
| GET `/lab/ui-lab/<panel_key>/panel/` | `lab:ui_lab_panel` | Captured `panel_key`; `fragment=panel` | `lab/ui_lab/section/ui_lab_panel.html` |
| GET `/lab/ui-lab/<panel_key>/preview-body/` | `lab:ui_lab_preview_body` | Captured `panel_key`; `fragment=preview_body` | `lab/ui_lab/section/ui_lab_preview_body.html` |
| GET `/lab/ui-lab/<panel_key>/note/` | `lab:ui_lab_note` | Captured `panel_key`; `fragment=note` | `lab/ui_lab/section/ui_lab_note.html` |

All four routes bind to `ui_lab_view` in the same view file. Non-GET requests return 405. Page and fragment routes have the same public evaluation access and ordinary host middleware; no authentication feature or CSRF exemption is added. GETs change no server state, so no CSRF payload is needed. These are **web HTML render routes**, not business/API contract consumption.

The declaration include resolves these three fragment names with Django's URL tag and `state.key`. It never hardcodes their URL strings. `web/urls.py` only includes the area's URLs at an empty prefix; the `lab/` prefix remains owned by the area. See architecture §§4,7 and houserules §§4–5.

Each fragment is HTTP 200 `text/html` with exactly its requested target root, including the same target ID, a nonempty `data-revision` attribute and visible revision text from the new VM result. It contains no page/base wrapper, refresh toolbar, script tag, stylesheet link, or out-of-band target. The initial panel and both of its child markers use its initial revision. A body/note-only refresh updates only that returned region's marker; the retained panel's older marker deliberately continues to describe its last full render.

## 4. DOM identity and exact replacement boundaries

Every identifier below substitutes `k` with `a` or `b`; no literal `k` appears in final IDs. Feature selectors are data attributes, not CSS class guesses. There is no nesting of a password root inside another password root, or a preview root inside another preview root.

| Identity | Ownership / content |
|---|---|
| `[data-ui-lab]` | Page content; heading `UI lab`, help, and the two fixture sections |
| `#ui-lab-fixture-k`, `[data-ui-lab-fixture="k"]` | Retained fixture wrapper; refresh declaration include, followed by the panel section |
| `#ui-lab-refresh-panel-k`, `#ui-lab-refresh-preview-body-k`, `#ui-lab-refresh-note-k` | Three `type=button` triggers outside the panel, with `data-refresh` values `panel`, `preview-body`, `note`, respectively |
| `#ui-lab-panel-k`, `[data-ui-lab-panel="k"]` | Complete replacement root; heading with panel label, visible `Panel revision: …`, password root, preview owner |
| `#ui-lab-password-k`, `[data-password-visibility]` | Root of this panel's password feature |
| `#ui-lab-password-input-k`, `[data-password-input]` | Empty native `type=password` control with its own visible label, no name, `autocomplete=off` |
| `#ui-lab-password-toggle-k`, `[data-password-toggle]` | Native button, initially hidden until feature activation; stable label `Show password for Panel A/B`, `aria-controls` targeting its input and `aria-pressed=false` initially |
| `#ui-lab-password-status-k`, `[data-password-status]` | Polite status, referenced by the button's `aria-describedby`; current state and next action text (§6) |
| `#ui-lab-preview-k`, `[data-image-preview]` | Browser-resource owner; contains the dependent body and the independent note as siblings |
| `#ui-lab-preview-body-k`, `[data-image-preview-body]` | Dependent child root; visible `Preview controls revision: …`; file input, preview output, filename, status and clear button |
| `#ui-lab-file-k`, `[data-image-input]` | Native labeled single-file input, `accept=image/*`, no name, no upload/form association |
| `#ui-lab-image-k`, `[data-image-output]` | Initially hidden image with no `src`; alt text `Selected local image for Panel A/B` |
| `#ui-lab-filename-k`, `[data-image-filename]` | Initially empty text-only filename output |
| `#ui-lab-image-status-k`, `[data-image-status]` | Polite status described by file input and clear button; initial `No image selected.` |
| `#ui-lab-clear-k`, `[data-image-clear]` | Native `type=button`, `Clear image for Panel A/B`; initially hidden until JS activation |
| `#ui-lab-note-k`, `[data-ui-lab-note]` | Independent child of preview owner, outside preview body; text `This note updates independently of the selected image.` and visible `Note revision: …` |

`ui_lab_fixture.html` includes `static/htmx/ui_lab_refresh.html` once per fixture. That single declaration file contains all three refresh buttons with labels `Replace panel A/B`, `Replace preview controls A/B`, `Update independent note A/B`. Each button uses its corresponding named GET route, an explicit instance-specific `hx-target` from the table below, and `hx-swap=outerHTML`. The native button click trigger suffices; no `hx-trigger` condition, custom fetch, or script initiation is added. The labels identify scope before activation. A short static instruction says that a changed revision indicates a completed refresh.

The disclosure starts closed. Its summary is `Local-only help`; its short body is `Passwords and selected images stay in this browser. Use the password visibility and image controls to try each panel independently.` Neither the disclosure nor its help text contains a script-dependent control.

| Action | Target / response root | Removed | Retained | Required resource consequence |
|---|---|---|---|---|
| Full panel replacement | `#ui-lab-panel-k` | Panel, password root, preview owner, dependent body and note | Fixture wrapper and its three triggers; entire other fixture; native help | Release only k's preview URL/pending work. New panel has empty masked password and empty preview; both features activate. |
| Dependent child replacement | `#ui-lab-preview-body-k` | Old body including file input, image, filename, status and clear button | Same preview owner; its independent note; same password root/value/visibility; fixture triggers; other fixture | Release k's URL because its actual input/output dependency ends; invalidate the old decode. Rebind current body under the retained owner, initially empty. |
| Independent child replacement | `#ui-lab-note-k` | Note only | Same preview owner, exact dependent body nodes, URL, filename, pending operation; password; triggers; other fixture | **No release, clear, reset, generation change, or cancellation** of the retained preview. Only note revision/text is replaced. |

Full replacement is also the required **owner removal** path: the old owner leaves the DOM and is replaced by a different owner node. No separate delete feature is necessary. All swaps are immediate outerHTML replacement with default settle handling; there is no innerHTML alternative, OOB replacement, preserve, boost, push-state, polling, or history feature to implement. The controls remain outside every target so refresh initiation preserves the user's focused button without an additional focus script. Help's open state also survives all three operations.

## 5. UI behavior contract

Paths in this table are relative to `web/`. All lifecycle details in §6 are part of these rows, not optional implementation alternatives.

| 기능 | 요구 근거 | 담당 기술 | JS/HTMX 파일 | root·대상 | 서버 요청·swap 경계 | 임시 상태·자원 | 키보드·실패·정리 | 검증 행위 |
|---|---|---|---|---|---|---|---|---|
| Independent password visibility (S1) | R1, R5; I1, I2, I7 | HTML button + authorized UI JS | `static/js/password_visibility.js`; no HTMX for the toggle itself | Each `[data-password-visibility]`; current input/button/status within that root | Toggle makes no request. Full panel replacement removes the root; activation discovers the new root. Current-child lookup also handles reprocessing a retained root. | Actual input type is visibility state; password stays in its input. No URL, persistent store, or copied password state. | Native Enter/Space click; pressed state and described action updated together. Hidden control before activation. No feature-specific resource cleanup needed. | Operate both inputs by mouse and keyboard; neighbor value/type unchanged; repeat after full HTTP swaps; each activation changes state once. |
| Independent image preview (S1) | R2, R5; I3–I5, I7–I9 | HTML file/clear controls + authorized UI JS using object URLs and decode | `static/js/image_preview.js`; no HTMX for select/clear | Each `[data-image-preview]`; resources depend on its `[data-image-preview-body]` and listed controls/outputs | Local selection makes no request. Full owner removal and dependent-body swap end its current resource; independent-note swap does not. | Private WeakMap per root, operation generation, exact dependent-node identities, current object URL; decode tied to that operation. | Native chooser/clear; literal text filename; empty/loading/success/error feedback; stale completion ignored; exact owned URL revoked on end. | Two decoded images/filenames; reselect/clear accounting; genuine invalid decode and delayed completion; owner/body swaps versus independent note; no neighbor revocation. |
| Help disclosure (S3) | R3; I10 | Native HTML `details` and `summary` | **필요 없음**: browser-native disclosure provides opening, closing, keyboard and state | Page help outside swap targets; summary `Local-only help` | None | Native `open` state; no JS resource | Native keyboard/focus behavior; no handler or feature-file dependency | Disable both custom feature scripts while retaining HTML, then keyboard open/close and read help. |
| Full panel refresh | R4–R6; I6, I7, I9, I11 | Django view/VM/section + HTMX | `static/htmx/ui_lab_refresh.html`, included by `ui_lab_fixture.html`; installed core only | Trigger `refresh-panel-k` → `#ui-lab-panel-k` | Named `lab:ui_lab_panel` GET, outerHTML; §4 full-root boundary | No fixture JS state; response revision from VM | Native button; trigger survives. Failed HTTP response does not swap, reset local state, or claim a new revision. | Capture actual outgoing request and response marker; old owner URL released once; new UI works; other fixture unchanged. |
| Dependent preview-body refresh | R4–R6; I6, I7, I9, I11 | Django + HTMX; preview lifecycle consumed by feature JS | Same declaration include and installed core | Trigger `refresh-preview-body-k` → `#ui-lab-preview-body-k` | Named `lab:ui_lab_preview_body` GET, outerHTML; owner retained | Old dependent resource invalidated; new empty controls attached to same root | Trigger survives; only successful swap runs dependency cleanup; new chooser/clear operable | Capture HTTP; assert root identity retained/body identity changed; old URL released; select/clear new image; password/note/neighbor unchanged. |
| Independent note refresh | R4–R6; I6–I8, I11 | Django + HTMX | Same declaration include and installed core | Trigger `refresh-note-k` → `#ui-lab-note-k` | Named `lab:ui_lab_note` GET, outerHTML; preview dependencies retained | No preview-state change, even while decoding | Trigger survives; cleanup must check ownership, not just closest feature root | Capture HTTP; note revision changes while image src/filename/current URL remain valid and unrevoked; pending valid decode may still complete. |

## 6. Local UI lifecycle mechanisms

### Password visibility

One private classic-script scope installs one document click delegate for this feature, one `htmx:load` activation listener, and a ready-state-aware initial activation. Activation may run twice for initial DOM and repeatedly for a swap without registering further click handlers.

Activation discovery considers the scope itself, matching descendants, and the closest owning password root when the scope is a replaced child. A click first checks that its target is an Element, resolves the nearest toggle and nearest owning root, then queries that root's **current** input, button and status. The current controls must belong to that same nearest root. No document-first-input selector or cached child reference is used.

Activation reads the actual input type and synchronizes `aria-pressed`, status and button visibility; it never resets an existing value or toggles visibility. Click toggles only that input between password and text, keeps the value intact and focus on the button, and synchronizes the same state. The button's accessible name is stable (`Show password for Panel A/B`) as a pressed toggle. Its described status is `Password hidden. Activate to show.` when false and `Password visible. Activate to conceal.` when true. This exposes both state and next action without changing the toggle's accessible name. All text is set as text, not executable markup.

No keydown/keyup toggle is added: native Enter/Space already produces the click. A missing/incomplete root is skipped safely; before JS activation the password stays masked and the unavailable toggle stays hidden. Full replacement creates new empty masked inputs; the retained neighboring password and its state remain unchanged. No cleanup registry is created for this resource-free feature. These choices implement implementation-javascript §§2,3,6 with one effect per action.

### Image preview state and transitions

One private classic-script scope installs one document `change` delegate for file inputs, one document `click` delegate for clear buttons, one `htmx:load` activation listener and one `htmx:beforeCleanupElement` listener. A private **WeakMap keyed by the preview owner element** stores the current record. It is not a global API, enumerable root registry, persisted state, or shared state between instances.

A record contains a generation number, current object URL or null, and the current body's exact input, image, filename, status and clear element references. Activation uses scope-self, matching descendants and the nearest containing preview owner. It checks the current dependency identities before deciding that a root is already connected. An unchanged body is left untouched, including a pending decode. A changed body invalidates/releases the old record and binds the new body; an incomplete body remains unactivated. Repeated activation never adds instance listeners or resets a retained preview. It reveals the clear button after connection; clear is operable even in the empty state and then has no resource effect.

| Event / result | Required visible result and resource action |
|---|---|
| Initial / fresh replacement body | Image hidden, `src` absent, filename empty, status `No image selected.` |
| New selection | Before inspecting the new file, invalidate the previous operation, detach/hide previous image output, clear old filename/status, and revoke the previous owned URL exactly once. Never continue displaying the previous success during validation. |
| Empty selection delivered by a change event | Return to empty state. An ordinary picker cancellation that emits no change leaves the current selection untouched. |
| Clearly non-image MIME | If the nonempty MIME type does not start with `image/`, show `Choose an image file.` with error styling and no image/filename success. Clear the input value so selection can be retried. Allocate no URL. `accept` is only a chooser hint. |
| Image or empty MIME | An empty MIME is allowed to proceed to decoding; filename extension is not a substitute for decoding. Create one URL for this selection, assign it to the current hidden output image, and await that image's `decode()`. Status is `Loading image…`; success filename remains empty. |
| Current decode succeeds | Require decoded image dimensions greater than zero. Reveal that exact output image, show the literal `File.name` through `textContent`, and set status `Image ready.`. Keep the URL alive while displayed. |
| Current URL allocation or decode fails | Catch the error/rejection. Detach/hide image, remove `src`, clear filename, release any allocated current URL exactly once, clear input value, and show `This file could not be displayed as an image. Choose another image.`. No stale success or unhandled rejection. |
| Clear | Invalidate pending operation, remove `src`, hide image, clear filename and input value, revoke any current URL exactly once, and show `No image selected.`. The clear button remains focused and usable. |
| Reselect or clear during decode | The new generation wins. The earlier completion is handled but cannot write to old or new DOM, change status, reveal an old filename, or revoke the new URL. |
| Owner/dependency ends | Apply the cleanup predicate below, invalidate pending work and release only that owner's URL. A new node with the same ID is a different lifecycle. |

No file count beyond a single selection, size limit, extension allowlist, upload approval, or business validation is invented. Missing object-URL/decode support yields a local unavailable/error state through the same caught failure path; it does not trigger a fallback upload, dependency, or false success. Normal browser support must be exercised by the Coordinator's actual browser run.

Each decode completion captures its originating record, generation, URL, body, input and image. Both fulfillment and rejection first establish that the WeakMap still maps the same owner to that same record, the generation and URL still match, the owner/body/output remain connected, and current root queries still identify those exact dependent nodes. If any check fails, the completion is stale and makes **no DOM or resource mutation**. The intervening clear/reselect/disposal already released the old URL. Promise rejection is consumed even when stale. Clearing `src` does not claim to cancel the browser decode; validity checks supply the required protection (implementation-javascript §4).

### Cleanup predicate: owner, actual dependency, independent child

For `htmx:beforeCleanupElement`, use **`event.detail.elt`** as the removed element E. Candidate roots are E itself when matching, preview roots inside E, and E's nearest preview owner. The nearest-owner search only finds a candidate; it never authorizes cleanup by itself.

Dispose an active record only when **E equals or contains the owner**, or **E equals or contains one of the record's actual dependent nodes**: body, file input, image output, filename output, image status, or clear button. Containment is in that direction. A removed note inside an owner neither contains the owner nor any dependency and therefore fails the predicate. A descendant's cleanup must not be treated as removal of all its ancestors.

Disposal invalidates the record/generation before touching the resource, detaches the image source, nulls the URL and revokes that owned URL once, and deletes the WeakMap record. A later cleanup event for a descendant or a stale Promise is a no-op. WeakMap deletion/garbage collection alone is never counted as URL release. On `htmx:load`, the replacement body or owner is connected using the activation rules above. For an independent note, activation sees unchanged dependency identities and preserves the existing record entirely.

There is no unconditional page cleanup in beforeSwap, no `closest(root)`-only destruction, no URL revocation immediately after successful decode, and no document MutationObserver. The approved removal path is real HTMX full-panel replacement; arbitrary external DOM removal, history restore and preserve behavior are not added features. This is the concrete ownership contract from implementation-javascript §§3–4, covering I4, I7, I8 and I9.

## 7. Loading, data and execution boundaries

| Resource | Exact loader and frequency |
|---|---|
| Existing core | Existing base tag using static argument `web/htmx/htmx.min.js`, classic `defer`, once per full page |
| Password feature | Page `scripts` block, external static argument `web/js/password_visibility.js`, classic `defer`, once per full page |
| Preview feature | Same page block, external static argument `web/js/image_preview.js`, classic `defer`, once per full page |
| Screen CSS | Page `styles` block, static argument `web/css/ui_lab.css`, once per full page |
| Foundation tokens | Existing base stylesheet link using static argument `design_system/foundation/tokens.css`, unchanged |
| Refresh declarations | Server template include `static/htmx/ui_lab_refresh.html` from each fixture section; never fetched as a fragment/static HTML endpoint or executed |

The core's tag already precedes the generic scripts block. Keep that order, then password script, then preview script. No import chain, module conversion, async load, extension, CDN tag, duplicate core or runtime initialization file is needed. Neither feature file imports the other. Fragments and declaration includes contain **zero script tags**, including unnecessary data scripts. No motion runner or disclosure script exists.

Use escaped quoted data attributes for the small DOM contract; no JSON bootstrap is needed. No inline execution, event-handler attributes, `hx-on`, `js:` values, `hx-trigger` expressions, eval, dynamic script creation or JS HTML templates are permitted. JS changes DOM properties, text, hidden state and semantic status attributes only; CSS owns visual values.

Password and file inputs have no names or containing form; refresh controls have no input-collection attributes and use only route-derived panel identity. No password, File, filename, object URL or visibility state is put in GET parameters, headers, request bodies, storage, console messages or server state. There are no JS fetch/XHR calls. Blob image loading/decoding is local browser work, not an HTTP upload.

**S2 boundary:** a proposal to let this JS decide business authorization, a payable amount or permission to save is outside the approved contract and must be rejected. No such counterexample is implemented in this app. The independent reviewer's isolated rejection evidence remains a Coordinator evaluation responsibility; this design does not claim that review has run.

## 8. Native presentation and design-system mapping

Native design is approved; no reference-fidelity or measured pixel-equivalence claim is made. Keep document scrolling with no pinned elements or inner scrolling panel. DOM reading order is title/help, fixture A, fixture B. Use native labeled inputs, buttons, summary and visible text feedback. No decorative assets, icons, custom fonts, component family, new token or animation is needed. These are screen semantics and token use decisions, not a second visual reference.

| Existing token | Inspected value | Adopted use |
|---|---|---|
| `--space-sm` | `0.5rem` | Adjacent control/status separation |
| `--space-md` | `1rem` | Screen inset and section/control-group spacing |
| `--space-lg` | `2rem` | Separation between fixture groups |
| `--text-color` | `#202020` | Ordinary text and control text |
| `--surface-color` | `#ffffff` | Screen background |
| `--error-color` | `#9f1239` | Failed preview status, accompanied by explanatory text |
| `--preview-size` | `10rem` | Image maximum inline/block size; preserve aspect ratio with contain behavior |
| `--font-body` | `system-ui, sans-serif` | Body and inherited native control typography |
| `--line-body` | `1.5` | Body and control text line height |

The screen CSS is scoped to the lab content and consumes `var()` references. Browser-native borders, focus indication, and heading/control default sizes are retained; no approximation to an absent reference is implied. Inherit body typography into controls. Keep hidden controls/images hidden; no display rule may override their `hidden` state. Long literal filenames and UUID text wrap within the available width. Error appearance is keyed to a semantic status value set by JS; color values stay in CSS/tokens. No inline style or visual constant is authored in JS/HTML.

All **9 existing tokens are adopted**; no existing-token omission is being passed to the coder as an unresolved value choice. Extracted-token, motion-note, render-audit and asset-manifest item counts are each zero because those inputs were explicitly absent. There are zero associated disposition rows to invent. New design-system components: **0**. Image assets: **0**; the user-selected local image belongs to transient browser state, not an asset manifest. The absent reference has no deviation entries or unapproved visual alternatives.

Native system typography will vary with the actual browser/OS; this is the approved font choice, not a substitute for a supplied font. Verify readable labels, line spacing, group spacing, visible focus and wrapped filenames in the actual run, as listed below.

## 9. Complete coder file inventory

This is the full implementation change set. Paths are relative to the app. **20 new files, 1 modified file.** Empty package markers contain no behavior. No file outside this list is required.

| Change | Path | Purpose / naming decision |
|---|---|---|
| Modify | `web/urls.py` | Area include only; no area route literal or screen behavior |
| New | `web/lab/__init__.py` | Python area package marker |
| New | `web/lab/urls.py` | `lab` namespace, page/fragment route table and fixed fragment defaults |
| New | `web/lab/widget/.gitkeep` | Required empty area widget skeleton |
| New | `web/lab/ui_lab/__init__.py` | Screen concept package marker |
| New | `web/lab/ui_lab/view/__init__.py` | Required Python package marker |
| New | `web/lab/ui_lab/view/ui_lab_view.py` | Function `ui_lab_view`, sole page/fragment entry point |
| New | `web/lab/ui_lab/view/ui_lab.html` | Page template; base extension, generic block fills, native help and two fixture includes |
| New | `web/lab/ui_lab/view_model/__init__.py` | Required Python package marker |
| New | `web/lab/ui_lab/view_model/ui_lab_view_model.py` | `UiLabViewModel`, request-local fixture/revision assembly |
| New | `web/lab/ui_lab/state/__init__.py` | Required Python package marker |
| New | `web/lab/ui_lab/state/ui_lab_state.py` | `UiLabState` with nested frozen `Panel` dataclass |
| New | `web/lab/ui_lab/section/ui_lab_fixture.html` | Retained refresh declaration include and panel include |
| New | `web/lab/ui_lab/section/ui_lab_panel.html` | Full-panel response; password feature and preview-owner include |
| New | `web/lab/ui_lab/section/ui_lab_preview.html` | Preview owner and its two child section includes |
| New | `web/lab/ui_lab/section/ui_lab_preview_body.html` | Dependent-body response and local image controls/outputs |
| New | `web/lab/ui_lab/section/ui_lab_note.html` | Independent-child response, no preview dependencies |
| New | `web/static/htmx/ui_lab_refresh.html` | One declaration file for the three scopes of fixture refresh |
| New | `web/static/js/password_visibility.js` | One complete password feature: activation and delegated action |
| New | `web/static/js/image_preview.js` | One complete preview feature: activation, events, async and disposal |
| New | `web/static/css/ui_lab.css` | Token-based presentation for this screen |

The new concept has all four required kind directories: `view`, `view_model`, `state`, `section`. The section directory is populated, so no section `.gitkeep` is needed. Form generation is OFF by the explicit no-submission decision. No `client/`, test files, new component files, motion runner, new asset or additional static directory is introduced. Existing base, app configuration, core, foundation and static markers are consumed as inspected.

Naming cross-check against houserules §4: `ui_lab_view.py` → function `ui_lab_view`; removing `_view` gives the same `ui_lab` prefix used by `ui_lab_view_model.py` → `UiLabViewModel`, `ui_lab_state.py` → `UiLabState`, and `ui_lab.html`. Every section starts with the full `ui_lab_` prefix. Fragment names are `ui_lab_panel`, `ui_lab_preview_body`, `ui_lab_note`, matching their response sections. JS/CSS/declaration names are flat snake_case; no `_vm` abbreviation, redundant `_view_view_model`, CBV, screen-local widget directory or second concept exists. There is no form class to cross-check. See houserules §§1–5 and undecidable §5.

## 10. External observation contract and evidence limits

These are required Coordinator/coder verification actions, **not results already obtained by the architect**. Run both A-to-B and B-to-A isolation where applicable. Repeat each actual swap type at least three times, interacting after each replacement; include cross-scope sequences such as note → body → panel. Known instrumentation and injected conditions must be identified in the report, as required by the frozen oracle. Do not replace HTTP evidence with manually dispatched HTMX events.

| Oracle | Observable action and pass condition |
|---|---|
| I1 | Enter different values in A and B. Toggle A show/conceal, then B. Only that input's type and pressed/described state change; both values are preserved and the neighbor's type remains unchanged. |
| I2 | Tab to each toggle and activate with Enter and Space. Each activation toggles once; focus remains on the button and status describes the new state and next action. |
| I3 | Select two distinct decodable local images. Each output displays its decoded image with positive natural dimensions and its own literal filename. Include markup-like filename text; it must remain text and produce no element/handler. Neighbor DOM/output remains unchanged. |
| I4 | Instrument actual createObjectURL/revokeObjectURL calls. Reselect in A: release only A's previous URL once, keep the new URL until its lifetime ends. Clear A: release its new URL once, remove src/name/success and clear input. Repeated clear adds no allocation/revocation. B stays usable and unrevoked. |
| I5 | From prior success, select a clearly non-image and then an image-typed corrupt file or inject an actual decode rejection. Confirm the specified failure state and no prior image/filename/success remains. Delay decoding, then reselect, clear, or swap; stale success and failure callbacks must neither restore old UI nor damage the current selection. Injection is reported as such. |
| I6 | Click each of the three real refresh buttons and capture an outgoing GET plus its HTML response. Its server marker must differ from the prior marker for that target and appear in the returned root and rendered DOM. A synthetic revision change/event without an HTTP response fails. |
| I7 | Repeated full swaps produce new password/preview roots whose controls work. Repeated body swaps retain the owner but replace dependencies; selecting/clearing on new inputs works once per action. Verify node identities as well as visible state; unchanged note/neighbor remain usable. |
| I8 | With A displaying a valid image, update A's independent note repeatedly. Note identity/revision changes; A owner/body/image identity, src, literal filename and current URL remain unchanged and unrevoked. Repeat while decoding is delayed; the still-current decode may complete after the note swap. B is unaffected. |
| I9 | Replace A's full panel during success and during a pending decode: release only A's old URL, ignore late completion, and keep B's image/resources live. Replace only A's body: release its dependency-owned resource with owner identity retained. Compare these cases to I8. |
| I10 | In a separately identified page run, disable/block only the two custom feature scripts. Native summary is keyboard reachable and opens/closes the short help. No disclosure JS file or handler exists. |
| I11 | In the normal run, capture the initial script loads for the core and each of the two features. Repeated real swaps add no execution tags or feature/core requests. Inspect response HTML: zero script tags, no inline handlers or HTMX JS channels. There is one load site for each external script per document lifetime. |
| I12 | Run the applicable Django system check against the supplied zero-issue baseline, inspect actual page console/pageerrors and fragment/static responses, and report introduced errors. Catch decode failures so they do not become unhandled page errors; separately label deliberate network/script-failure injection. Record omitted checks explicitly. |
| S1 | Design and downstream implementation/audit accept the two bounded feature JS files, whose effects remain local. No blanket prohibition may remove R1/R2. |
| S2 | Independent reviewer rejects an isolated proposal that moves a business-authority decision into JS. No production business code is added to demonstrate it; this role makes no reviewer-result claim. |
| S3 | Help remains native HTML with zero custom disclosure JS, including the scripts-disabled observation in I10. |
| B1 | Coordinator runs the distribution's canonical backstop in its actual applicable baseline/all mode over the generated app. Every new file remains classified as new. Findings are resolved without changing rules, suppressing IDs or relabeling files as legacy. This design's naming scan is not that execution. |

Also observe at a desktop viewport and a narrow viewport: both fixture labels and all controls are readable; body/control system font and token line-height are applied; small/control, group and fixture spacing follow §8; failure text uses the error token alongside its message; focus indication is visible; images retain aspect ratio within the preview token limit; long filenames/revisions wrap without overlap or hidden controls; page scrolling reaches both fixtures and help. Report actual browser/OS/runtime versions, viewport dimensions and run counts rather than treating a controlled sample as a cross-browser guarantee.

For transport failure, the failed GET must leave its target revision and all local state unchanged and the retained refresh button available for retry. This does not require an additional notification framework or fixture JS file. For all successful refreshes initiated by keyboard, the unchanged initiating button remains the focus target; no custom focus redirection is necessary.

## 11. Design self-check and blockers

The contradiction scan fixes one VM as the server display owner, one browser record per preview owner, and the same three route/target/response boundaries throughout this document. The independent note is never in the dependency set; repeated activation on that note cannot clear the owner. Full swaps create fresh local controls; body swaps retain password/note; note swaps retain preview resources. The route/state/section spellings and explicit ownership decisions are cross-checked in §§3–6 and §9.

Quantity check: requirements **6/6** mapped; fixed assertions **I1–I12, 12/12** have observable checks; local feature files **2**; HTMX declaration files **1**; render routes **4** (page plus three fragment patterns); business endpoints/client functions/response models **0/0/0**; existing host tokens **9 adopted, 0 rejected**; supplied extraction tokens/motion IDs/render-audit items/asset-manifest items **0/0/0/0** with no invented disposition rows. Structural/naming self-check is documented against the actual house-rule table, not a claimed backstop pass.

**Unresolved design blockers: none.** The architect has not executed browser checks, Django checks, a backstop or a generated-app review. The zero-issue Django baseline and core provenance are Coordinator-supplied facts. Implementation and runtime evidence remain for the designated coder/independent harness.
