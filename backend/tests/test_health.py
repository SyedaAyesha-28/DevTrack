
def test_health_endpoint_returns_healthy_status(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "healthy",
        "service": "DevTrack API",
    }
