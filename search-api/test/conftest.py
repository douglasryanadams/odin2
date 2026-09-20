from pytest import fixture
from search_api.main import app
from starlette.testclient import TestClient


@fixture
def test_client():
    return TestClient(app)
