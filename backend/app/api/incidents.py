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
    AIAssessmentResponse,
    IncidentSummaryExport,
    IncidentClassificationRequest,
    IncidentClassificationResponse
)
from ..services.prompt_builder import PromptBuilder
from ..services.decision_logic import DecisionGuardrails
from ..services.classifier import IncidentClassifier
from .ai import AIService

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

# In-memory storage for MVP (use database in production)
incidents_db: Dict[str, IncidentState] = {}

# Initialize services
guardrails = DecisionGuardrails()
ai_service = AIService()
prompt_builder = PromptBuilder()
classifier = IncidentClassifier()


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


@router.post("/{incident_id}/assess", response_model=Dict)
async def assess_incident(incident_id: str):
    """
    Generate AI assessment for incident
    Determines what we know, what we need, and next steps
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]

    # Get system and user prompts
    system_prompt = prompt_builder.get_system_prompt()
    user_prompt = prompt_builder.build_initial_assessment_prompt(incident)

    # Generate AI response
    ai_response = ai_service.generate_response(system_prompt, user_prompt)

    # Parse response
    parsed = prompt_builder.parse_ai_response(ai_response, "initial_assessment")

    # Get playbook-based steps for validation
    playbook_steps = guardrails.get_applicable_investigation_steps(incident)

    # Add guardrails enrichment
    parsed["risk_level"] = guardrails.assess_risk_level(incident)
    needs_escalation, escalation_level = guardrails.check_escalation_needed(incident)
    parsed["escalation"] = {
        "required": needs_escalation,
        "level": escalation_level
    }
    parsed["playbook_steps"] = playbook_steps

    # Store assessment
    incident.current_assessment = parsed
    incident.assessment_history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "assessment": parsed
    })
    incident.updated_at = datetime.utcnow()

    incidents_db[incident_id] = incident

    return parsed


@router.post("/{incident_id}/containment", response_model=Dict)
async def get_containment_guidance(incident_id: str):
    """
    Generate containment and remediation guidance
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]

    # Get system and user prompts
    system_prompt = prompt_builder.get_system_prompt()
    user_prompt = prompt_builder.build_containment_prompt(incident)

    # Generate AI response
    ai_response = ai_service.generate_response(system_prompt, user_prompt)

    # Parse response
    parsed = prompt_builder.parse_ai_response(ai_response, "containment")

    # Get playbook-based actions
    playbook_actions = guardrails.get_applicable_containment_actions(incident)
    remediation_steps = guardrails.get_remediation_steps(incident)

    # Add guardrails enrichment
    parsed["playbook_containment_actions"] = playbook_actions
    parsed["playbook_remediation"] = remediation_steps

    # Validate AI recommendations
    if parsed.get("containment_actions"):
        approved, rejected = guardrails.validate_ai_recommendations(
            parsed["containment_actions"], incident
        )
        parsed["validated_actions"] = {
            "approved": approved,
            "requires_review": rejected
        }

    # Store assessment
    incident.current_assessment = parsed
    incident.assessment_history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "assessment": parsed
    })
    incident.updated_at = datetime.utcnow()

    incidents_db[incident_id] = incident

    return parsed


@router.get("/{incident_id}/export", response_model=IncidentSummaryExport)
async def export_incident_summary(incident_id: str):
    """
    Generate final incident summary for export
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident = incidents_db[incident_id]

    # Generate summary using AI
    system_prompt = prompt_builder.get_system_prompt()
    user_prompt = prompt_builder.build_summary_prompt(incident)
    ai_summary = ai_service.generate_response(system_prompt, user_prompt)

    # Build timeline from assessment history
    timeline = []
    for entry in incident.assessment_history:
        timeline.append({
            "timestamp": entry["timestamp"],
            "event": "Assessment performed",
            "details": entry["assessment"].get("response_type", "unknown")
        })

    # Create export object
    export = IncidentSummaryExport(
        incident_id=incident.incident_id,
        incident_type=incident.incident_type,
        created_at=incident.created_at,
        closed_at=datetime.utcnow() if incident.status == "closed" else None,
        incident_summary=ai_summary,
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


@router.post("/classify", response_model=IncidentClassificationResponse)
async def classify_incident(request: IncidentClassificationRequest):
    """
    Classify raw incident data to suggest incident type
    Uses AI to analyze logs, descriptions, or event data
    """
    try:
        # Build classification prompt
        prompt = classifier.build_classification_prompt(
            request.raw_data,
            request.context
        )

        # Get AI classification
        ai_response = ai_service.generate_response(
            "You are a security incident classification expert. Analyze data and provide structured JSON responses.",
            prompt
        )

        # Parse AI response
        parsed = classifier.parse_classification_response(ai_response)

        # Also get keyword-based scores as fallback/validation
        keyword_scores = classifier.keyword_based_classification(request.raw_data)

        # Build final response
        result = classifier.build_classification_result(parsed, keyword_scores)

        return result

    except Exception as e:
        # If AI fails, use keyword-based classification
        keyword_scores = classifier.keyword_based_classification(request.raw_data)

        # Find top classification
        top_type = max(keyword_scores.items(), key=lambda x: x[1])
        alternatives = sorted(
            [(t, s) for t, s in keyword_scores.items() if t != top_type[0] and s > 30],
            key=lambda x: x[1],
            reverse=True
        )[:3]

        from ..models.incident import IncidentTypeClassification

        primary = IncidentTypeClassification(
            incident_type=top_type[0],
            confidence=min(top_type[1], 100),
            reasoning="Classification based on keyword analysis (AI unavailable)",
            key_indicators=["Keyword-based analysis"]
        )

        alt_classifications = [
            IncidentTypeClassification(
                incident_type=t,
                confidence=min(s, 100),
                reasoning="Alternative based on keyword matching",
                key_indicators=[]
            )
            for t, s in alternatives
        ]

        return IncidentClassificationResponse(
            primary_classification=primary,
            alternative_classifications=alt_classifications,
            raw_data_summary="AI classification unavailable, using keyword matching",
            suggested_next_steps=["Review the raw data manually", "Select the most appropriate incident type"]
        )


@router.delete("/{incident_id}")
async def delete_incident(incident_id: str):
    """Delete an incident (for testing)"""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail="Incident not found")

    del incidents_db[incident_id]
    return {"message": "Incident deleted"}
