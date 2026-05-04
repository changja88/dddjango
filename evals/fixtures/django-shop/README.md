# django-shop fixture

Small Django fixture for dddjango real-repo forward evaluation.

The code intentionally contains common issues:

- `Order` has business workflow logic in the model.
- `views.py` mixes HTTP parsing, transaction handling, stock updates, and response shaping.
- `api_drf.py` contains a legacy DRF serializer/APIView implementation that should be converted to Django Ninja.
- tests are thin and need pytest coverage around cancellation, stock reservation, and API behavior.

This fixture is not intended to be a production app. It is a stable text fixture for patch-oriented evaluation.
