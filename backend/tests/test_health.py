import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from main import app


@pytest.mark.asyncio
async def test_health():
    """Test health endpoint"""
    from starlette.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_without_auth():
    """Health endpoint should not require auth"""
    from starlette.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
