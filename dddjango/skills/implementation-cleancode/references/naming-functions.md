# Naming And Functions

Use this reference for names, function shape, arguments, side effects, command/query separation, formatting, and docstrings.

## Naming

- Names should reveal intent, role, and usage without needing a comment.
- Use one word for one concept; avoid synonyms like `fetch`, `retrieve`, and `get` for the same operation unless the project already distinguishes them.
- Class names should be nouns or noun phrases; methods/functions should usually be verbs or verb phrases.
- Use positive boolean names such as `is_valid`, `has_permission`, or `can_cancel`; avoid confusing negative names.
- Use plural names for collections and precise suffixes such as `_count` or `_index` when they matter.
- Longer scopes need more descriptive names; short loop variables are acceptable only in small, obvious loops.

## Functions

- Keep a function at one abstraction level.
- If a meaningful extracted name is obvious, the original function may be doing more than one thing.
- Avoid flag arguments that make one function choose between multiple behaviors.
- Keep argument lists short; introduce a parameter object or value object when a group travels together.
- Separate commands from queries. A function should either change state or answer a question, not surprise callers by doing both.
- Make side effects visible in the name or isolate them in an orchestration function.
- Prefer guard clauses when they make the main path clearer.

## Formatting And Docstrings

- Follow the project formatter and lint configuration rather than inventing local style.
- Use docstrings for public modules, classes, and functions when callers need behavior, parameter, return, side-effect, or exception details.
- Keep inline comments rare and focused on intent, trade-off, or warning.
