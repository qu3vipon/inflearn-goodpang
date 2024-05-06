import pytest

from tests.utils import APIClient


@pytest.fixture(scope="session")
def api_client():
    return APIClient()
