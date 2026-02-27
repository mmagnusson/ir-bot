"""
IncidentRepository — async persistence layer for IncidentState objects.
"""

from typing import List, Optional

from sqlalchemy import select, delete as sa_delete
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncEngine

from ..models.incident import IncidentState
from .database import incidents_table, get_engine


class IncidentRepository:
    def __init__(self, engine: AsyncEngine | None = None):
        self._engine = engine or get_engine()

    async def get(self, incident_id: str) -> Optional[IncidentState]:
        async with self._engine.begin() as conn:
            row = (
                await conn.execute(
                    select(incidents_table.c.data).where(
                        incidents_table.c.incident_id == incident_id
                    )
                )
            ).first()
        if row is None:
            return None
        return IncidentState.model_validate_json(row.data)

    async def create(self, incident: IncidentState) -> IncidentState:
        await self._save(incident)
        return incident

    async def save(self, incident: IncidentState) -> IncidentState:
        await self._save(incident)
        return incident

    async def list_all(self) -> List[IncidentState]:
        async with self._engine.begin() as conn:
            rows = (
                await conn.execute(
                    select(incidents_table.c.data).order_by(
                        incidents_table.c.created_at.desc()
                    )
                )
            ).all()
        return [IncidentState.model_validate_json(r.data) for r in rows]

    async def delete(self, incident_id: str) -> bool:
        async with self._engine.begin() as conn:
            result = await conn.execute(
                sa_delete(incidents_table).where(
                    incidents_table.c.incident_id == incident_id
                )
            )
        return result.rowcount > 0

    async def _save(self, incident: IncidentState) -> None:
        data = incident.model_dump_json()
        values = {
            "incident_id": incident.incident_id,
            "incident_type": incident.incident_type.value,
            "status": incident.status,
            "created_at": incident.created_at.isoformat(),
            "updated_at": incident.updated_at.isoformat(),
            "data": data,
        }
        stmt = sqlite_insert(incidents_table).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["incident_id"],
            set_={
                "incident_type": stmt.excluded.incident_type,
                "status": stmt.excluded.status,
                "updated_at": stmt.excluded.updated_at,
                "data": stmt.excluded.data,
            },
        )
        async with self._engine.begin() as conn:
            await conn.execute(stmt)
