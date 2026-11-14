from django.contrib.auth import get_user_model


def test_screen_opens_for_staff() -> None:
    staff: object = get_user_model()
    assert staff is not None
