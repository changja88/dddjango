# shop_service Fixture

Small Django-like Python project for code-backed eval cases.

The project intentionally avoids external dependencies. Files use Django naming and boundaries, but the validation command is standard-library friendly:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/dddjango-pycache python -m compileall apps tests
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests
```

Agents may add or edit files under `apps/` and `tests/` unless a public case says otherwise. Do not edit eval answer files or run artifacts.
