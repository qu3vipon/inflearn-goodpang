def test_health_check(api_client):
    response = api_client.get("")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
