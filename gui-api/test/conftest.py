from pytest import fixture
from starlette.testclient import TestClient

from gui_api.main import app


@fixture
def test_client():
    return TestClient(app)
