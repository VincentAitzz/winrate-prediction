from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_predict_endpoint_ok():
    payload = {
        "team_champions": [1, 2, 3, 4, 5],
        "enemy_champions": [6, 7, 8, 9, 10],
    }

    response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "winrate" in data
    assert 0.0 <= data["winrate"] <= 1.0
