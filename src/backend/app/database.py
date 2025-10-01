# app/database.py
import asyncio

async def get_db():
    # simulate async DB connection
    await asyncio.sleep(0.01)
    return "fake_db_connection"
