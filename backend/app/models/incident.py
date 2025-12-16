from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class IncidentType(str, Enum):
    PHISHING = "phishing"
    MALWARE = "malware"
    ACCOUNT_COMPROMISE = "account_compromise"
    DATA_BREACH = "data_breach"
    RANSOMWARE = "ransomware"
    INSIDER_THREAT = "insider_threat"
    DDOS = "ddos"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


class YesNoUnknown(str, Enum):
    YES = "yes"
    NO = "no"
    UNKNOWN = "unknown"


class Observables(BaseModel):
    url: Optional[str] = None
    hash: Optional[str] = None
    sender_email: Optional[str] = None
    sender_ip: Optional[str] = None


class PhishingIncidentData(BaseModel):
    """Structured data for phishing incidents"""
    reporting_user_email: str = Field(..., description="Email of the user who reported the incident")
    user_clicked: YesNoUnknown = Field(default=YesNoUnknown.UNKNOWN, description="Did user click a link?")
    attachment_opened: YesNoUnknown = Field(default=YesNoUnknown.UNKNOWN, description="Did user open an attachment?")
    credentials_entered: YesNoUnknown = Field(default=YesNoUnknown.UNKNOWN, description="Did user enter credentials?")
    time_of_report: datetime = Field(default_factory=datetime.utcnow, description="When was this reported?")
    headers_available: bool = Field(default=False, description="Are email headers available?")
    observables: Observables = Field(default_factory=Observables, description="Observable indicators")

    # Updated during investigation
    credential_submission_confirmed: Optional[YesNoUnknown] = None
    suspicious_signins_observed: Optional[YesNoUnknown] = None
    mfa_enabled: Optional[YesNoUnknown] = None
    other_affected_users: Optional[YesNoUnknown] = None


class MalwareIncidentData(BaseModel):
    """Structured data for malware incidents"""
    reporting_user_email: str = Field(..., description="Email of the user who reported the incident")
    file_executed: YesNoUnknown = Field(default=YesNoUnknown.UNKNOWN, description="Was the file executed?")
    suspicious_behavior: str = Field(default="", description="Describe suspicious behavior observed")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")
    observables: Observables = Field(default_factory=Observables, description="Observable indicators")

    # Investigation findings
    malware_type: Optional[str] = None
    c2_communication_detected: Optional[YesNoUnknown] = None
    data_exfiltration_suspected: Optional[YesNoUnknown] = None
    other_infected_systems: Optional[YesNoUnknown] = None


class AccountCompromiseIncidentData(BaseModel):
    """Structured data for account compromise incidents"""
    affected_user_email: str = Field(..., description="Email of the compromised account")
    unauthorized_access_detected: YesNoUnknown = Field(default=YesNoUnknown.YES, description="Unauthorized access confirmed?")
    suspicious_activities: str = Field(default="", description="Describe suspicious activities")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    access_method: Optional[str] = None  # e.g., "stolen credentials", "session hijacking"
    mfa_bypassed: Optional[YesNoUnknown] = None
    data_accessed: Optional[YesNoUnknown] = None
    actions_taken_by_attacker: Optional[str] = None


class DataBreachIncidentData(BaseModel):
    """Structured data for data breach incidents"""
    data_type_affected: str = Field(..., description="Type of data affected (PII, credentials, etc.)")
    number_of_records: Optional[int] = Field(None, description="Estimated number of records affected")
    breach_source: str = Field(default="", description="How was the data breached?")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    exfiltration_confirmed: Optional[YesNoUnknown] = None
    attacker_identified: Optional[YesNoUnknown] = None
    regulatory_notification_required: Optional[YesNoUnknown] = None


class RansomwareIncidentData(BaseModel):
    """Structured data for ransomware incidents"""
    reporting_user_email: str = Field(..., description="Email of the user who reported the incident")
    files_encrypted: YesNoUnknown = Field(default=YesNoUnknown.UNKNOWN, description="Are files encrypted?")
    ransom_note_present: YesNoUnknown = Field(default=YesNoUnknown.UNKNOWN, description="Was a ransom note found?")
    ransom_amount: Optional[str] = Field(None, description="Ransom amount demanded")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    ransomware_variant: Optional[str] = None
    spread_to_other_systems: Optional[YesNoUnknown] = None
    backups_affected: Optional[YesNoUnknown] = None


class InsiderThreatIncidentData(BaseModel):
    """Structured data for insider threat incidents"""
    suspect_user_email: str = Field(..., description="Email of the suspected insider")
    suspicious_activity: str = Field(..., description="Describe the suspicious activity")
    data_access_anomaly: YesNoUnknown = Field(default=YesNoUnknown.UNKNOWN, description="Unusual data access detected?")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    intent_determined: Optional[str] = None  # "malicious", "negligent", "unknown"
    data_exfiltrated: Optional[YesNoUnknown] = None
    hr_notified: Optional[YesNoUnknown] = None


class DDoSIncidentData(BaseModel):
    """Structured data for DDoS incidents"""
    affected_service: str = Field(..., description="What service is being attacked?")
    attack_type: str = Field(default="", description="Type of DDoS attack if known")
    service_impacted: YesNoUnknown = Field(default=YesNoUnknown.YES, description="Is service currently impacted?")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    attack_volume: Optional[str] = None  # e.g., "100 Gbps"
    source_ips_identified: Optional[YesNoUnknown] = None
    mitigation_active: Optional[YesNoUnknown] = None


class UnauthorizedAccessIncidentData(BaseModel):
    """Structured data for unauthorized access incidents"""
    affected_system: str = Field(..., description="What system was accessed?")
    access_method: str = Field(default="", description="How was access obtained?")
    unauthorized_actions: str = Field(default="", description="What actions were taken?")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    attacker_identified: Optional[YesNoUnknown] = None
    data_modified: Optional[YesNoUnknown] = None
    persistence_established: Optional[YesNoUnknown] = None


class IncidentState(BaseModel):
    """Main incident object that tracks the entire lifecycle"""
    incident_id: str = Field(..., description="Unique incident identifier")
    incident_type: IncidentType = Field(..., description="Type of incident")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: Literal["intake", "investigation", "containment", "remediation", "closed"] = "intake"

    # Type-specific data
    phishing_data: Optional[PhishingIncidentData] = None
    malware_data: Optional[MalwareIncidentData] = None
    account_compromise_data: Optional[AccountCompromiseIncidentData] = None
    data_breach_data: Optional[DataBreachIncidentData] = None
    ransomware_data: Optional[RansomwareIncidentData] = None
    insider_threat_data: Optional[InsiderThreatIncidentData] = None
    ddos_data: Optional[DDoSIncidentData] = None
    unauthorized_access_data: Optional[UnauthorizedAccessIncidentData] = None

    # AI-generated outputs
    assessment_history: List[Dict] = Field(default_factory=list, description="History of AI assessments")
    current_assessment: Optional[Dict] = None

    # Actions taken
    actions_taken: List[str] = Field(default_factory=list)
    open_risks: List[str] = Field(default_factory=list)
    recommended_followups: List[str] = Field(default_factory=list)


class IncidentCreateRequest(BaseModel):
    """Request to create a new incident"""
    incident_type: IncidentType
    phishing_data: Optional[PhishingIncidentData] = None
    malware_data: Optional[MalwareIncidentData] = None
    account_compromise_data: Optional[AccountCompromiseIncidentData] = None
    data_breach_data: Optional[DataBreachIncidentData] = None
    ransomware_data: Optional[RansomwareIncidentData] = None
    insider_threat_data: Optional[InsiderThreatIncidentData] = None
    ddos_data: Optional[DDoSIncidentData] = None
    unauthorized_access_data: Optional[UnauthorizedAccessIncidentData] = None


class IncidentUpdateRequest(BaseModel):
    """Request to update incident with new information"""
    phishing_data: Optional[PhishingIncidentData] = None
    malware_data: Optional[MalwareIncidentData] = None
    account_compromise_data: Optional[AccountCompromiseIncidentData] = None
    data_breach_data: Optional[DataBreachIncidentData] = None
    ransomware_data: Optional[RansomwareIncidentData] = None
    insider_threat_data: Optional[InsiderThreatIncidentData] = None
    ddos_data: Optional[DDoSIncidentData] = None
    unauthorized_access_data: Optional[UnauthorizedAccessIncidentData] = None
    actions_taken: Optional[List[str]] = None
    status: Optional[str] = None


class AIAssessmentResponse(BaseModel):
    """Structured response from AI assessment"""
    what_we_know: List[str]
    what_we_need: List[str]
    next_steps: List[str]
    containment_actions: Optional[List[str]] = None
    remediation_steps: Optional[List[str]] = None
    risk_notes: Optional[List[str]] = None


class IncidentSummaryExport(BaseModel):
    """Final incident summary for export"""
    incident_id: str
    incident_type: str
    created_at: datetime
    closed_at: Optional[datetime]
    incident_summary: str
    actions_taken: List[str]
    open_risks: List[str]
    recommended_followups: List[str]
    timeline: List[Dict]


class IncidentClassificationRequest(BaseModel):
    """Request to classify raw incident data"""
    raw_data: str = Field(..., description="Raw logs, description, or event data to classify")
    context: Optional[str] = Field(None, description="Additional context about the incident")


class IncidentTypeClassification(BaseModel):
    """Classification result for a single incident type"""
    incident_type: IncidentType
    confidence: float = Field(..., ge=0.0, le=100.0, description="Confidence percentage (0-100)")
    reasoning: str = Field(..., description="Brief explanation of why this type was suggested")
    key_indicators: List[str] = Field(default_factory=list, description="Key indicators found in the data")


class IncidentClassificationResponse(BaseModel):
    """Response containing classification suggestions"""
    primary_classification: IncidentTypeClassification
    alternative_classifications: List[IncidentTypeClassification] = Field(
        default_factory=list,
        description="Other possible incident types, sorted by confidence"
    )
    raw_data_summary: str = Field(..., description="Summary of the analyzed data")
    suggested_next_steps: List[str] = Field(
        default_factory=list,
        description="Immediate steps the analyst should take"
    )
