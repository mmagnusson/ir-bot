import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Observables {
  url?: string;
  hash?: string;
  sender_email?: string;
  sender_ip?: string;
}

export interface PhishingIncidentData {
  reporting_user_email: string;
  user_clicked: 'yes' | 'no' | 'unknown';
  attachment_opened: 'yes' | 'no' | 'unknown';
  credentials_entered: 'yes' | 'no' | 'unknown';
  time_of_report?: string;
  headers_available: boolean;
  observables?: Observables;
  credential_submission_confirmed?: 'yes' | 'no' | 'unknown';
  suspicious_signins_observed?: 'yes' | 'no' | 'unknown';
  mfa_enabled?: 'yes' | 'no' | 'unknown';
  other_affected_users?: 'yes' | 'no' | 'unknown';
}

export interface IncidentState {
  incident_id: string;
  incident_type: 'phishing' | 'malware' | 'account_compromise';
  created_at: string;
  updated_at: string;
  status: 'intake' | 'investigation' | 'containment' | 'remediation' | 'closed';
  phishing_data?: PhishingIncidentData;
  assessment_history: any[];
  current_assessment?: any;
  actions_taken: string[];
  open_risks: string[];
  recommended_followups: string[];
}

export interface IncidentCreateRequest {
  incident_type: 'phishing' | 'malware' | 'account_compromise';
  phishing_data?: PhishingIncidentData;
}

export interface IncidentUpdateRequest {
  phishing_data?: PhishingIncidentData;
  actions_taken?: string[];
  status?: string;
}

export interface Assessment {
  what_we_know: string[];
  what_we_need: string[];
  next_steps: string[];
  containment_actions?: string[];
  remediation_steps?: string[];
  risk_notes?: string[];
  risk_level?: string;
  escalation?: {
    required: boolean;
    level: string;
  };
  playbook_steps?: string[];
  playbook_containment_actions?: string[];
  playbook_remediation?: {
    standard_steps: string[];
    user_education: string[];
  };
}

export interface IncidentSummary {
  incident_id: string;
  incident_type: string;
  created_at: string;
  closed_at?: string;
  incident_summary: string;
  actions_taken: string[];
  open_risks: string[];
  recommended_followups: string[];
  timeline: any[];
}

export interface IncidentTypeClassification {
  incident_type: string;
  confidence: number;
  reasoning: string;
  key_indicators: string[];
}

export interface ClassificationResponse {
  primary_classification: IncidentTypeClassification;
  alternative_classifications: IncidentTypeClassification[];
  raw_data_summary: string;
  suggested_next_steps: string[];
}

export interface ClassificationRequest {
  raw_data: string;
  context?: string;
}

export const incidentAPI = {
  createIncident: async (data: IncidentCreateRequest): Promise<IncidentState> => {
    const response = await apiClient.post('/api/incidents/', data);
    return response.data;
  },

  getIncident: async (incidentId: string): Promise<IncidentState> => {
    const response = await apiClient.get(`/api/incidents/${incidentId}`);
    return response.data;
  },

  updateIncident: async (
    incidentId: string,
    data: IncidentUpdateRequest
  ): Promise<IncidentState> => {
    const response = await apiClient.put(`/api/incidents/${incidentId}`, data);
    return response.data;
  },

  assessIncident: async (incidentId: string): Promise<Assessment> => {
    const response = await apiClient.post(`/api/incidents/${incidentId}/assess`);
    return response.data;
  },

  getContainmentGuidance: async (incidentId: string): Promise<Assessment> => {
    const response = await apiClient.post(`/api/incidents/${incidentId}/containment`);
    return response.data;
  },

  exportSummary: async (incidentId: string): Promise<IncidentSummary> => {
    const response = await apiClient.get(`/api/incidents/${incidentId}/export`);
    return response.data;
  },

  listIncidents: async (): Promise<IncidentState[]> => {
    const response = await apiClient.get('/api/incidents/');
    return response.data;
  },
};

export default apiClient;
