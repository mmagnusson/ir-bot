"""
Playbook Execution API Endpoints

REST API for playbook-driven incident response workflow.
Provides endpoints for step management, role assignments, and phase handoffs.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..models.incident import (
    StepUpdateRequest, RoleAssignmentRequest, PhaseHandoffRequest,
    PhaseSignOffRequest, StepExecution, PhaseExecution, StepStatus,
    EvidenceItem
)
from ..services.playbook_engine import PlaybookEngine
from ..db.repository import IncidentRepository
from ..dependencies import get_repository
from .incidents import _get_incident_or_404

router = APIRouter(prefix="/api/incidents/{incident_id}/playbook", tags=["playbook"])

# Initialize playbook engine
playbook_engine = PlaybookEngine()


@router.get("/phases")
async def get_incident_phases(
    incident_id: str,
    repo: IncidentRepository = Depends(get_repository),
):
    """
    Get all phases with their metadata for this incident
    """
    incident = await _get_incident_or_404(incident_id, repo)
    phases = playbook_engine.get_phases_for_incident(incident)
    await repo.save(incident)
    return phases


@router.get("/phases/{phase_name}/steps")
async def get_phase_steps(
    incident_id: str,
    phase_name: str,
    repo: IncidentRepository = Depends(get_repository),
):
    """
    Get all steps for a specific phase with execution status
    """
    incident = await _get_incident_or_404(incident_id, repo)
    steps = playbook_engine.get_phase_steps(incident, phase_name)
    await repo.save(incident)
    return steps


@router.post("/steps/{step_id}/start")
async def start_step(
    incident_id: str,
    step_id: str,
    assigned_user: str,
    repo: IncidentRepository = Depends(get_repository),
):
    """
    Mark a step as started
    """
    incident = await _get_incident_or_404(incident_id, repo)

    # Check dependencies
    can_start, reason = playbook_engine.check_step_dependencies(incident, step_id)
    if not can_start:
        raise HTTPException(status_code=400, detail=f"Cannot start step: {reason}")

    # Start the step
    updated = playbook_engine.start_step(incident, step_id, assigned_user)
    playbook_engine.trigger_notifications(updated, "step_started", step_id)
    await repo.save(updated)

    return {
        "message": "Step started",
        "step": updated.phase_executions[updated.status].steps[step_id]
    }


@router.put("/steps/{step_id}")
async def update_step(
    incident_id: str,
    step_id: str,
    request: StepUpdateRequest,
    repo: IncidentRepository = Depends(get_repository),
):
    """
    Update step status and add evidence
    """
    incident = await _get_incident_or_404(incident_id, repo)

    try:
        updated = playbook_engine.update_step(incident, request)

        if request.status == StepStatus.COMPLETED:
            playbook_engine.trigger_notifications(updated, "step_completed", step_id)

        await repo.save(updated)

        return {
            "message": "Step updated",
            "step": updated.phase_executions[updated.status].steps[step_id]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/steps/{step_id}/evidence")
async def add_evidence(
    incident_id: str,
    step_id: str,
    evidence: List[EvidenceItem],
    repo: IncidentRepository = Depends(get_repository),
):
    """
    Add evidence items to a step
    """
    incident = await _get_incident_or_404(incident_id, repo)

    try:
        updated = playbook_engine.add_evidence_to_step(incident, step_id, evidence)
        playbook_engine.trigger_notifications(updated, "evidence_uploaded", step_id)
        await repo.save(updated)

        return {"message": "Evidence added", "evidence_count": len(evidence)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/roles/assign")
async def assign_role(
    incident_id: str,
    request: RoleAssignmentRequest,
    repo: IncidentRepository = Depends(get_repository),
):
    """
    Assign a user to a role
    """
    incident = await _get_incident_or_404(incident_id, repo)

    updated = playbook_engine.assign_role(incident, request.role_name, request.assigned_user)
    await repo.save(updated)

    return {
        "message": f"User {request.assigned_user} assigned to role {request.role_name}",
        "assignment": updated.role_assignments[request.role_name]
    }


@router.get("/roles")
async def get_role_assignments(
    incident_id: str,
    repo: IncidentRepository = Depends(get_repository),
):
    """
    Get all role assignments for this incident
    """
    incident = await _get_incident_or_404(incident_id, repo)
    return incident.role_assignments


@router.post("/handoff")
async def initiate_handoff(
    incident_id: str,
    request: PhaseHandoffRequest,
    initiated_by: str,
    repo: IncidentRepository = Depends(get_repository),
):
    """
    Initiate a phase handoff
    """
    incident = await _get_incident_or_404(incident_id, repo)

    # Check handoff requirements
    can_handoff, requirements = playbook_engine.check_handoff_requirements(
        incident,
        request.to_phase
    )

    if not can_handoff:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Handoff requirements not met",
                "requirements": requirements
            }
        )

    updated = playbook_engine.initiate_handoff(
        incident,
        request.to_phase,
        initiated_by,
        request.handoff_notes
    )
    await repo.save(updated)

    return {
        "message": "Handoff initiated",
        "requires_sign_off": True,
        "handoff": updated.handoff_history[-1]
    }


@router.post("/handoff/sign-off")
async def sign_off_handoff(
    incident_id: str,
    request: PhaseSignOffRequest,
    repo: IncidentRepository = Depends(get_repository),
):
    """
    Sign off on a phase handoff
    """
    incident = await _get_incident_or_404(incident_id, repo)

    try:
        updated = playbook_engine.sign_off_handoff(
            incident,
            request.signed_off_by,
            request.notes
        )
        await repo.save(updated)

        return {
            "message": "Handoff signed off",
            "new_phase": updated.status,
            "handoff": updated.handoff_history[-1]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dashboard")
async def get_incident_dashboard(
    incident_id: str,
    repo: IncidentRepository = Depends(get_repository),
):
    """
    Get dashboard view with progress, SLA status, role assignments
    """
    incident = await _get_incident_or_404(incident_id, repo)
    dashboard = playbook_engine.build_dashboard(incident)
    return dashboard
