import pytest
from httpx import AsyncClient, ASGITransport
from app import app


@pytest.mark.asyncio
async def test_generate_fallback():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # call the index to ensure it's up
        r = await ac.get("/")
        assert r.status_code == 200

        # call the generate endpoint using the fallback (no OPENAI_API_KEY)
        data = {"dish": "test pilaf"}
        r = await ac.post("/generate", data=data)
        assert r.status_code == 200
        assert "Ingredients" in r.text or "Recipe" in r.text
