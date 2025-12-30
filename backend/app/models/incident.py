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
    BEC = "bec"  # Business Email Compromise
    WEB_APPLICATION_ATTACK = "web_application_attack"
    DATA_EXFILTRATION = "data_exfiltration"
    SUPPLY_CHAIN_ATTACK = "supply_chain_attack"
    CLOUD_ACCOUNT_COMPROMISE = "cloud_account_compromise"
    API_SECURITY_BREACH = "api_security_breach"
    CREDENTIAL_STUFFING = "credential_stuffing"
    ZERO_DAY_EXPLOIT = "zero_day_exploit"
    CONTAINER_COMPROMISE = "container_compromise"
    IOT_DEVICE_COMPROMISE = "iot_device_compromise"
    BACKUP_SYSTEM_COMPROMISE = "backup_system_compromise"
    DNS_HIJACKING = "dns_hijacking"
    SAAS_APPLICATION_COMPROMISE = "saas_application_compromise"
    MOBILE_DEVICE_COMPROMISE = "mobile_device_compromise"
    REGULATORY_COMPLIANCE_INCIDENT = "regulatory_compliance_incident"


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


class BECIncidentData(BaseModel):
    """Structured data for Business Email Compromise incidents"""
    compromised_account_email: str = Field(..., description="Email address of compromised account")
    impersonated_executive: Optional[str] = Field(None, description="Name/title of impersonated executive")
    fraudulent_request_type: str = Field(..., description="Type of fraudulent request (wire transfer, gift cards, etc.)")
    target_recipient_email: str = Field(..., description="Who received the fraudulent email?")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    financial_loss_occurred: Optional[YesNoUnknown] = None
    transaction_amount: Optional[str] = None
    funds_recovered: Optional[YesNoUnknown] = None
    other_targets_identified: Optional[YesNoUnknown] = None


class WebApplicationAttackIncidentData(BaseModel):
    """Structured data for web application attack incidents"""
    affected_application: str = Field(..., description="Name/URL of affected application")
    attack_type: str = Field(..., description="Type of attack (SQLi, XSS, CSRF, etc.)")
    attack_vector: str = Field(default="", description="How was the attack delivered?")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    successful_exploitation: Optional[YesNoUnknown] = None
    data_accessed: Optional[YesNoUnknown] = None
    waf_bypassed: Optional[YesNoUnknown] = None
    vulnerability_patched: Optional[YesNoUnknown] = None


class DataExfiltrationIncidentData(BaseModel):
    """Structured data for data exfiltration incidents"""
    affected_system: str = Field(..., description="System from which data was exfiltrated")
    data_classification: str = Field(..., description="Classification of exfiltrated data (public, internal, confidential, etc.)")
    estimated_data_volume: str = Field(default="", description="Estimated volume of data exfiltrated")
    exfiltration_method: str = Field(..., description="Method used for exfiltration")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    exfiltration_destination: Optional[str] = None
    insider_involvement: Optional[YesNoUnknown] = None
    encryption_used: Optional[YesNoUnknown] = None
    ongoing_exfiltration: Optional[YesNoUnknown] = None


class SupplyChainAttackIncidentData(BaseModel):
    """Structured data for supply chain attack incidents"""
    affected_vendor: str = Field(..., description="Name of affected vendor/supplier")
    compromised_component: str = Field(..., description="Compromised software/hardware component")
    attack_vector: str = Field(..., description="How was the supply chain compromised?")
    internal_systems_affected: YesNoUnknown = Field(default=YesNoUnknown.UNKNOWN, description="Are internal systems affected?")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    malicious_code_identified: Optional[YesNoUnknown] = None
    scope_determined: Optional[YesNoUnknown] = None
    vendor_notified: Optional[YesNoUnknown] = None
    alternative_vendor_identified: Optional[YesNoUnknown] = None


class CloudAccountCompromiseIncidentData(BaseModel):
    """Structured data for cloud account compromise incidents"""
    cloud_provider: str = Field(..., description="Cloud provider (AWS, Azure, GCP, etc.)")
    compromised_account_id: str = Field(..., description="Compromised account/subscription ID")
    account_type: str = Field(..., description="Type of account (root, admin, service account, etc.)")
    unauthorized_actions: str = Field(default="", description="Unauthorized actions observed")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    resources_created: Optional[YesNoUnknown] = None
    data_accessed: Optional[YesNoUnknown] = None
    cryptomining_detected: Optional[YesNoUnknown] = None
    lateral_movement: Optional[YesNoUnknown] = None
    mfa_enabled: Optional[YesNoUnknown] = None


class APISecurityBreachIncidentData(BaseModel):
    """Structured data for API security breach incidents"""
    affected_api: str = Field(..., description="API endpoint or service affected")
    attack_type: str = Field(..., description="Type of API attack (broken auth, excessive data exposure, rate limit abuse, etc.)")
    api_authentication_method: str = Field(default="", description="Authentication method used by API")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    api_keys_compromised: Optional[YesNoUnknown] = None
    data_exfiltrated: Optional[YesNoUnknown] = None
    rate_limiting_bypassed: Optional[YesNoUnknown] = None
    sensitive_endpoints_accessed: Optional[YesNoUnknown] = None


class CredentialStuffingIncidentData(BaseModel):
    """Structured data for credential stuffing attack incidents"""
    affected_service: str = Field(..., description="Service/application targeted")
    attack_volume: str = Field(default="", description="Number of login attempts observed")
    source_ips_count: int = Field(default=0, description="Number of unique source IPs")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    successful_logins: Optional[YesNoUnknown] = None
    accounts_compromised_count: Optional[int] = None
    mfa_prevented_access: Optional[YesNoUnknown] = None
    bot_detection_bypassed: Optional[YesNoUnknown] = None


class ZeroDayExploitIncidentData(BaseModel):
    """Structured data for zero-day exploit incidents"""
    affected_software: str = Field(..., description="Software/system with zero-day vulnerability")
    vulnerability_type: str = Field(..., description="Type of vulnerability (RCE, privilege escalation, etc.)")
    exploit_source: str = Field(default="", description="How was exploit discovered (vendor disclosure, active exploitation, etc.)")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    patch_available: Optional[YesNoUnknown] = None
    exploitation_confirmed: Optional[YesNoUnknown] = None
    threat_actor_identified: Optional[YesNoUnknown] = None
    workaround_implemented: Optional[YesNoUnknown] = None


class ContainerCompromiseIncidentData(BaseModel):
    """Structured data for container/Kubernetes compromise incidents"""
    affected_platform: str = Field(..., description="Container platform (Docker, Kubernetes, etc.)")
    compromised_component: str = Field(..., description="Compromised component (container, pod, node, etc.)")
    namespace_affected: str = Field(default="", description="Kubernetes namespace if applicable")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    container_escape_detected: Optional[YesNoUnknown] = None
    secrets_exposed: Optional[YesNoUnknown] = None
    malicious_image_deployed: Optional[YesNoUnknown] = None
    lateral_movement_to_nodes: Optional[YesNoUnknown] = None


class IoTDeviceCompromiseIncidentData(BaseModel):
    """Structured data for IoT device compromise incidents"""
    device_type: str = Field(..., description="Type of IoT device (camera, sensor, smart device, etc.)")
    device_count: int = Field(..., description="Number of devices compromised")
    compromise_method: str = Field(..., description="How devices were compromised")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    botnet_activity_detected: Optional[YesNoUnknown] = None
    default_credentials_used: Optional[YesNoUnknown] = None
    firmware_backdoor: Optional[YesNoUnknown] = None
    network_segmentation_breached: Optional[YesNoUnknown] = None


class BackupSystemCompromiseIncidentData(BaseModel):
    """Structured data for backup system compromise incidents"""
    backup_system_type: str = Field(..., description="Type of backup system (cloud, tape, disk, hybrid, etc.)")
    backup_scope: str = Field(..., description="What's backed up (files, databases, VMs, entire systems)")
    compromise_method: str = Field(..., description="How were backups compromised")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    backup_integrity_compromised: Optional[YesNoUnknown] = None
    offline_backups_available: Optional[YesNoUnknown] = None
    retention_period_affected: Optional[str] = None  # e.g., "30 days", "90 days"
    ransom_demand_present: Optional[YesNoUnknown] = None
    immutable_backups_compromised: Optional[YesNoUnknown] = None
    backup_encryption_status: Optional[str] = None  # "encrypted", "not_encrypted", "ransomware_encrypted"


class DNSHijackingIncidentData(BaseModel):
    """Structured data for DNS hijacking incidents"""
    affected_domain: str = Field(..., description="Domain name(s) affected by hijacking")
    hijack_type: str = Field(..., description="Type of hijack (registrar takeover, DNS poisoning, subdomain takeover, cache poisoning)")
    dns_provider: str = Field(..., description="DNS hosting provider (Route53, Cloudflare, etc.)")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    registrar_account_compromised: Optional[YesNoUnknown] = None
    dns_records_modified: Optional[YesNoUnknown] = None
    malicious_nameservers: Optional[str] = None  # List of malicious NS records
    certificate_issued: Optional[YesNoUnknown] = None  # For HTTPS hijacking
    email_routing_affected: Optional[YesNoUnknown] = None
    dnssec_enabled: Optional[YesNoUnknown] = None


class SaaSApplicationCompromiseIncidentData(BaseModel):
    """Structured data for SaaS application compromise incidents"""
    saas_platform: str = Field(..., description="SaaS platform (Microsoft 365, Salesforce, Slack, Google Workspace, etc.)")
    compromise_type: str = Field(..., description="Type of compromise (OAuth abuse, admin takeover, consent phishing, etc.)")
    affected_accounts: int = Field(..., description="Number of user accounts affected")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    oauth_token_abuse: Optional[YesNoUnknown] = None
    admin_account_compromised: Optional[YesNoUnknown] = None
    data_exfiltration_detected: Optional[YesNoUnknown] = None
    third_party_app_involved: Optional[YesNoUnknown] = None
    mfa_bypassed: Optional[YesNoUnknown] = None
    malicious_app_permissions: Optional[str] = None  # Permissions granted to malicious app


class MobileDeviceCompromiseIncidentData(BaseModel):
    """Structured data for mobile device compromise incidents"""
    device_type: str = Field(..., description="Type of device (iPhone, Android, iPad, etc.)")
    device_ownership: str = Field(..., description="Ownership (corporate, BYOD, contractor)")
    compromise_method: str = Field(..., description="How device was compromised")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")

    # Investigation findings
    mobile_malware_detected: Optional[YesNoUnknown] = None
    mdm_bypassed: Optional[YesNoUnknown] = None
    device_jailbroken_rooted: Optional[YesNoUnknown] = None
    corporate_data_accessed: Optional[YesNoUnknown] = None
    sim_swap_detected: Optional[YesNoUnknown] = None
    device_location_known: Optional[YesNoUnknown] = None


class RegulatoryComplianceIncidentData(BaseModel):
    """Structured data for regulatory compliance incidents (GDPR, HIPAA, PCI-DSS, etc.)"""
    regulation_type: str = Field(..., description="Regulation violated (GDPR, HIPAA, PCI-DSS, SOX, etc.)")
    affected_data_type: str = Field(..., description="Type of data affected (PII, PHI, payment card data, etc.)")
    affected_records_count: int = Field(..., description="Number of records/individuals affected")
    time_of_detection: datetime = Field(default_factory=datetime.utcnow, description="When was this detected?")
    
    # Investigation findings
    breach_notification_required: Optional[YesNoUnknown] = None
    regulatory_authority_notified: Optional[YesNoUnknown] = None
    affected_individuals_notified: Optional[YesNoUnknown] = None
    data_encryption_enabled: Optional[YesNoUnknown] = None
    third_party_involved: Optional[YesNoUnknown] = None
    compliance_gap_identified: Optional[str] = None
    regulatory_authority: Optional[str] = None
    notification_deadline: Optional[datetime] = None


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
    bec_data: Optional[BECIncidentData] = None
    web_application_attack_data: Optional[WebApplicationAttackIncidentData] = None
    data_exfiltration_data: Optional[DataExfiltrationIncidentData] = None
    supply_chain_attack_data: Optional[SupplyChainAttackIncidentData] = None
    cloud_account_compromise_data: Optional[CloudAccountCompromiseIncidentData] = None
    api_security_breach_data: Optional[APISecurityBreachIncidentData] = None
    credential_stuffing_data: Optional[CredentialStuffingIncidentData] = None
    zero_day_exploit_data: Optional[ZeroDayExploitIncidentData] = None
    container_compromise_data: Optional[ContainerCompromiseIncidentData] = None
    iot_device_compromise_data: Optional[IoTDeviceCompromiseIncidentData] = None
    backup_system_compromise_data: Optional[BackupSystemCompromiseIncidentData] = None
    dns_hijacking_data: Optional[DNSHijackingIncidentData] = None
    saas_application_compromise_data: Optional[SaaSApplicationCompromiseIncidentData] = None
    mobile_device_compromise_data: Optional[MobileDeviceCompromiseIncidentData] = None
    regulatory_compliance_incident_data: Optional[RegulatoryComplianceIncidentData] = None

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
    bec_data: Optional[BECIncidentData] = None
    web_application_attack_data: Optional[WebApplicationAttackIncidentData] = None
    data_exfiltration_data: Optional[DataExfiltrationIncidentData] = None
    supply_chain_attack_data: Optional[SupplyChainAttackIncidentData] = None
    cloud_account_compromise_data: Optional[CloudAccountCompromiseIncidentData] = None
    api_security_breach_data: Optional[APISecurityBreachIncidentData] = None
    credential_stuffing_data: Optional[CredentialStuffingIncidentData] = None
    zero_day_exploit_data: Optional[ZeroDayExploitIncidentData] = None
    container_compromise_data: Optional[ContainerCompromiseIncidentData] = None
    iot_device_compromise_data: Optional[IoTDeviceCompromiseIncidentData] = None
    backup_system_compromise_data: Optional[BackupSystemCompromiseIncidentData] = None
    dns_hijacking_data: Optional[DNSHijackingIncidentData] = None
    saas_application_compromise_data: Optional[SaaSApplicationCompromiseIncidentData] = None
    mobile_device_compromise_data: Optional[MobileDeviceCompromiseIncidentData] = None
    regulatory_compliance_incident_data: Optional[RegulatoryComplianceIncidentData] = None


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
    bec_data: Optional[BECIncidentData] = None
    web_application_attack_data: Optional[WebApplicationAttackIncidentData] = None
    data_exfiltration_data: Optional[DataExfiltrationIncidentData] = None
    supply_chain_attack_data: Optional[SupplyChainAttackIncidentData] = None
    cloud_account_compromise_data: Optional[CloudAccountCompromiseIncidentData] = None
    api_security_breach_data: Optional[APISecurityBreachIncidentData] = None
    credential_stuffing_data: Optional[CredentialStuffingIncidentData] = None
    zero_day_exploit_data: Optional[ZeroDayExploitIncidentData] = None
    container_compromise_data: Optional[ContainerCompromiseIncidentData] = None
    iot_device_compromise_data: Optional[IoTDeviceCompromiseIncidentData] = None
    backup_system_compromise_data: Optional[BackupSystemCompromiseIncidentData] = None
    dns_hijacking_data: Optional[DNSHijackingIncidentData] = None
    saas_application_compromise_data: Optional[SaaSApplicationCompromiseIncidentData] = None
    mobile_device_compromise_data: Optional[MobileDeviceCompromiseIncidentData] = None
    regulatory_compliance_incident_data: Optional[RegulatoryComplianceIncidentData] = None
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
