"""
FastAPI dependency injection for the incident repository.
"""

from .db.repository import IncidentRepository


def get_repository() -> IncidentRepository:
    return IncidentRepository()
