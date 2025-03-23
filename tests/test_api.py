from os import environ, path, remove
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.app.main import app
from src.app.core.db import SqliteDatabase, get_session
from sqlalchemy import (
    create_engine, NullPool,
)

tmp_dir = Path("./tmp")
tmp_dir.mkdir(exist_ok=True)

TEST_DB_PATH = environ.get("TEST_DATABASE_PATH", "./tmp/pinggy.db")
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"


@pytest.fixture
def client():
    if path.exists(TEST_DB_PATH):
        remove(TEST_DB_PATH)
    test_db = SqliteDatabase(TEST_DB_URL)
    test_db.init_db()

    async def override_get_session():
        async with test_db.session() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_session] = override_get_session

    # Create test client
    test_client = TestClient(app)
    yield test_client

    # Clean up
    app.dependency_overrides.clear()

    if "CI" not in environ and path.exists(TEST_DB_PATH):
        import os
        os.remove(TEST_DB_PATH)


@pytest.fixture
def mock_create_tunnel():
    with patch('src.app.api.v1.create_tunnel') as mock:
        mock.return_value = ("random_pid", "http://random_http_url", "https://random_https_url")
        yield mock

@pytest.fixture
def mock_terminate_tunnel():
    with patch('src.app.api.v1.terminate_tunnel') as mock:
        yield mock

def test_create_tunnel(client, mock_create_tunnel):
    # act
    response = client.post("/api/tunnels", json={"hostname": "testhost", "port": 8080})

    # assert
    assert response.status_code == 201
    data = response.json()
    assert data["hostname"] == "testhost"
    assert data["port"] == 8080
    assert data["http_url"] == "http://random_http_url"
    assert data["https_url"] == "https://random_https_url"


def test_fetch_tunnel(client, mock_create_tunnel):
    # arrange
    create_response = client.post("/api/tunnels", json={"hostname": "testhost", "port": 8080})
    tunnel_id = create_response.json()["id"]

    # act
    fetch_response = client.get(f"/api/tunnels/{tunnel_id}")

    # assert
    assert fetch_response.status_code == 200
    data = fetch_response.json()
    assert data["id"] == tunnel_id
    assert data["hostname"] == "testhost"
    assert data["port"] == 8080


def test_delete_tunnel(client, mock_create_tunnel, mock_terminate_tunnel):
    # arrange
    create_response = client.post("/api/tunnels", json={"hostname": "testhost", "port": 8080})
    tunnel_id = create_response.json()["id"]

    # act
    delete_response = client.delete(f"/api/tunnels/{tunnel_id}")

    # assert
    assert delete_response.status_code == 204
