# Online Bookstore -- Project Structure

```
bookstore/
    .gitignore
    .env
    manage.py
    requirements/
        base.txt
        dev.txt
        prod.txt
    config/
        __init__.py
        settings/
            __init__.py
            base.py
            local.py
            production.py
            test.py
        urls.py
        wsgi.py
        asgi.py
    apps/
        users/
            __init__.py
            models.py
            views.py
            urls.py
            forms.py
            admin.py
            services.py
            tests/
                __init__.py
                test_models.py
                test_views.py
        books/
            __init__.py
            models.py
            views.py
            urls.py
            forms.py
            admin.py
            services.py
            tests/
                __init__.py
                test_models.py
                test_views.py
        orders/
            __init__.py
            models.py
            views.py
            urls.py
            forms.py
            admin.py
            services.py
            tests/
                __init__.py
                test_models.py
                test_views.py
        reviews/
            __init__.py
            models.py
            views.py
            urls.py
            forms.py
            admin.py
            services.py
            tests/
                __init__.py
                test_models.py
                test_views.py
```

## App Responsibilities

- **users** -- User authentication, profiles, account management.
- **books** -- Book catalog, categories, search, inventory.
- **orders** -- Order placement, order items, order status tracking.
- **reviews** -- Book reviews, ratings, review moderation.

## Design Decisions

- Two Scoops layout: `config/` for project settings, `apps/` for domain apps.
- Settings split into base/local/production/test with `django-environ` for secrets.
- Each app is named as a concise plural matching its domain concept.
- Each app has its own `tests/` package for organized test files.
- Service layer (`services.py`) included per app for when business logic outgrows models.
