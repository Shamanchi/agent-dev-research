"""API-тесты без сети: TestClient."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_health(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_corpus(client: TestClient) -> None:
    resp = client.get("/api/v1/corpus?q=caching&max_docs=5")
    assert resp.status_code == 200
    assert resp.json()[0]["title"] == "Redis caching ADR"


def test_brief(client: TestClient) -> None:
    resp = client.post("/api/v1/brief", json={"query": "caching redis", "max_docs": 2})
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload["docs"]) == 2
    assert payload["snippets"][0]["language"] == "python"


def test_brief_rejects_empty(client: TestClient) -> None:
    resp = client.post("/api/v1/brief", json={"query": "   ", "max_docs": 2})
    assert resp.status_code == 422


@pytest.mark.integration()
def test_brief_default_shape(client: TestClient) -> None:
    """Интеграционный по маркеру: форма брифа, без сети."""
    resp = client.post("/api/v1/brief", json={"query": "deploy docker"})
    assert resp.status_code == 200
    assert resp.json()["docs"][0]["title"] == "Deploy README"
