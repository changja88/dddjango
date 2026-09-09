Updated only [design.md](/private/tmp/dddjango-web-js-integration-20260905/codex/app/design.md).

Exact sections changed:

- **§1 — Approved scope and inspected host:** Corrected the core static name to `web/htmx/htmx.min.js`; recorded the inspected `web` and `design_system` tuple mappings and attributed the supplied HTTP/hash/token verification to the Coordinator.
- **§7 — Loading, data and execution boundaries:** Corrected loader arguments to `web/htmx/htmx.min.js`, `web/js/password_visibility.js`, `web/js/image_preview.js`, and `web/css/ui_lab.css`. Explicitly retained `design_system/foundation/tokens.css`.

Verified that every other section is byte-for-byte unchanged. Static references match the corrected host, and file naming remains consistent with the distribution’s house rules. No UI implementation, extra files, or tests were created. Browser, HTTP, Django, and backstop checks were not run in this invocation.

Serena: skipped — this was a bounded document correction using basic file tools.