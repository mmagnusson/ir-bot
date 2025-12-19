from typing import Optional, Dict, List, Literal, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import uuid


class IncidentType(str, Enum):
    PHISHING = "phishing"
    MALWARE = "malware"
    ACCOUNT_COMPROMISE = "account_compromise"
    DATA_BREACH = "data_breach"
    RANSOMWARE = "ransomware"
    INSIDER_THREAT = "insider_threat"
    DDOS = "ddos"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


# NEW: Playbook execution enums and models

class StepStatus(str, Enum):
    """Status of a playbook step"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class EvidenceType(str, Enum):
    """Types of evidence that can be collected"""
    TEXT = "text"
    FILE = "file"
    BOOLEAN = "boolean"
    NUMBER = "number"
    TIMESTAMP = "timestamp"
    URL = "url"


class EvidenceItem(BaseModel):
    """Single piece of evidence collected for a step"""
    evidence_type: EvidenceType
    name: str
    value: Any
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    collected_by: Optional[str] = None  # Username or role


class StepExecution(BaseModel):
    """Tracks execution of a single playbook step"""
    step_id: str
    status: StepStatus = StepStatus.NOT_STARTED
    assigned_to: Optional[str] = None  # Role name
    assigned_user: Optional[str] = None  # Actual username
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    evidence: List[EvidenceItem] = Field(default_factory=list)
    notes: Optional[str] = None
    blocked_reason: Optional[str] = None

    @property
    def time_spent_minutes(self) -> Optional[float]:
        """Calculate time spent on this step"""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() / 60
        return None


class PhaseExecution(BaseModel):
    """Tracks execution of a phase with all its steps"""
    phase_name: str
    status: Literal["not_started", "in_progress", "completed"] = "not_started"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    steps: Dict[str, StepExecution] = Field(default_factory=dict)
    signed_off_by: Optional[str] = None
    signed_off_at: Optional[datetime] = None
    sla_target_completion: Optional[datetime] = None

    @property
    def completion_percentage(self) -> float:
        """Calculate percentage of completed steps"""
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps.values() if s.status == StepStatus.COMPLETED)
        return (completed / len(self.steps)) * 100

    @property
    def is_sla_breached(self) -> bool:
        """Check if SLA has been breached"""
        if self.sla_target_completion and not self.completed_at:
            return datetime.utcnow() > self.sla_target_completion
        return False


class RoleAssignment(BaseModel):
    """Assignment of a user to a role"""
    role_name: str
    assigned_user: Optional[str] = None  # Username or email
    assigned_at: Optional[datetime] = None
    required: bool = False


class PhaseHandoff(BaseModel):
    """Record of a phase transition handoff"""
    from_phase: str
    to_phase: str
    from_role: str
    to_role: str
    initiated_by: str
    initiated_at: datetime = Field(default_factory=datetime.utcnow)
    signed_off_by: Optional[str] = None
    signed_off_at: Optional[datetime] = None
    handoff_notes: Optional[str] = None
    checklist_completion_at_handoff: float  # Percentage
    requirements_met: bool = False
    requirements_check: Dict[str, bool] = Field(default_factory=dict)


class NotificationLog(BaseModel):
    """Log of notifications sent"""
    notification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trigger: str
    message: str
    notified_roles: List[str]
    notified_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_by: List[str] = Field(default_factory=list)


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
    estimated_records: int = Field(..., description="Estimated number of records affected")
    breach_method: str = Field(..., description="How was the data breached?")
    time_of_discovery: datetime = Field(..., description="When was the breach discovered?")
    breach_source: Optional[str] = Field(None, description="Additional details about the breach source")

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

    # Actions taken
    actions_taken: List[str] = Field(default_factory=list)
    open_risks: List[str] = Field(default_factory=list)
    recommended_followups: List[str] = Field(default_factory=list)

    # NEW: Playbook execution tracking
    role_assignments: Dict[str, RoleAssignment] = Field(default_factory=dict)
    phase_executions: Dict[str, PhaseExecution] = Field(default_factory=dict)
    handoff_history: List[PhaseHandoff] = Field(default_factory=list)
    notifications: List[NotificationLog] = Field(default_factory=list)


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


# NEW: Request/Response models for playbook execution

class StepUpdateRequest(BaseModel):
    """Request to update a step's status and evidence"""
    step_id: str
    status: Optional[StepStatus] = None
    assigned_user: Optional[str] = None
    notes: Optional[str] = None
    blocked_reason: Optional[str] = None
    evidence: Optional[List[EvidenceItem]] = None


class RoleAssignmentRequest(BaseModel):
    """Request to assign a user to a role"""
    role_name: str
    assigned_user: str


class PhaseHandoffRequest(BaseModel):
    """Request to initiate a phase handoff"""
    to_phase: str
    handoff_notes: Optional[str] = None


class PhaseSignOffRequest(BaseModel):
    """Request to sign off on a handoff"""
    signed_off_by: str
    notes: Optional[str] = None
