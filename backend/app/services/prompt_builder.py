"""
Prompt Builder Service
Constructs controlled, structured prompts for AI interaction
"""

from typing import Dict, List
import json
from ..models.incident import (
    IncidentState,
    PhishingIncidentData,
    MalwareIncidentData,
    AccountCompromiseIncidentData,
    DataBreachIncidentData,
    RansomwareIncidentData,
    InsiderThreatIncidentData,
    DDoSIncidentData,
    UnauthorizedAccessIncidentData,
    YesNoUnknown
)


class PromptBuilder:
    """Builds controlled prompts to prevent hallucinations"""

    @staticmethod
    def get_system_prompt() -> str:
        """Fixed system prompt for all AI interactions"""
        return """You are an Incident Response procedural assistant.

Your role is to:
1. Provide guidance based ONLY on the supplied incident data
2. Follow established IR best practices
3. Explicitly state what information is missing
4. Never speculate or invent facts
5. Provide calm, structured, checklist-based guidance

If information is missing or unknown, you MUST state "This cannot be determined without [specific information]."

Your outputs must be structured and actionable. Focus on:
- What we know (facts from the incident data)
- What we don't know (gaps in information)
- What to investigate next (specific, actionable steps)
- Containment actions (when appropriate)
- Remediation steps (when appropriate)
- Risk considerations (based on known facts)

Do not make assumptions. Do not recommend actions without sufficient information.
"""

    @staticmethod
    def build_incident_context(incident: IncidentState) -> Dict:
        """Convert incident state to structured JSON for AI"""
        context = {
            "incident_id": incident.incident_id,
            "incident_type": incident.incident_type,
            "status": incident.status,
            "created_at": incident.created_at.isoformat(),
        }

        # Add type-specific details based on incident type
        if incident.incident_type == "phishing" and incident.phishing_data:
            context["incident_details"] = PromptBuilder._build_phishing_context(
                incident.phishing_data
            )
        elif incident.incident_type == "malware" and incident.malware_data:
            context["incident_details"] = PromptBuilder._build_malware_context(
                incident.malware_data
            )
        elif incident.incident_type == "account_compromise" and incident.account_compromise_data:
            context["incident_details"] = PromptBuilder._build_account_compromise_context(
                incident.account_compromise_data
            )
        elif incident.incident_type == "data_breach" and incident.data_breach_data:
            context["incident_details"] = PromptBuilder._build_data_breach_context(
                incident.data_breach_data
            )
        elif incident.incident_type == "ransomware" and incident.ransomware_data:
            context["incident_details"] = PromptBuilder._build_ransomware_context(
                incident.ransomware_data
            )
        elif incident.incident_type == "insider_threat" and incident.insider_threat_data:
            context["incident_details"] = PromptBuilder._build_insider_threat_context(
                incident.insider_threat_data
            )
        elif incident.incident_type == "ddos" and incident.ddos_data:
            context["incident_details"] = PromptBuilder._build_ddos_context(
                incident.ddos_data
            )
        elif incident.incident_type == "unauthorized_access" and incident.unauthorized_access_data:
            context["incident_details"] = PromptBuilder._build_unauthorized_access_context(
                incident.unauthorized_access_data
            )

        if incident.actions_taken:
            context["actions_taken"] = incident.actions_taken

        return context

    @staticmethod
    def _build_phishing_context(data: PhishingIncidentData) -> Dict:
        """Build structured phishing incident context"""
        context = {
            "reporting_user": data.reporting_user_email,
            "time_of_report": data.time_of_report.isoformat(),
            "user_interactions": {
                "clicked_link": data.user_clicked.value,
                "opened_attachment": data.attachment_opened.value,
                "entered_credentials": data.credentials_entered.value,
            },
            "evidence_available": {
                "email_headers": data.headers_available,
            },
            "observables": {}
        }

        # Add observables if present
        if data.observables.url:
            context["observables"]["url"] = data.observables.url
        if data.observables.hash:
            context["observables"]["hash"] = data.observables.hash
        if data.observables.sender_email:
            context["observables"]["sender_email"] = data.observables.sender_email

        # Add investigation findings if available
        if data.credential_submission_confirmed:
            context["investigation_findings"] = {
                "credentials_confirmed": data.credential_submission_confirmed.value,
            }
            if data.suspicious_signins_observed:
                context["investigation_findings"]["suspicious_signins"] = (
                    data.suspicious_signins_observed.value
                )
            if data.mfa_enabled:
                context["investigation_findings"]["mfa_enabled"] = data.mfa_enabled.value
            if data.other_affected_users:
                context["investigation_findings"]["other_affected_users"] = (
                    data.other_affected_users.value
                )

        return context

    @staticmethod
    def _build_malware_context(data: MalwareIncidentData) -> Dict:
        """Build structured malware incident context"""
        context = {
            "reporting_user": data.reporting_user_email,
            "time_of_detection": data.time_of_detection.isoformat(),
            "file_executed": data.file_executed.value if data.file_executed else "unknown",
            "suspicious_behavior": data.suspicious_behavior,
            "observables": {}
        }

        if data.observables.url:
            context["observables"]["url"] = data.observables.url
        if data.observables.hash:
            context["observables"]["hash"] = data.observables.hash

        # Investigation findings
        if data.malware_type:
            context["malware_type"] = data.malware_type
        if data.c2_communication_detected:
            context["c2_communication_detected"] = data.c2_communication_detected.value
        if data.data_exfiltration_suspected:
            context["data_exfiltration_suspected"] = data.data_exfiltration_suspected.value
        if data.other_infected_systems:
            context["other_infected_systems"] = data.other_infected_systems.value

        return context

    @staticmethod
    def _build_account_compromise_context(data: AccountCompromiseIncidentData) -> Dict:
        """Build structured account compromise incident context"""
        context = {
            "affected_user": data.affected_user_email,
            "time_of_detection": data.time_of_detection.isoformat(),
            "unauthorized_access_detected": data.unauthorized_access_detected.value if data.unauthorized_access_detected else "unknown",
            "suspicious_activities": data.suspicious_activities,
        }

        # Investigation findings
        if data.access_method:
            context["access_method"] = data.access_method
        if data.mfa_bypassed:
            context["mfa_bypassed"] = data.mfa_bypassed.value
        if data.data_accessed:
            context["data_accessed"] = data.data_accessed.value
        if data.actions_taken_by_attacker:
            context["actions_taken_by_attacker"] = data.actions_taken_by_attacker

        return context

    @staticmethod
    def _build_data_breach_context(data: DataBreachIncidentData) -> Dict:
        """Build structured data breach incident context"""
        context = {
            "data_type_affected": data.data_type_affected,
            "time_of_detection": data.time_of_detection.isoformat(),
            "breach_source": data.breach_source,
        }

        if data.number_of_records:
            context["number_of_records"] = data.number_of_records

        # Investigation findings
        if data.exfiltration_confirmed:
            context["exfiltration_confirmed"] = data.exfiltration_confirmed.value
        if data.attacker_identified:
            context["attacker_identified"] = data.attacker_identified.value
        if data.regulatory_notification_required:
            context["regulatory_notification_required"] = data.regulatory_notification_required.value

        return context

    @staticmethod
    def _build_ransomware_context(data: RansomwareIncidentData) -> Dict:
        """Build structured ransomware incident context"""
        context = {
            "reporting_user": data.reporting_user_email,
            "time_of_detection": data.time_of_detection.isoformat(),
            "files_encrypted": data.files_encrypted.value if data.files_encrypted else "unknown",
            "ransom_note_present": data.ransom_note_present.value if data.ransom_note_present else "unknown",
        }

        if data.ransom_amount:
            context["ransom_amount"] = data.ransom_amount

        # Investigation findings
        if data.ransomware_variant:
            context["ransomware_variant"] = data.ransomware_variant
        if data.spread_to_other_systems:
            context["spread_to_other_systems"] = data.spread_to_other_systems.value
        if data.backups_affected:
            context["backups_affected"] = data.backups_affected.value

        return context

    @staticmethod
    def _build_insider_threat_context(data: InsiderThreatIncidentData) -> Dict:
        """Build structured insider threat incident context"""
        context = {
            "suspect_user": data.suspect_user_email,
            "time_of_detection": data.time_of_detection.isoformat(),
            "suspicious_activity": data.suspicious_activity,
            "data_access_anomaly": data.data_access_anomaly.value if data.data_access_anomaly else "unknown",
        }

        # Investigation findings
        if data.intent_determined:
            context["intent_determined"] = data.intent_determined
        if data.data_exfiltrated:
            context["data_exfiltrated"] = data.data_exfiltrated.value
        if data.hr_notified:
            context["hr_notified"] = data.hr_notified.value

        return context

    @staticmethod
    def _build_ddos_context(data: DDoSIncidentData) -> Dict:
        """Build structured DDoS incident context"""
        context = {
            "affected_service": data.affected_service,
            "time_of_detection": data.time_of_detection.isoformat(),
            "attack_type": data.attack_type,
            "service_impacted": data.service_impacted.value if data.service_impacted else "unknown",
        }

        # Investigation findings
        if data.attack_volume:
            context["attack_volume"] = data.attack_volume
        if data.source_ips_identified:
            context["source_ips_identified"] = data.source_ips_identified.value
        if data.mitigation_active:
            context["mitigation_active"] = data.mitigation_active.value

        return context

    @staticmethod
    def _build_unauthorized_access_context(data: UnauthorizedAccessIncidentData) -> Dict:
        """Build structured unauthorized access incident context"""
        context = {
            "affected_system": data.affected_system,
            "time_of_detection": data.time_of_detection.isoformat(),
            "access_method": data.access_method,
            "unauthorized_actions": data.unauthorized_actions,
        }

        # Investigation findings
        if data.attacker_identified:
            context["attacker_identified"] = data.attacker_identified.value
        if data.data_modified:
            context["data_modified"] = data.data_modified.value
        if data.persistence_established:
            context["persistence_established"] = data.persistence_established.value

        return context

    @staticmethod
    def build_initial_assessment_prompt(incident: IncidentState) -> str:
        """Build prompt for initial incident assessment"""
        context = PromptBuilder.build_incident_context(incident)

        prompt = f"""Based on this incident state, provide an initial assessment:

{json.dumps(context, indent=2)}

Provide your response in the following structured format:

1. WHAT WE KNOW:
   - List only the confirmed facts from the incident data
   - Be specific and factual

2. WHAT WE NEED TO DETERMINE:
   - List information gaps that must be filled
   - Prioritize by importance

3. RECOMMENDED NEXT INVESTIGATIVE STEPS:
   - Provide specific, actionable investigation steps
   - Number them in order of priority
   - Each step should be clear and achievable

Do not provide containment or remediation guidance yet. Focus only on understanding the current state and next investigative steps.
"""
        return prompt

    @staticmethod
    def build_containment_prompt(incident: IncidentState) -> str:
        """Build prompt for containment and remediation guidance"""
        context = PromptBuilder.build_incident_context(incident)

        prompt = f"""Based on the current incident state and investigation findings, provide containment and remediation guidance:

{json.dumps(context, indent=2)}

Provide your response in the following structured format:

1. CONTAINMENT ACTIONS:
   - List immediate actions to prevent further damage
   - Be specific and prioritize by urgency
   - Only recommend actions supported by the evidence

2. REMEDIATION STEPS:
   - List steps to recover and clean up
   - Include preventive measures
   - Consider organizational impact

3. RISK NOTES:
   - Identify residual risks based on known facts
   - Highlight areas requiring follow-up
   - Note any escalation criteria met

Only recommend actions that are justified by the incident data. If critical information is missing, state what is needed before taking action.
"""
        return prompt

    @staticmethod
    def build_summary_prompt(incident: IncidentState) -> str:
        """Build prompt for final incident summary"""
        context = PromptBuilder.build_incident_context(incident)

        prompt = f"""Generate a concise incident summary for documentation:

{json.dumps(context, indent=2)}

Provide:
1. A 2-3 sentence summary of what happened
2. Key findings from the investigation
3. Actions taken (from the incident data)
4. Any open risks or recommended follow-ups

Keep it factual, concise, and professional. This will be used for formal documentation.
"""
        return prompt

    @staticmethod
    def parse_ai_response(response: str, response_type: str) -> Dict:
        """Parse AI response into structured format"""
        # This is a simple parser - in production, you might want more robust parsing
        parsed = {
            "raw_response": response,
            "response_type": response_type,
        }

        # Extract structured sections based on response type
        if response_type == "initial_assessment":
            parsed["what_we_know"] = PromptBuilder._extract_section(
                response, "WHAT WE KNOW"
            )
            parsed["what_we_need"] = PromptBuilder._extract_section(
                response, "WHAT WE NEED TO DETERMINE"
            )
            parsed["next_steps"] = PromptBuilder._extract_section(
                response, "RECOMMENDED NEXT INVESTIGATIVE STEPS"
            )

        elif response_type == "containment":
            parsed["containment_actions"] = PromptBuilder._extract_section(
                response, "CONTAINMENT ACTIONS"
            )
            parsed["remediation_steps"] = PromptBuilder._extract_section(
                response, "REMEDIATION STEPS"
            )
            parsed["risk_notes"] = PromptBuilder._extract_section(
                response, "RISK NOTES"
            )

        return parsed

    @staticmethod
    def _extract_section(text: str, section_name: str) -> List[str]:
        """Extract bullet points or numbered items from a section"""
        lines = text.split('\n')
        in_section = False
        items = []

        for line in lines:
            if section_name in line.upper():
                in_section = True
                continue

            if in_section:
                # Check if we've hit another section header
                if line.strip() and line.strip()[0].isdigit() and '.' in line[:3]:
                    if any(keyword in line.upper() for keyword in ['WHAT', 'CONTAINMENT', 'REMEDIATION', 'RISK']):
                        break

                # Extract bullet points or numbered items
                stripped = line.strip()
                if stripped and (stripped.startswith('-') or stripped.startswith('*') or
                               (stripped[0].isdigit() and '.' in stripped[:4])):
                    # Remove bullet/number prefix
                    item = stripped.lstrip('0123456789.-* ').strip()
                    if item:
                        items.append(item)

        return items
