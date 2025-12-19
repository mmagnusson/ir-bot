import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// TypeScript interfaces for playbook API

export interface EvidenceItem {
  evidence_type: 'text' | 'file' | 'boolean' | 'number' | 'timestamp' | 'url';
  name: string;
  value: any;
  collected_at?: string;
  collected_by?: string;
}

export interface StepExecution {
  step_id: string;
  status: 'not_started' | 'in_progress' | 'blocked' | 'completed' | 'skipped';
  assigned_to?: string;
  assigned_user?: string;
  started_at?: string;
  completed_at?: string;
  evidence: EvidenceItem[];
  notes?: string;
  blocked_reason?: string;
}

export interface PhaseExecution {
  phase_name: string;
  status: 'not_started' | 'in_progress' | 'completed';
  started_at?: string;
  completed_at?: string;
  steps: { [key: string]: StepExecution };
  signed_off_by?: string;
  signed_off_at?: string;
  sla_target_completion?: string;
  completion_percentage: number;
}

export interface RoleAssignment {
  role_name: string;
  assigned_user?: string;
  assigned_at?: string;
  required: boolean;
}

export interface PhaseHandoff {
  from_phase: string;
  to_phase: string;
  from_role: string;
  to_role: string;
  initiated_by: string;
  initiated_at: string;
  signed_off_by?: string;
  signed_off_at?: string;
  handoff_notes?: string;
  checklist_completion_at_handoff: number;
  requirements_met: boolean;
}

export interface ChecklistStep {
  id: string;
  step: string;
  description: string;
  assigned_to: string;
  estimated_time_minutes: number;
  parallel_group: string | null;
  dependencies: string[];
  critical: boolean;
  evidence_required: Array<{
    type: string;
    name: string;
    prompt: string;
    optional?: boolean;
  }>;

  // Execution data
  status: 'not_started' | 'in_progress' | 'blocked' | 'completed' | 'skipped';
  assigned_user?: string;
  started_at?: string;
  completed_at?: string;
  notes?: string;
  blocked_reason?: string;
  evidence?: EvidenceItem[];

  // Computed fields
  applies: boolean;
  dependencies_met: boolean;
}

export interface PhaseData {
  phase_name: string;
  description: string;
  primary_role: string;
  supporting_roles?: string[];
  handoff_to?: string;
  sla?: {
    target_completion_hours: number;
    escalation_threshold_hours: number;
    notify_roles: string[];
  };
  steps: ChecklistStep[];
}

export interface DashboardData {
  incident_id: string;
  current_phase: string;
  phase_progress: { [key: string]: PhaseProgress };
  role_assignments: { [key: string]: RoleAssignment };
  pending_handoff?: PhaseHandoff | null;
  overall_completion: number;
}

export interface PhaseProgress {
  phase_name: string;
  status: 'not_started' | 'in_progress' | 'completed';
  started_at?: string;
  completed_at?: string;
  completion_percentage: number;
  sla_target_completion?: string;
  sla_escalation_threshold?: string;
  sla_status: 'on_track' | 'warning' | 'breached' | 'na';
  time_remaining_hours?: number;
  estimated_total_minutes?: number;
  actual_total_minutes?: number;
}

export interface StepUpdateRequest {
  step_id: string;
  status?: 'not_started' | 'in_progress' | 'blocked' | 'completed' | 'skipped';
  assigned_user?: string;
  notes?: string;
  blocked_reason?: string;
  evidence?: EvidenceItem[];
}

export interface RoleAssignmentRequest {
  role_name: string;
  assigned_user: string;
}

export interface PhaseHandoffRequest {
  to_phase: string;
  initiated_by: string;
  handoff_notes?: string;
}

export interface PhaseSignOffRequest {
  signed_off_by: string;
  notes?: string;
}

// Playbook API methods

export const playbookAPI = {
  /**
   * Get all phases for an incident with their metadata
   */
  getPhases: async (incidentId: string): Promise<{ [key: string]: PhaseData }> => {
    const response = await apiClient.get(`/api/incidents/${incidentId}/playbook/phases`);
    return response.data;
  },

  /**
   * Get all steps for a specific phase with execution status
   */
  getPhaseSteps: async (incidentId: string, phaseName: string): Promise<ChecklistStep[]> => {
    const response = await apiClient.get(
      `/api/incidents/${incidentId}/playbook/phases/${phaseName}/steps`
    );
    return response.data;
  },

  /**
   * Start a step (mark as in_progress)
   */
  startStep: async (incidentId: string, stepId: string, assignedUser: string): Promise<StepExecution> => {
    const response = await apiClient.post(
      `/api/incidents/${incidentId}/playbook/steps/${stepId}/start`,
      { assigned_user: assignedUser }
    );
    return response.data;
  },

  /**
   * Update a step's status, notes, or other fields
   */
  updateStep: async (
    incidentId: string,
    stepId: string,
    updates: Partial<StepUpdateRequest>
  ): Promise<StepExecution> => {
    const response = await apiClient.put(
      `/api/incidents/${incidentId}/playbook/steps/${stepId}`,
      updates
    );
    return response.data;
  },

  /**
   * Add evidence to a step
   */
  addEvidence: async (
    incidentId: string,
    stepId: string,
    evidence: EvidenceItem[]
  ): Promise<StepExecution> => {
    const response = await apiClient.post(
      `/api/incidents/${incidentId}/playbook/steps/${stepId}/evidence`,
      { evidence }
    );
    return response.data;
  },

  /**
   * Assign a user to a role
   */
  assignRole: async (
    incidentId: string,
    roleName: string,
    assignedUser: string
  ): Promise<RoleAssignment> => {
    const response = await apiClient.post(
      `/api/incidents/${incidentId}/playbook/roles/assign`,
      { role_name: roleName, assigned_user: assignedUser }
    );
    return response.data;
  },

  /**
   * Get all role assignments for an incident
   */
  getRoles: async (incidentId: string): Promise<{ [key: string]: RoleAssignment }> => {
    const response = await apiClient.get(`/api/incidents/${incidentId}/playbook/roles`);
    return response.data;
  },

  /**
   * Initiate a handoff from current phase to next phase
   */
  initiateHandoff: async (
    incidentId: string,
    toPhase: string,
    initiatedBy: string,
    notes?: string
  ): Promise<PhaseHandoff> => {
    const response = await apiClient.post(
      `/api/incidents/${incidentId}/playbook/handoff`,
      { to_phase: toPhase, initiated_by: initiatedBy, handoff_notes: notes }
    );
    return response.data;
  },

  /**
   * Sign off on a pending handoff
   */
  signOffHandoff: async (
    incidentId: string,
    signedOffBy: string,
    notes?: string
  ): Promise<PhaseHandoff> => {
    const response = await apiClient.post(
      `/api/incidents/${incidentId}/playbook/handoff/sign-off`,
      { signed_off_by: signedOffBy, notes: notes }
    );
    return response.data;
  },

  /**
   * Get complete dashboard data for an incident
   */
  getDashboard: async (incidentId: string): Promise<DashboardData> => {
    const response = await apiClient.get(`/api/incidents/${incidentId}/playbook/dashboard`);
    return response.data;
  }
};

export default playbookAPI;
