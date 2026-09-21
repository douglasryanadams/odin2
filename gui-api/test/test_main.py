def test_root(test_client):
    response = test_client.get("/")
    assert response.status_code == 204


def test_search_no_get(test_client):
    response = test_client.get("/search")
    assert response.status_code == 405


def test_search_without_redirect(test_client):
    response = test_client.post("/search", json={"query": "Test Query"}, follow_redirects=False)
    assert response.status_code == 302


def test_search(test_client):
    response = test_client.post("/search", json={"query": "Test Query"})
    assert response.status_code == 200
    assert response.json() == "placeholder"


# TODO: Write test for failure case, where api-search fails
