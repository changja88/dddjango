import pytest


@pytest.fixture
def guest_session(db):
    return None


@pytest.fixture(autouse=True)
def database_for_every_test(db):
    yield


@pytest.fixture(autouse=False)
def explicit_only(db):
    return None
