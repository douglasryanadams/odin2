from pytest import fixture
from starlette.testclient import TestClient

from search_api.main import app


@fixture
def test_client():
    return TestClient(app)
