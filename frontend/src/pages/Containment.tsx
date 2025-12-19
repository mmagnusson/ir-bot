import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { incidentAPI, IncidentState } from '../api/client';
import { playbookAPI, ChecklistStep, DashboardData, EvidenceItem } from '../api/playbookAPI';
import { EnhancedChecklist } from '../components/EnhancedChecklist';
import { RoleAssignment } from '../components/RoleAssignment';
import { HandoffPanel } from '../components/HandoffPanel';
import { TimeTrackingDashboard } from '../components/TimeTrackingDashboard';

const Containment: React.FC = () => {
  const { incidentId } = useParams<{ incidentId: string }>();
  const navigate = useNavigate();

  const [incident, setIncident] = useState<IncidentState | null>(null);
  const [steps, setSteps] = useState<ChecklistStep[]>([]);
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentUser] = useState('admin@company.com'); // TODO: Get from auth context
  const [currentUserRole] = useState('system_admin'); // TODO: Get from role assignment

  useEffect(() => {
    loadIncident();
  }, [incidentId]);

  const loadIncident = async () => {
    if (!incidentId) return;

    try {
      const [incidentData, stepsData, dashboardData] = await Promise.all([
        incidentAPI.getIncident(incidentId),
        playbookAPI.getPhaseSteps(incidentId, 'containment'),
        playbookAPI.getDashboard(incidentId)
      ]);

      setIncident(incidentData);
      setSteps(stepsData);
      setDashboard(dashboardData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load incident');
    } finally {
      setLoading(false);
    }
  };

  const handleStepStart = async (stepId: string) => {
    if (!incidentId) return;

    try {
      await playbookAPI.startStep(incidentId, stepId, currentUser);
      await loadIncident();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start step');
    }
  };

  const handleStepUpdate = async (stepId: string, updates: Partial<ChecklistStep>) => {
    if (!incidentId) return;

    try {
      await playbookAPI.updateStep(incidentId, stepId, updates);
      await loadIncident();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update step');
    }
  };

  const handleEvidenceAdd = async (stepId: string, evidence: EvidenceItem[]) => {
    if (!incidentId) return;

    try {
      await playbookAPI.addEvidence(incidentId, stepId, evidence);
      await loadIncident();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add evidence');
    }
  };

  const handleRoleAssign = async (roleName: string, user: string) => {
    if (!incidentId) return;

    try {
      await playbookAPI.assignRole(incidentId, roleName, user);
      await loadIncident();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to assign role');
    }
  };

  const handleInitiateHandoff = async (notes: string) => {
    if (!incidentId) return;

    try {
      await playbookAPI.initiateHandoff(incidentId, 'remediation', currentUser, notes);
      await loadIncident();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to initiate handoff');
    }
  };

  const handleSignOff = async (notes: string) => {
    if (!incidentId) return;

    try {
      await playbookAPI.signOffHandoff(incidentId, currentUser, notes);
      await loadIncident();
      navigate(`/summary/${incidentId}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to sign off handoff');
    }
  };

  if (loading) {
    return <div className="container"><div className="loading">Loading incident...</div></div>;
  }

  if (!incident || !dashboard) {
    return <div className="container"><div className="error-message">Incident not found</div></div>;
  }

  // Calculate handoff requirements
  const handoffRequirements = [
    {
      key: 'all_critical',
      description: 'All critical containment steps completed',
      met: steps.filter(s => s.critical).every(s => s.status === 'completed')
    },
    {
      key: 'sign_off',
      description: 'System administrator sign-off required',
      met: !!dashboard.phase_progress['containment']?.signed_off_by
    }
  ];

  return (
    <div className="container">
      <div className="header">
        <h1>Containment Phase</h1>
        <p className="subtitle">Incident ID: {incident.incident_id}</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Time Tracking Dashboard */}
      <TimeTrackingDashboard
        phases={dashboard.phase_progress}
        currentPhase={dashboard.current_phase}
        incidentCreatedAt={incident.created_at}
      />

      {/* Role Assignments */}
      <RoleAssignment
        roles={dashboard.role_assignments}
        onAssign={handleRoleAssign}
        readOnly={false}
      />

      {/* Containment Checklist */}
      <div className="card">
        <h2>Containment Checklist</h2>
        <EnhancedChecklist
          steps={steps}
          onStepStart={handleStepStart}
          onStepUpdate={handleStepUpdate}
          onEvidenceAdd={handleEvidenceAdd}
          currentUser={currentUser}
          currentUserRole={currentUserRole}
          readOnly={false}
        />
      </div>

      {/* Handoff Panel */}
      <HandoffPanel
        currentPhase="containment"
        nextPhase="remediation"
        requirements={handoffRequirements}
        onInitiateHandoff={handleInitiateHandoff}
        onSignOff={handleSignOff}
        pendingHandoff={dashboard.pending_handoff}
        canInitiate={currentUserRole === 'system_admin'}
        canSignOff={currentUserRole === 'incident_commander'}
        readOnly={false}
      />
    </div>
  );
};

export default Containment;
