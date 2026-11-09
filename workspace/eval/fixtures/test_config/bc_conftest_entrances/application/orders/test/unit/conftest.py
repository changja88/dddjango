import pytest


@pytest.fixture(autouse=True)
def fresh_clock():
    yield
