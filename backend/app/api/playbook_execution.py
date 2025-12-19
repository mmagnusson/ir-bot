"""
Playbook Execution API Endpoints

REST API for playbook-driven incident response workflow.
Provides endpoints for step management, role assignments, and phase handoffs.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
from datetime import datetime

from ..models.incident import (
    StepUpdateRequest, RoleAssignmentRequest, PhaseHandoffRequest,
    PhaseSignOffRequest, StepExecution, PhaseExecution, StepStatus,
    EvidenceItem
)
from ..services.playbook_engine import PlaybookEngine
from .incidents import incidents_db  # Import shared incident storage

router = APIRouter(prefix="/api/incidents/{incident_id}/playbook", tags=["playbook"])

# Initialize playbook engine
playbook_engine = PlaybookEngine()


@router.get("/phases")
async def get_incident_phases(incident_id: str):
    """
    Get all phases with their metadata for this incident

    Returns phase information including:
    - Phase description
    - Primary role
    - SLA targets
    - Execution status
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]
    phases = playbook_engine.get_phases_for_incident(incident)

    # Update incident in database
    incidents_db[incident_id] = incident

    return phases


@router.get("/phases/{phase_name}/steps")
async def get_phase_steps(incident_id: str, phase_name: str):
    """
    Get all steps for a specific phase with execution status

    Returns list of steps with:
    - Step metadata (description, time estimate, etc.)
    - Execution status
    - Dependencies
    - Evidence requirements
    - Whether step applies to this incident
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]
    steps = playbook_engine.get_phase_steps(incident, phase_name)

    # Update incident in database
    incidents_db[incident_id] = incident

    return steps


@router.post("/steps/{step_id}/start")
async def start_step(incident_id: str, step_id: str, assigned_user: str):
    """
    Mark a step as started

    Checks dependencies before allowing step to start.
    Records start time and assigned user.
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]

    # Check dependencies
    can_start, reason = playbook_engine.check_step_dependencies(incident, step_id)
    if not can_start:
        raise HTTPException(status_code=400, detail=f"Cannot start step: {reason}")

    # Start the step
    updated = playbook_engine.start_step(incident, step_id, assigned_user)
    incidents_db[incident_id] = updated

    # Trigger notification
    playbook_engine.trigger_notifications(updated, "step_started", step_id)
    incidents_db[incident_id] = updated

    return {
        "message": "Step started",
        "step": updated.phase_executions[updated.status].steps[step_id]
    }


@router.put("/steps/{step_id}")
async def update_step(incident_id: str, step_id: str, request: StepUpdateRequest):
    """
    Update step status and add evidence

    Allows updating:
    - Status (in_progress, blocked, completed, skipped)
    - Assigned user
    - Notes
    - Blocked reason
    - Evidence items
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]

    try:
        updated = playbook_engine.update_step(incident, request)
        incidents_db[incident_id] = updated

        # Trigger notifications if step completed
        if request.status == StepStatus.COMPLETED:
            playbook_engine.trigger_notifications(updated, "step_completed", step_id)
            incidents_db[incident_id] = updated

        return {
            "message": "Step updated",
            "step": updated.phase_executions[updated.status].steps[step_id]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/steps/{step_id}/evidence")
async def add_evidence(incident_id: str, step_id: str, evidence: List[EvidenceItem]):
    """
    Add evidence items to a step

    Evidence can include:
    - Text notes
    - File references
    - Boolean flags
    - Numeric values
    - Timestamps
    - URLs
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]

    try:
        updated = playbook_engine.add_evidence_to_step(incident, step_id, evidence)
        incidents_db[incident_id] = updated

        # Trigger notification
        playbook_engine.trigger_notifications(updated, "evidence_uploaded", step_id)
        incidents_db[incident_id] = updated

        return {"message": "Evidence added", "evidence_count": len(evidence)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/roles/assign")
async def assign_role(incident_id: str, request: RoleAssignmentRequest):
    """
    Assign a user to a role

    Creates or updates role assignment with timestamp.
    Role assignments help track who is responsible for which aspects
    of the incident response.
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]

    updated = playbook_engine.assign_role(incident, request.role_name, request.assigned_user)
    incidents_db[incident_id] = updated

    return {
        "message": f"User {request.assigned_user} assigned to role {request.role_name}",
        "assignment": updated.role_assignments[request.role_name]
    }


@router.get("/roles")
async def get_role_assignments(incident_id: str):
    """
    Get all role assignments for this incident

    Returns dictionary of role_name -> assignment info
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]
    return incident.role_assignments


@router.post("/handoff")
async def initiate_handoff(
    incident_id: str,
    request: PhaseHandoffRequest,
    initiated_by: str
):
    """
    Initiate a phase handoff

    Checks handoff requirements before allowing transition.
    Requirements may include:
    - Minimum checklist completion percentage
    - All required fields complete
    - Phase sign-off

    Handoff is not complete until signed off by receiving role.
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]

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
    incidents_db[incident_id] = updated

    return {
        "message": "Handoff initiated",
        "requires_sign_off": True,
        "handoff": updated.handoff_history[-1]
    }


@router.post("/handoff/sign-off")
async def sign_off_handoff(incident_id: str, request: PhaseSignOffRequest):
    """
    Sign off on a phase handoff

    Completes the phase transition by:
    - Marking current phase as complete
    - Recording sign-off
    - Transitioning to next phase
    - Initializing next phase execution
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]

    try:
        updated = playbook_engine.sign_off_handoff(
            incident,
            request.signed_off_by,
            request.notes
        )
        incidents_db[incident_id] = updated

        return {
            "message": "Handoff signed off",
            "new_phase": updated.status,
            "handoff": updated.handoff_history[-1]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dashboard")
async def get_incident_dashboard(incident_id: str):
    """
    Get dashboard view with progress, SLA status, role assignments

    Returns comprehensive dashboard including:
    - Role assignments
    - Phase progress with completion percentages
    - SLA status
    - Pending handoffs
    - Recent notifications
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]
    dashboard = playbook_engine.build_dashboard(incident)
    return dashboard
