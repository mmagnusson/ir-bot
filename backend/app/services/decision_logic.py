"""
Decision Logic and Guardrails
Non-AI logic that validates and constrains decisions
"""

from typing import List, Dict, Tuple, Any
import yaml
from pathlib import Path
from ..models.incident import IncidentState, IncidentType, YesNoUnknown


class DecisionGuardrails:
    """Implements non-AI decision logic and safety checks"""

    def __init__(self):
        self.playbook_path = Path(__file__).parent.parent / "data" / "playbooks"
        self.playbooks = {}
        self._load_playbooks()

    def _load_playbooks(self):
        """Load all YAML playbooks"""
        for playbook_file in self.playbook_path.glob("*.yaml"):
            with open(playbook_file, 'r') as f:
                playbook = yaml.safe_load(f)
                self.playbooks[playbook['incident_type']] = playbook

    def get_required_fields(self, incident_type: str, phase: str) -> List[str]:
        """Get required fields for a specific incident type and phase"""
        playbook = self.playbooks.get(incident_type)
        if not playbook:
            return []

        phase_data = playbook.get('phases', {}).get(phase, {})
        return phase_data.get('required_fields', [])

    def validate_incident_data(self, incident: IncidentState) -> Tuple[bool, List[str]]:
        """Validate that incident has required data for current phase"""
        errors = []

        # Get the incident type-specific data
        incident_data = self._get_incident_data(incident)

        if incident_data is None:
            errors.append(f"{incident.incident_type.value} incident missing type-specific data")
            return False, errors

        required = self.get_required_fields(incident.incident_type.value, incident.status)
        data_dict = incident_data.dict()

        for field in required:
            if field not in data_dict or data_dict[field] is None:
                errors.append(f"Missing required field: {field}")

        return len(errors) == 0, errors

    def _get_incident_data(self, incident: IncidentState) -> Any:
        """Get the type-specific data object for an incident"""
        type_mapping = {
            "phishing": incident.phishing_data,
            "malware": incident.malware_data,
            "account_compromise": incident.account_compromise_data,
            "data_breach": incident.data_breach_data,
            "ransomware": incident.ransomware_data,
            "insider_threat": incident.insider_threat_data,
            "ddos": incident.ddos_data,
            "unauthorized_access": incident.unauthorized_access_data,
            "bec": incident.bec_data,
            "web_application_attack": incident.web_application_attack_data,
            "data_exfiltration": incident.data_exfiltration_data,
            "supply_chain_attack": incident.supply_chain_attack_data,
            "cloud_account_compromise": incident.cloud_account_compromise_data,
            "api_security_breach": incident.api_security_breach_data,
            "credential_stuffing": incident.credential_stuffing_data,
            "zero_day_exploit": incident.zero_day_exploit_data,
            "container_compromise": incident.container_compromise_data,
            "iot_device_compromise": incident.iot_device_compromise_data,
            "backup_system_compromise": incident.backup_system_compromise_data,
            "dns_hijacking": incident.dns_hijacking_data,
            "saas_application_compromise": incident.saas_application_compromise_data,
            "mobile_device_compromise": incident.mobile_device_compromise_data,
            "regulatory_compliance_incident": incident.regulatory_compliance_incident_data,
        }
        return type_mapping.get(incident.incident_type.value)

    def assess_risk_level(self, incident: IncidentState) -> str:
        """Determine risk level based on playbook criteria"""
        incident_data = self._get_incident_data(incident)
        if not incident_data:
            return "unknown"

        playbook = self.playbooks.get(incident.incident_type.value, {})
        risk_factors = playbook.get('risk_factors', {})

        # Check critical risk factors (if defined)
        critical_risk = risk_factors.get('critical_risk', [])
        if critical_risk and self._matches_criteria(incident_data, critical_risk):
            return "critical"

        # Check high risk factors
        high_risk = risk_factors.get('high_risk', [])
        if high_risk and self._matches_criteria(incident_data, high_risk):
            return "high"

        # Check medium risk factors
        medium_risk = risk_factors.get('medium_risk', [])
        if medium_risk and self._matches_criteria(incident_data, medium_risk):
            return "medium"

        # Check low risk factors
        low_risk = risk_factors.get('low_risk', [])
        if low_risk and self._matches_criteria(incident_data, low_risk):
            return "low"

        return "medium"  # Default to medium if unclear

    def check_escalation_needed(self, incident: IncidentState) -> Tuple[bool, str]:
        """Check if incident meets escalation criteria"""
        incident_data = self._get_incident_data(incident)
        if not incident_data:
            return False, "none"

        playbook = self.playbooks.get(incident.incident_type.value, {})
        escalation = playbook.get('escalation', {})

        # Check immediate escalation criteria
        immediate_criteria = escalation.get('immediate', [])
        for criterion in immediate_criteria:
            if self._check_text_criterion(incident_data, criterion, incident.incident_type.value):
                return True, "immediate"

        # Check standard escalation criteria
        standard_criteria = escalation.get('standard', [])
        for criterion in standard_criteria:
            if self._check_text_criterion(incident_data, criterion, incident.incident_type.value):
                return True, "standard"

        return False, "none"

    def get_applicable_investigation_steps(self, incident: IncidentState) -> List[str]:
        """Get investigation steps based on incident data"""
        incident_data = self._get_incident_data(incident)
        if not incident_data:
            return []

        playbook = self.playbooks.get(incident.incident_type.value, {})
        investigation = playbook.get('phases', {}).get('investigation', {})
        conditions = investigation.get('conditions', {})

        steps = []

        # Check each condition
        for condition_name, condition_data in conditions.items():
            triggers = condition_data.get('triggers_when', {})
            if self._matches_criteria(incident_data, [triggers]):
                steps.extend(condition_data.get('investigation_steps', []))

        return steps

    def get_applicable_containment_actions(self, incident: IncidentState) -> List[str]:
        """Get containment actions based on incident data"""
        incident_data = self._get_incident_data(incident)
        if not incident_data:
            return []

        playbook = self.playbooks.get(incident.incident_type.value, {})
        containment = playbook.get('phases', {}).get('containment', {})
        conditions = containment.get('conditions', {})

        actions = []

        # Check each condition
        for condition_name, condition_data in conditions.items():
            triggers = condition_data.get('triggers_when', {})
            if self._matches_criteria(incident_data, [triggers]):
                actions.extend(condition_data.get('containment_actions', []))

        return actions

    def get_remediation_steps(self, incident: IncidentState) -> Dict[str, List[str]]:
        """Get standard remediation steps"""
        playbook = self.playbooks.get(incident.incident_type.value)
        if not playbook:
            return {}

        remediation = playbook.get('phases', {}).get('remediation', {})

        result = {
            'standard_steps': remediation.get('standard_steps', [])
        }

        # Add optional remediation sections if they exist
        if 'user_education' in remediation:
            result['user_education'] = remediation.get('user_education', [])
        if 'verification_steps' in remediation:
            result['verification_steps'] = remediation.get('verification_steps', [])
        if 'recovery_priority' in remediation:
            result['recovery_priority'] = remediation.get('recovery_priority', [])

        return result

    def _matches_criteria(self, data: Any, criteria_list: List) -> bool:
        """Check if data matches any criteria in the list"""
        data_dict = data.dict()

        for criteria in criteria_list:
            if isinstance(criteria, dict):
                match = True
                for field, expected_value in criteria.items():
                    actual_value = data_dict.get(field)

                    # Handle YesNoUnknown enum
                    if hasattr(actual_value, 'value'):
                        actual_value = actual_value.value

                    if actual_value != expected_value:
                        match = False
                        break

                if match:
                    return True

        return False

    def _check_text_criterion(self, data: Any, criterion: str, incident_type: str) -> bool:
        """Check text-based criteria (for escalation)"""
        criterion_lower = criterion.lower()
        data_dict = data.dict()

        # Generic keyword matching - looks for field names and values in the criterion
        # This is a simple implementation; production might use more sophisticated matching

        # Try to match keywords in the criterion with data fields
        for field, value in data_dict.items():
            # Handle enum values
            if hasattr(value, 'value'):
                value = value.value

            # Check if field name appears in criterion
            if isinstance(value, str) and field.replace('_', ' ') in criterion_lower:
                # Check if the value matches what's expected
                if value.lower() in criterion_lower or str(value).lower() in criterion_lower:
                    return True
            elif isinstance(value, bool):
                # For boolean fields, check if they're mentioned and true
                if field.replace('_', ' ') in criterion_lower and value:
                    return True
            elif value == "yes" or value == YesNoUnknown.YES:
                # If a yes/no field is yes and mentioned in criterion
                if field.replace('_', ' ') in criterion_lower:
                    return True

        # Fallback to specific pattern matching for common escalation criteria
        # Phishing-specific
        if incident_type == "phishing":
            if "account compromise" in criterion_lower and "active" in criterion_lower:
                return (data_dict.get('credential_submission_confirmed') == YesNoUnknown.YES and
                        data_dict.get('suspicious_signins_observed') == YesNoUnknown.YES)
            if "malware execution" in criterion_lower:
                return data_dict.get('attachment_opened') == YesNoUnknown.YES

        return False

    def validate_ai_recommendations(self, recommendations: List[str], incident: IncidentState) -> Tuple[List[str], List[str]]:
        """Validate AI recommendations against guardrails"""
        approved = []
        rejected = []

        playbook_steps = self.get_applicable_investigation_steps(incident)
        playbook_actions = self.get_applicable_containment_actions(incident)

        valid_actions = playbook_steps + playbook_actions

        for recommendation in recommendations:
            # Check if recommendation is broadly similar to playbook actions
            # This is a simple implementation - production would use better matching
            if any(self._similar_action(recommendation, valid) for valid in valid_actions):
                approved.append(recommendation)
            else:
                # Flag for manual review
                rejected.append(f"{recommendation} [REQUIRES MANUAL REVIEW]")

        return approved, rejected

    def _similar_action(self, ai_action: str, playbook_action: str) -> bool:
        """Check if AI action is similar to playbook action"""
        # Simple keyword matching - production would use better NLP
        ai_keywords = set(ai_action.lower().split())
        playbook_keywords = set(playbook_action.lower().split())

        # If they share significant keywords, consider them similar
        overlap = ai_keywords & playbook_keywords
        return len(overlap) >= 2
