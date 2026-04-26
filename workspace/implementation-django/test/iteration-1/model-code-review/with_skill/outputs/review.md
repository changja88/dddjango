# Django Code Review

## Summary

The code defines a `Product` model, a `ProductListView`, and a `post_save` signal handler. The model's `__str__` method and `Meta.ordering` are correctly placed per Django's field ordering convention. However, the code has several significant issues ranging from N+1 queries to boolean flag proliferation and misuse of signals.

---

## Findings

### 1. Boolean Flag Proliferation

```
[Boolean flag proliferation] -- Three BooleanField fields (is_active, is_featured, is_on_sale) represent
overlapping product states. This pattern allows invalid state combinations (e.g., a product that is both
inactive and featured) and makes filtering logic verbose. Use TextChoices or IntegerChoices to model
mutually exclusive states as a single field. Independent boolean traits (like is_active for soft-delete)
may remain as standalone BooleanField, but is_featured and is_on_sale suggest product "display status"
that is better expressed as a single enumerated field.
```

### 2. FloatField Used for Price

```
[Model field selection] -- price uses FloatField, which suffers from floating-point precision errors
(e.g., 0.1 + 0.2 != 0.3). Money and currency values must use DecimalField(max_digits=..., decimal_places=2)
to guarantee exact decimal arithmetic at both the Python and database level.
```

### 3. N+1 Query in ProductListView

```
[Missing select_related] -- The view iterates over all products and accesses p.category.name inside the
loop. Without select_related("category"), Django issues a separate SQL query for each product's category,
producing an N+1 problem. For a list of 1000 products, this means 1001 queries instead of 1.
Fix: Product.objects.select_related("category").all()
```

### 4. No Pagination

```
[View pattern] -- Product.objects.all() loads every product from the database into memory. Without
pagination, this view will degrade severely as the product count grows. Use Django's built-in Paginator
or, if this is an API endpoint, switch to a DRF ListAPIView with pagination_class configured.
```

### 5. Manual Serialization in View (Fat View)

```
[Fat Model, Thin View] -- The view manually builds a list of dictionaries in a for-loop, embedding
data transformation logic directly in the view layer. This violates the Thin View principle. Extract
this to either a model method, a values()/values_list() queryset call, or a DRF Serializer. Using
values("name", "category__name", "price") would also eliminate the N+1 problem entirely.
```

### 6. Signal Used for Same-App Logic

```
[Signal misuse] -- The post_save signal handler update_search_index reacts to Product saves to rebuild a
search index. Since Product and the signal handler live in the same app, this creates invisible coupling
that makes the code harder to trace and debug. Signals should be reserved for third-party model hooks or
breaking circular dependencies. Replace this with a save() override on the Product model, or call
rebuild_search_index() directly from a service function that handles product creation/updates.
```

### 7. Django 5.x Features Not Used

```
[Django 5.x features] -- The is_active field uses default=True, which is computed in Python. If the
project targets Django 5.x, consider db_default=True to set the default at the database level. This
ensures correctness even when rows are inserted outside Django (e.g., bulk SQL imports, data migrations).
```

---

## Review Checklist Results

| Check | Status | Notes |
|-------|--------|-------|
| Project structure | N/A | Not enough context to evaluate |
| Model field ordering | PASS | fields -> Meta -> `__str__` is correct |
| Boolean flag proliferation | FAIL | Three boolean flags should be consolidated |
| Missing select_related/prefetch_related | FAIL | category accessed in loop without select_related |
| N+1 queries in views | FAIL | Direct consequence of missing select_related |
| save() without update_fields | N/A | No save() calls in this code |
| Signals for same-app logic | FAIL | post_save on Product should be direct call |
| fields = `"__all__"` in form/serializer | N/A | No forms or serializers present |
| Multi-table inheritance | PASS | Not used |
| Raw SQL with string interpolation | PASS | Not used |
| Missing CSRF protection | PASS | View only handles GET |
| CBV with 4+ Mixins | PASS | No excessive Mixin usage |
| Fat views with business logic | FAIL | Manual dict-building belongs elsewhere |
| Missing assertNumQueries | N/A | No tests present |
| Django 5.x features not used | FAIL | db_default not used where applicable |
