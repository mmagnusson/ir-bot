"""
PlaybookEngine Service

Core orchestration engine for playbook-driven incident response.
Handles step execution, dependencies, role assignments, handoffs, and notifications.
"""

from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import yaml
import uuid

from ..models.incident import (
    IncidentState, StepExecution, PhaseExecution, PhaseHandoff,
    RoleAssignment, NotificationLog, StepStatus, EvidenceItem,
    StepUpdateRequest
)


class PlaybookEngine:
    """Core engine for playbook-driven incident response"""

    def __init__(self):
        self.playbook_path = Path(__file__).parent.parent / "data" / "playbooks"
        self.playbooks: Dict[str, Dict] = {}
        self._load_playbooks()

    def _load_playbooks(self):
        """Load all YAML playbooks from the playbooks directory"""
        if not self.playbook_path.exists():
            print(f"Warning: Playbook directory not found at {self.playbook_path}")
            return

        for playbook_file in self.playbook_path.glob("*.yaml"):
            try:
                with open(playbook_file, 'r') as f:
                    playbook = yaml.safe_load(f)
                    if playbook and 'incident_type' in playbook:
                        self.playbooks[playbook['incident_type']] = playbook
            except Exception as e:
                print(f"Error loading playbook {playbook_file}: {e}")

    def get_phases_for_incident(self, incident: IncidentState) -> Dict:
        """
        Get all phases with metadata for an incident

        Returns dictionary of phase_name -> phase_info including:
        - description
        - primary_role
        - sla
        - execution status
        """
        playbook = self.playbooks.get(incident.incident_type.value)
        if not playbook:
            return {}

        phases = {}
        for phase_name, phase_data in playbook.get('phases', {}).items():
            # Initialize phase execution if not exists
            if phase_name not in incident.phase_executions:
                status = "in_progress" if phase_name == incident.status else "not_started"
                incident.phase_executions[phase_name] = PhaseExecution(
                    phase_name=phase_name,
                    status=status
                )

            phases[phase_name] = {
                "description": phase_data.get('description'),
                "primary_role": phase_data.get('primary_role'),
                "sla": phase_data.get('sla'),
                "execution": incident.phase_executions[phase_name]
            }

        return phases

    def get_phase_steps(self, incident: IncidentState, phase_name: str) -> List[Dict]:
        """
        Get all steps for a phase with execution status

        Returns list of step dictionaries with:
        - Step metadata from playbook
        - Execution status
        - Whether step applies based on conditions
        """
        playbook = self.playbooks.get(incident.incident_type.value)
        if not playbook:
            return []

        phase = playbook.get('phases', {}).get(phase_name)
        if not phase:
            return []

        # Initialize phase execution if needed
        if phase_name not in incident.phase_executions:
            incident.phase_executions[phase_name] = PhaseExecution(phase_name=phase_name)

        phase_exec = incident.phase_executions[phase_name]
        steps = []

        for step in phase.get('checklist', []):
            step_id = step.get('id', step.get('step'))  # Use id or fall back to step text
            if not step_id:
                continue

            # Initialize step execution if needed
            if step_id not in phase_exec.steps:
                phase_exec.steps[step_id] = StepExecution(
                    step_id=step_id,
                    assigned_to=step.get('assigned_to')
                )

            # Check if step applies based on conditions
            applies = self._check_step_conditions(incident, step.get('conditions'))

            step_info = {
                "id": step_id,
                "step": step.get('step', step_id),
                "description": step.get('description'),
                "assigned_to": step.get('assigned_to'),
                "estimated_time_minutes": step.get('estimated_time_minutes'),
                "parallel_group": step.get('parallel_group'),
                "dependencies": step.get('dependencies', []),
                "critical": step.get('critical', False),
                "evidence_required": step.get('evidence_required', []),
                "applies": applies,
                "execution": phase_exec.steps[step_id]
            }

            steps.append(step_info)

        return steps

    def _check_step_conditions(self, incident: IncidentState, conditions: Optional[Dict]) -> bool:
        """
        Check if step conditions are met

        Conditions format:
        {
            "triggers_when": {
                "field_name": "expected_value"
            }
        }
        """
        if not conditions:
            return True

        triggers = conditions.get('triggers_when', {})
        if not triggers:
            return True

        incident_data = self._get_incident_data(incident)
        if not incident_data:
            return False

        # Convert to dict for checking
        try:
            data_dict = incident_data.model_dump() if hasattr(incident_data, 'model_dump') else incident_data.dict()
        except:
            return False

        # Check all trigger conditions
        for field, expected_value in triggers.items():
            actual_value = data_dict.get(field)

            # Handle enum values
            if hasattr(actual_value, 'value'):
                actual_value = actual_value.value

            if actual_value != expected_value:
                return False

        return True

    def _get_incident_data(self, incident: IncidentState):
        """Get incident-specific data object based on incident type"""
        type_mapping = {
            "phishing": incident.phishing_data,
            "malware": incident.malware_data,
            "account_compromise": incident.account_compromise_data,
            "data_breach": incident.data_breach_data,
            "ransomware": incident.ransomware_data,
            "insider_threat": incident.insider_threat_data,
            "ddos": incident.ddos_data,
            "unauthorized_access": incident.unauthorized_access_data,
        }
        return type_mapping.get(incident.incident_type.value)

    def check_step_dependencies(self, incident: IncidentState, step_id: str) -> Tuple[bool, str]:
        """
        Check if step dependencies are met

        Returns (can_start, reason)
        """
        playbook = self.playbooks.get(incident.incident_type.value)
        if not playbook:
            return False, "Playbook not found"

        # Find the step in current phase
        phase = playbook.get('phases', {}).get(incident.status)
        if not phase:
            return False, "Phase not found"

        step = None
        for s in phase.get('checklist', []):
            if s.get('id') == step_id or s.get('step') == step_id:
                step = s
                break

        if not step:
            return False, "Step not found"

        # Check dependencies
        dependencies = step.get('dependencies', [])
        if not dependencies:
            return True, "No dependencies"

        phase_exec = incident.phase_executions.get(incident.status)
        if not phase_exec:
            return False, "Phase execution not initialized"

        for dep_id in dependencies:
            dep_step = phase_exec.steps.get(dep_id)
            if not dep_step or dep_step.status != StepStatus.COMPLETED:
                return False, f"Dependency '{dep_id}' not completed"

        return True, "Dependencies met"

    def start_step(self, incident: IncidentState, step_id: str, assigned_user: str) -> IncidentState:
        """
        Mark a step as started

        Sets status to IN_PROGRESS, records start time and user
        """
        phase_exec = incident.phase_executions.get(incident.status)
        if not phase_exec:
            # Initialize phase if needed
            phase_exec = PhaseExecution(phase_name=incident.status, status="in_progress")
            incident.phase_executions[incident.status] = phase_exec

        # Initialize step if needed
        if step_id not in phase_exec.steps:
            phase_exec.steps[step_id] = StepExecution(step_id=step_id)

        step_exec = phase_exec.steps[step_id]
        step_exec.status = StepStatus.IN_PROGRESS
        step_exec.assigned_user = assigned_user
        step_exec.started_at = datetime.utcnow()

        incident.updated_at = datetime.utcnow()
        return incident

    def update_step(self, incident: IncidentState, request: StepUpdateRequest) -> IncidentState:
        """
        Update step status, notes, and evidence

        Handles status changes, evidence collection, notes, and blocked reasons
        """
        phase_exec = incident.phase_executions.get(incident.status)
        if not phase_exec:
            raise ValueError(f"Phase execution not found for {incident.status}")

        step_exec = phase_exec.steps.get(request.step_id)
        if not step_exec:
            raise ValueError(f"Step {request.step_id} not found")

        # Update status
        if request.status:
            step_exec.status = request.status
            if request.status == StepStatus.COMPLETED:
                step_exec.completed_at = datetime.utcnow()

        # Update assignment
        if request.assigned_user:
            step_exec.assigned_user = request.assigned_user

        # Update notes
        if request.notes:
            step_exec.notes = request.notes

        # Update blocked reason
        if request.blocked_reason:
            step_exec.blocked_reason = request.blocked_reason

        # Add evidence
        if request.evidence:
            step_exec.evidence.extend(request.evidence)

        incident.updated_at = datetime.utcnow()
        return incident

    def add_evidence_to_step(self, incident: IncidentState, step_id: str, evidence: List[EvidenceItem]) -> IncidentState:
        """Add evidence items to a step"""
        phase_exec = incident.phase_executions.get(incident.status)
        if not phase_exec:
            raise ValueError(f"Phase execution not found for {incident.status}")

        step_exec = phase_exec.steps.get(step_id)
        if not step_exec:
            raise ValueError(f"Step {step_id} not found")

        step_exec.evidence.extend(evidence)
        incident.updated_at = datetime.utcnow()
        return incident

    def assign_role(self, incident: IncidentState, role_name: str, assigned_user: str) -> IncidentState:
        """
        Assign a user to a role

        Creates or updates role assignment with timestamp
        """
        if role_name not in incident.role_assignments:
            # Load required status from playbook if available
            playbook = self.playbooks.get(incident.incident_type.value)
            required = False
            if playbook and 'roles' in playbook:
                role_def = playbook['roles'].get(role_name, {})
                required = role_def.get('required', False)

            incident.role_assignments[role_name] = RoleAssignment(
                role_name=role_name,
                required=required
            )

        incident.role_assignments[role_name].assigned_user = assigned_user
        incident.role_assignments[role_name].assigned_at = datetime.utcnow()
        incident.updated_at = datetime.utcnow()

        return incident

    def check_handoff_requirements(self, incident: IncidentState, to_phase: str) -> Tuple[bool, Dict]:
        """
        Check if handoff requirements are met

        Returns (requirements_met, requirements_detail)

        Requirements can include:
        - all_required_fields_complete
        - checklist_completion_threshold
        - sign_off_required
        """
        playbook = self.playbooks.get(incident.incident_type.value)
        if not playbook:
            return False, {"error": "Playbook not found"}

        current_phase = playbook.get('phases', {}).get(incident.status)
        if not current_phase:
            return False, {"error": "Current phase not found"}

        requirements = current_phase.get('handoff_requirements', {})
        phase_exec = incident.phase_executions.get(incident.status)

        checks = {}
        all_met = True

        # Check required fields
        if requirements.get('all_required_fields_complete'):
            required_fields = current_phase.get('required_fields', [])
            incident_data = self._get_incident_data(incident)
            if incident_data:
                try:
                    data_dict = incident_data.model_dump() if hasattr(incident_data, 'model_dump') else incident_data.dict()
                    for field in required_fields:
                        if field not in data_dict or data_dict[field] is None:
                            checks[f"field_{field}"] = False
                            all_met = False
                        else:
                            checks[f"field_{field}"] = True
                except:
                    checks['required_fields'] = False
                    all_met = False

        # Check checklist completion threshold
        if requirements.get('checklist_completion_threshold'):
            threshold = requirements['checklist_completion_threshold']
            if phase_exec:
                completion = phase_exec.completion_percentage
                checks['checklist_completion'] = completion >= threshold
                checks['completion_percentage'] = completion
                if completion < threshold:
                    all_met = False
            else:
                checks['checklist_completion'] = False
                all_met = False

        # Check sign-off required
        if requirements.get('sign_off_required'):
            if not phase_exec or not phase_exec.signed_off_by:
                checks['sign_off'] = False
                all_met = False
            else:
                checks['sign_off'] = True

        return all_met, checks

    def initiate_handoff(self, incident: IncidentState, to_phase: str, initiated_by: str, notes: Optional[str]) -> IncidentState:
        """
        Initiate a phase handoff

        Creates handoff record but does not transition until signed off
        """
        playbook = self.playbooks.get(incident.incident_type.value)
        if not playbook:
            raise ValueError("Playbook not found")

        current_phase = playbook.get('phases', {}).get(incident.status)
        next_phase = playbook.get('phases', {}).get(to_phase)

        if not current_phase or not next_phase:
            raise ValueError("Phase not found in playbook")

        phase_exec = incident.phase_executions.get(incident.status)
        completion = phase_exec.completion_percentage if phase_exec else 0

        handoff = PhaseHandoff(
            from_phase=incident.status,
            to_phase=to_phase,
            from_role=current_phase.get('primary_role', 'unknown'),
            to_role=next_phase.get('primary_role', 'unknown'),
            initiated_by=initiated_by,
            handoff_notes=notes,
            checklist_completion_at_handoff=completion,
            requirements_met=True
        )

        incident.handoff_history.append(handoff)
        incident.updated_at = datetime.utcnow()

        return incident

    def sign_off_handoff(self, incident: IncidentState, signed_off_by: str, notes: Optional[str]) -> IncidentState:
        """
        Sign off on the latest handoff and transition phase

        Completes current phase and starts next phase
        """
        if not incident.handoff_history:
            raise ValueError("No handoff to sign off")

        latest_handoff = incident.handoff_history[-1]
        if latest_handoff.signed_off_by:
            raise ValueError("Handoff already signed off")

        # Sign off handoff
        latest_handoff.signed_off_by = signed_off_by
        latest_handoff.signed_off_at = datetime.utcnow()
        if notes:
            latest_handoff.handoff_notes = (latest_handoff.handoff_notes or "") + f"\nSign-off notes: {notes}"

        # Complete current phase
        phase_exec = incident.phase_executions.get(incident.status)
        if phase_exec:
            phase_exec.status = "completed"
            phase_exec.completed_at = datetime.utcnow()
            phase_exec.signed_off_by = signed_off_by
            phase_exec.signed_off_at = datetime.utcnow()

        # Transition to next phase
        incident.status = latest_handoff.to_phase

        # Initialize next phase
        if latest_handoff.to_phase not in incident.phase_executions:
            incident.phase_executions[latest_handoff.to_phase] = PhaseExecution(
                phase_name=latest_handoff.to_phase,
                status="in_progress",
                started_at=datetime.utcnow()
            )
        else:
            incident.phase_executions[latest_handoff.to_phase].status = "in_progress"
            incident.phase_executions[latest_handoff.to_phase].started_at = datetime.utcnow()

        incident.updated_at = datetime.utcnow()
        return incident

    def trigger_notifications(self, incident: IncidentState, trigger_type: str, context: Any):
        """
        Trigger notifications based on playbook rules

        Checks playbook for notification rules matching trigger_type
        and creates notification logs
        """
        playbook = self.playbooks.get(incident.incident_type.value)
        if not playbook:
            return

        phase = playbook.get('phases', {}).get(incident.status)
        if not phase:
            return

        notifications = phase.get('notifications', [])

        for notif in notifications:
            if notif.get('trigger') == trigger_type:
                notification = NotificationLog(
                    notification_id=str(uuid.uuid4()),
                    trigger=trigger_type,
                    message=notif.get('message', f"Notification: {trigger_type}"),
                    notified_roles=notif.get('notify_roles', [])
                )
                incident.notifications.append(notification)

    def build_dashboard(self, incident: IncidentState) -> Dict:
        """
        Build dashboard summary with progress, roles, and SLA status

        Returns comprehensive dashboard data structure
        """
        playbook = self.playbooks.get(incident.incident_type.value)

        dashboard = {
            "incident_id": incident.incident_id,
            "incident_type": incident.incident_type.value,
            "current_phase": incident.status,
            "created_at": incident.created_at.isoformat(),
            "role_assignments": {},
            "phase_progress": {},
            "sla_status": {},
            "pending_handoffs": [],
            "recent_notifications": []
        }

        # Role assignments
        for role_name, assignment in incident.role_assignments.items():
            dashboard["role_assignments"][role_name] = {
                "assigned_user": assignment.assigned_user,
                "assigned_at": assignment.assigned_at.isoformat() if assignment.assigned_at else None,
                "required": assignment.required
            }

        # Phase progress
        for phase_name, phase_exec in incident.phase_executions.items():
            dashboard["phase_progress"][phase_name] = {
                "status": phase_exec.status,
                "completion_percentage": phase_exec.completion_percentage,
                "is_sla_breached": phase_exec.is_sla_breached,
                "started_at": phase_exec.started_at.isoformat() if phase_exec.started_at else None,
                "completed_at": phase_exec.completed_at.isoformat() if phase_exec.completed_at else None,
                "sla_target": phase_exec.sla_target_completion.isoformat() if phase_exec.sla_target_completion else None
            }

        # Pending handoffs
        for handoff in incident.handoff_history:
            if not handoff.signed_off_by:
                dashboard["pending_handoffs"].append({
                    "from_phase": handoff.from_phase,
                    "to_phase": handoff.to_phase,
                    "initiated_by": handoff.initiated_by,
                    "initiated_at": handoff.initiated_at.isoformat()
                })

        # Recent notifications
        dashboard["recent_notifications"] = [
            {
                "message": n.message,
                "roles": n.notified_roles,
                "at": n.notified_at.isoformat()
            }
            for n in incident.notifications[-5:]  # Last 5
        ]

        return dashboard
