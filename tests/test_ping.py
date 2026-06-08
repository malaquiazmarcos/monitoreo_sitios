from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chequear_ping():
    response = client.get("/ping")

    assert response.status_code == 200

    assert response.json() == {"estado": "ok", "mensaje":"la api esta viva"}