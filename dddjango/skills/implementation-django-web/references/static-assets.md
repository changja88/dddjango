# Static Assets

Use this reference for Django static file organization, CSS/JS placement, collectstatic/manifest concerns, and asset verification. This skill is provisional; follow the project’s existing asset pipeline when present.

## Organization

- Keep app-specific assets near the app when the project uses `app/static/app_name/...`.
- Keep shared design-system or global assets in the project’s established shared static location.
- Use clear names for CSS and JS files that reflect the page or component they support.
- Do not place generated build artifacts in source directories unless the project’s pipeline expects it.

## Loading Assets

- Use `{% load static %}` and `{% static 'path/to/file.css' %}` instead of hardcoded static URLs.
- Put CSS and JS includes in base-template blocks when pages need to opt in.
- Keep inline scripts small and local to the template only when external files would be less clear.
- Avoid mixing domain data transformations into JavaScript embedded in templates.

## Production Concerns

- Respect the project’s `STATIC_URL`, `STATIC_ROOT`, `STATICFILES_DIRS`, storage backend, and deployment pipeline.
- If the project uses manifest/static hashing, make sure asset references go through Django static resolution.
- If the project uses WhiteNoise, a bundler, or another asset pipeline, follow the existing convention rather than inventing a new one.
- Run or recommend `collectstatic` only when relevant to deployment or asset resolution, and report whether it was actually run.

## Verification

- Check that referenced static paths exist.
- Check that page templates load required CSS/JS without duplicate or stale references.
- For visible UI changes, verify rendering with available tests, screenshots, or browser checks when practical.
- If render/browser checks were not run, state that clearly.
