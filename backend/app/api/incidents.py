"""
Incident API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
import uuid
from datetime import datetime

from ..models.incident import (
    IncidentState,
    IncidentCreateRequest,
    IncidentUpdateRequest,
    IncidentSummaryExport
)
from ..services.decision_logic import DecisionGuardrails

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

# In-memory storage for MVP (use database in production)
incidents_db: Dict[str, IncidentState] = {}

# Initialize services
guardrails = DecisionGuardrails()


@router.post("/", response_model=IncidentState)
async def create_incident(request: IncidentCreateRequest):
    """Create a new incident"""
    incident_id = str(uuid.uuid4())

    # Build incident with appropriate data field based on incident type
    incident_data = {
        "incident_id": incident_id,
        "incident_type": request.incident_type,
    }

    # Map incident type to corresponding data field
    if request.phishing_data:
        incident_data["phishing_data"] = request.phishing_data
    if request.malware_data:
        incident_data["malware_data"] = request.malware_data
    if request.account_compromise_data:
        incident_data["account_compromise_data"] = request.account_compromise_data
    if request.data_breach_data:
        incident_data["data_breach_data"] = request.data_breach_data
    if request.ransomware_data:
        incident_data["ransomware_data"] = request.ransomware_data
    if request.insider_threat_data:
        incident_data["insider_threat_data"] = request.insider_threat_data
    if request.ddos_data:
        incident_data["ddos_data"] = request.ddos_data
    if request.unauthorized_access_data:
        incident_data["unauthorized_access_data"] = request.unauthorized_access_data
    if request.bec_data:
        incident_data["bec_data"] = request.bec_data
    if request.web_application_attack_data:
        incident_data["web_application_attack_data"] = request.web_application_attack_data
    if request.data_exfiltration_data:
        incident_data["data_exfiltration_data"] = request.data_exfiltration_data
    if request.supply_chain_attack_data:
        incident_data["supply_chain_attack_data"] = request.supply_chain_attack_data
    if request.cloud_account_compromise_data:
        incident_data["cloud_account_compromise_data"] = request.cloud_account_compromise_data
    if request.api_security_breach_data:
        incident_data["api_security_breach_data"] = request.api_security_breach_data
    if request.credential_stuffing_data:
        incident_data["credential_stuffing_data"] = request.credential_stuffing_data
    if request.zero_day_exploit_data:
        incident_data["zero_day_exploit_data"] = request.zero_day_exploit_data
    if request.container_compromise_data:
        incident_data["container_compromise_data"] = request.container_compromise_data
    if request.iot_device_compromise_data:
        incident_data["iot_device_compromise_data"] = request.iot_device_compromise_data
    if request.backup_system_compromise_data:
        incident_data["backup_system_compromise_data"] = request.backup_system_compromise_data
    if request.dns_hijacking_data:
        incident_data["dns_hijacking_data"] = request.dns_hijacking_data
    if request.saas_application_compromise_data:
        incident_data["saas_application_compromise_data"] = request.saas_application_compromise_data
    if request.mobile_device_compromise_data:
        incident_data["mobile_device_compromise_data"] = request.mobile_device_compromise_data
    if request.regulatory_compliance_incident_data:
        incident_data["regulatory_compliance_incident_data"] = request.regulatory_compliance_incident_data

    incident = IncidentState(**incident_data)

    # Validate incident data
    is_valid, errors = guardrails.validate_incident_data(incident)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Validation errors: {errors}")

    incidents_db[incident_id] = incident
    return incident


@router.get("/{incident_id}", response_model=IncidentState)
async def get_incident(incident_id: str):
    """Get incident by ID"""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incidents_db[incident_id]


@router.put("/{incident_id}", response_model=IncidentState)
async def update_incident(incident_id: str, request: IncidentUpdateRequest):
    """Update incident with new information"""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]

    # Update type-specific data fields
    if request.phishing_data:
        incident.phishing_data = request.phishing_data
    if request.malware_data:
        incident.malware_data = request.malware_data
    if request.account_compromise_data:
        incident.account_compromise_data = request.account_compromise_data
    if request.data_breach_data:
        incident.data_breach_data = request.data_breach_data
    if request.ransomware_data:
        incident.ransomware_data = request.ransomware_data
    if request.insider_threat_data:
        incident.insider_threat_data = request.insider_threat_data
    if request.ddos_data:
        incident.ddos_data = request.ddos_data
    if request.unauthorized_access_data:
        incident.unauthorized_access_data = request.unauthorized_access_data
    if request.bec_data:
        incident.bec_data = request.bec_data
    if request.web_application_attack_data:
        incident.web_application_attack_data = request.web_application_attack_data
    if request.data_exfiltration_data:
        incident.data_exfiltration_data = request.data_exfiltration_data
    if request.supply_chain_attack_data:
        incident.supply_chain_attack_data = request.supply_chain_attack_data
    if request.cloud_account_compromise_data:
        incident.cloud_account_compromise_data = request.cloud_account_compromise_data
    if request.api_security_breach_data:
        incident.api_security_breach_data = request.api_security_breach_data
    if request.credential_stuffing_data:
        incident.credential_stuffing_data = request.credential_stuffing_data
    if request.zero_day_exploit_data:
        incident.zero_day_exploit_data = request.zero_day_exploit_data
    if request.container_compromise_data:
        incident.container_compromise_data = request.container_compromise_data
    if request.iot_device_compromise_data:
        incident.iot_device_compromise_data = request.iot_device_compromise_data
    if request.backup_system_compromise_data:
        incident.backup_system_compromise_data = request.backup_system_compromise_data
    if request.dns_hijacking_data:
        incident.dns_hijacking_data = request.dns_hijacking_data
    if request.saas_application_compromise_data:
        incident.saas_application_compromise_data = request.saas_application_compromise_data
    if request.mobile_device_compromise_data:
        incident.mobile_device_compromise_data = request.mobile_device_compromise_data
    if request.regulatory_compliance_incident_data:
        incident.regulatory_compliance_incident_data = request.regulatory_compliance_incident_data

    if request.actions_taken:
        incident.actions_taken.extend(request.actions_taken)

    if request.status:
        incident.status = request.status

    incident.updated_at = datetime.utcnow()

    # Validate updated data
    is_valid, errors = guardrails.validate_incident_data(incident)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Validation errors: {errors}")

    incidents_db[incident_id] = incident
    return incident


@router.get("/{incident_id}/export", response_model=IncidentSummaryExport)
async def export_incident_summary(incident_id: str):
    """
    Generate final incident summary for export
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]

    # Build summary from incident data (no AI)
    summary_parts = [
        f"Incident Type: {incident.incident_type.value}",
        f"Status: {incident.status}",
        f"Created: {incident.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
    ]

    if incident.status == "closed" and incident.updated_at:
        summary_parts.append(f"Closed: {incident.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

    summary_parts.append(f"\nActions Taken: {len(incident.actions_taken)}")
    summary_parts.append(f"Open Risks: {len(incident.open_risks)}")

    playbook_summary = summary_parts + [
        "\nThis incident was handled following established playbook procedures."
    ]

    incident_summary = "\n".join(playbook_summary)

    # Build timeline from incident lifecycle
    timeline = [
        {
            "timestamp": incident.created_at.isoformat(),
            "event": "Incident Created",
            "details": f"Type: {incident.incident_type.value}"
        }
    ]

    if incident.status != "intake":
        timeline.append({
            "timestamp": incident.updated_at.isoformat(),
            "event": f"Phase: {incident.status}",
            "details": f"Current status: {incident.status}"
        })

    # Create export object
    export = IncidentSummaryExport(
        incident_id=incident.incident_id,
        incident_type=incident.incident_type,
        created_at=incident.created_at,
        closed_at=incident.updated_at if incident.status == "closed" else None,
        incident_summary=incident_summary,
        actions_taken=incident.actions_taken,
        open_risks=incident.open_risks,
        recommended_followups=incident.recommended_followups,
        timeline=timeline
    )

    return export


@router.get("/", response_model=List[IncidentState])
async def list_incidents():
    """List all incidents"""
    return list(incidents_db.values())


@router.delete("/{incident_id}")
async def delete_incident(incident_id: str):
    """Delete an incident (for testing)"""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    del incidents_db[incident_id]
    return {"message": "Incident deleted"}

