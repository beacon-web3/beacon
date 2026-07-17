import pytest

from tests.recommendations.factories import AccountFactory


@pytest.fixture
def account():
    return AccountFactory()
