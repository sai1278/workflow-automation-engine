import pytest
from app.main import create_app
from httpx import AsyncClient
from asgi_lifespan import LifespanManager
from httpx import ASGITransport  # ✅ Import ASGITransport

@pytest.mark.asyncio
async def test_post_data_ok():
    app = create_app()
    # Wrap app with LifespanManager to handle startup/shutdown
    async with LifespanManager(app):
        # Use AsyncClient with ASGI transport
        async with AsyncClient(
            transport=ASGITransport(app=app),  # ✅ use ASGITransport instead of app=
            base_url="http://testserver"
        ) as client:
            response = await client.post("/data", json={"name": "a", "value": 10})
    assert response.status_code == 201
    assert response.json()["status"] == "accepted"

@pytest.mark.asyncio
async def test_post_data_invalid():
    app = create_app()
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app),  # ✅ use ASGITransport instead of app=
            base_url="http://testserver"
        ) as client:
            response = await client.post("/data", json={"name": "", "value": -1})
    assert response.status_code in [400, 422]
