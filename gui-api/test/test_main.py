def test_root(test_client):
    response = test_client.get("/")
    assert response.status_code == 200


def test_search_no_get(test_client):
    response = test_client.get("/search")
    assert response.status_code == 405


def test_search(test_client):
    response = test_client.post("/search", json={"req": "placeholder"})
    assert response.status_code == 200
    assert response.json() == {"res": "placeholder"}
