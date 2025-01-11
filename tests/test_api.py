import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.core.db import db

client = TestClient(app)


@pytest.fixture(scope="session")
def setup_db():
    db.init_db()


@pytest.fixture
def mock_create_tunnel():
    with patch('app.api.v1.create_pinggy_tunnel') as mock:
        mock.return_value = ("random_pid", "http://random_http_url", "https://random_https_url")
        yield mock

@pytest.fixture
def mock_terminate_tunnel():
    with patch('app.api.v1.terminate_tunnel') as mock:
        yield mock

def test_create_tunnel(mock_create_tunnel):
    # act
    response = client.post("/api/v1/tunnels", json={"hostname": "testhost", "port": 8080})

    # assert
    assert response.status_code == 201
    data = response.json()
    assert data["hostname"] == "testhost"
    assert data["port"] == 8080
    assert data["http_url"] == "http://random_http_url"
    assert data["https_url"] == "https://random_https_url"


def test_fetch_tunnel(mock_create_tunnel, setup_db):
    # arrange
    create_response = client.post("/api/v1/tunnels", json={"hostname": "testhost", "port": 8080})
    tunnel_id = create_response.json()["id"]

    # act
    fetch_response = client.get(f"/api/v1/tunnels/{tunnel_id}")

    # assert
    assert fetch_response.status_code == 200
    data = fetch_response.json()
    assert data["id"] == tunnel_id
    assert data["hostname"] == "testhost"
    assert data["port"] == 8080


def test_delete_tunnel(mock_create_tunnel, mock_terminate_tunnel):
    # arrange
    create_response = client.post("/api/v1/tunnels", json={"hostname": "testhost", "port": 8080})
    tunnel_id = create_response.json()["id"]

    # act
    delete_response = client.delete(f"/api/v1/tunnels/{tunnel_id}")

    # assert
    assert delete_response.status_code == 204
