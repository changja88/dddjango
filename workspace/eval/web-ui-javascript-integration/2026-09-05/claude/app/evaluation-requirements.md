# Controlled UI integration evaluation requirements

This is an isolated temporary Django app used to evaluate the current dddjango-web distribution. It is not a requested production feature. The user authorized evaluation and its implementation. No OpenAPI/business API is consumed (static_only). There is no design reference; use a restrained native layout and existing host design tokens. No new dependencies, backend business code, storage, authentication flow, or submission feature. Area is `lab`; one screen concept is `ui_lab`.

Required observable behavior:

1. Two independently usable password fields. Each has a keyboard-operable control to show and conceal its own value. Its current state and action are accessible. Toggling one does not change the other. Values do not leave the browser.
2. Two independently usable local image previews. A valid local image selection shows that image and its literal filename. Selecting another image or clearing removes the old preview. A failed/invalid image has an understandable state without displaying stale success. No upload or persistence occurs.
3. Native disclosure containing short help text. It must be usable without custom JS.
4. Real HTMX requests to Django render replacement HTML for this screen. The controlled fixture must expose replacement of a complete UI panel and replacement of only a dependent child of a retained panel. Also expose an independent child update next to a retained preview, so the browser harness can distinguish child cleanup from owner cleanup. Responses contain a server-generated revision marker to prove an HTTP response was used. These routes return fixture UI HTML only and do not invent a business API.
5. After replacement, the new controls still work and a retained neighboring UI keeps its state. Repeated replacement/interaction must not multiply effects. Removing or replacing a preview owner releases its old browser resource. Replacing an independent child must not clear a retained preview.
6. External scripts are loaded once per page lifetime according to the distribution's host/file contract. No execution script is returned in a fragment. No inline execution channels. CSS owns visual values.

The Coordinator/harness supplies a standard host skeleton, core installation and source/version, naming/area decisions, output location, and system-check baseline before the relevant role. Architects decide compliant files and mechanism in the existing design spec. Code belongs to the coder. Independent review and browser checks supply pass/fail evidence. Do not return a claim of browser success without executing it.
