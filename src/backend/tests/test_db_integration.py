import pytest
from app.database import get_db

@pytest.mark.asyncio
async def test_db_connection():
    db = await get_db()
    assert db is not None
