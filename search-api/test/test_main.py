import pytest


def test_root(test_client):
    response = test_client.get("/")
    assert response.status_code == 204


def test_search_no_get(test_client):
    response = test_client.get("/brave")
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_search(test_client, fake_redis):
    response = test_client.post("/brave", json={"query": "Test Search Query"}, follow_redirects=False)
    assert response.status_code == 302


@pytest.mark.asyncio
async def test_search_with_redirects(test_client, fake_redis):
    response = test_client.post("/brave", json={"query": "Test Search Query"}, follow_redirects=True)
    assert response.status_code == 200
    assert response.json() == {"result": "placeholder"}
