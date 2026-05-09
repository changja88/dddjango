# Templates

Use this reference for Django templates, inheritance, base templates, includes/components, and template style. This skill is provisional; exact component or design-system conventions must follow the project.

## Template Role

- Keep templates responsible for presentation and presentation-related branching only.
- Do not put domain rules, state transitions, pricing, permission policy, or complex data selection in templates.
- Prepare data in views, selectors, or services before rendering.
- Use template filters/tags for small presentation transforms, not business decisions.

## Inheritance And Base Templates

- Put shared document structure, common blocks, common assets, and navigation in a base template when the project uses inheritance.
- Keep `{% extends %}` as the first non-comment template line.
- Name blocks explicitly and close them with the block name, such as `{% endblock content %}`.
- Keep page-specific templates focused on the page’s content and local blocks.

## Includes And Components

- Use includes/components for repeated UI fragments that share meaning and change together.
- Keep include context explicit; avoid relying on broad implicit context when a small set of variables is enough.
- Do not turn every small snippet into an include. Reuse only when it improves clarity or consistency.

## Template Style

- Put one space inside `{{ variable }}` and `{% tag %}`.
- Load template libraries alphabetically when multiple libraries are needed.
- Keep template indentation consistent with the project; Django source style uses two spaces for HTML templates.
- Use `{% load static %}` when rendering static assets through Django’s staticfiles system.
- Avoid `|safe` and `mark_safe()` unless the value is trusted and escaping has been deliberately handled.
