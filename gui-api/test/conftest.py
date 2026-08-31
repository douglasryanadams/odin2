from pytest import fixture
from src.main import app
from starlette.testclient import TestClient


@fixture
def test_client():
    return TestClient(app)
