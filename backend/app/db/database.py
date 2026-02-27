"""
Database engine, table definitions, and initialization for SQLite persistence.
"""

import os
from pathlib import Path

from sqlalchemy import MetaData, Table, Column, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

metadata = MetaData()

incidents_table = Table(
    "incidents",
    metadata,
    Column("incident_id", Text, primary_key=True),
    Column("incident_type", Text, nullable=False),
    Column("status", Text, nullable=False),
    Column("created_at", Text, nullable=False),
    Column("updated_at", Text, nullable=False),
    Column("data", Text, nullable=False),
)

_engine: AsyncEngine | None = None


def get_db_path() -> str:
    return os.environ.get("IR_BOT_DB_PATH", "./data/ir_bot.db")


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        db_path = get_db_path()
        _engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    return _engine


async def init_db() -> None:
    """Create the data directory and tables if they don't exist."""
    db_path = get_db_path()
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
