import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { incidentAPI, IncidentState, Assessment } from '../api/client';
import Checklist from '../components/Checklist';

const Containment: React.FC = () => {
  const { incidentId } = useParams<{ incidentId: string }>();
  const navigate = useNavigate();

  const [incident, setIncident] = useState<IncidentState | null>(null);
  const [guidance, setGuidance] = useState<Assessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionsTaken, setActionsTaken] = useState<string>('');

  useEffect(() => {
    loadIncident();
  }, [incidentId]);

  const loadIncident = async () => {
    if (!incidentId) return;

    try {
      const data = await incidentAPI.getIncident(incidentId);
      setIncident(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load incident');
    } finally {
      setLoading(false);
    }
  };

  const generateGuidance = async () => {
    if (!incidentId) return;

    setGenerating(true);
    setError(null);

    try {
      const result = await incidentAPI.getContainmentGuidance(incidentId);
      setGuidance(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate guidance');
    } finally {
      setGenerating(false);
    }
  };

  const recordActions = async () => {
    if (!incidentId || !actionsTaken.trim()) return;

    setLoading(true);
    try {
      const actions = actionsTaken
        .split('\n')
        .map((a) => a.trim())
        .filter((a) => a);

      await incidentAPI.updateIncident(incidentId, {
        actions_taken: actions,
        status: 'remediation',
      });

      await loadIncident();
      setActionsTaken('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to record actions');
    } finally {
      setLoading(false);
    }
  };

  const proceedToSummary = () => {
    navigate(`/summary/${incidentId}`);
  };

  if (loading && !incident) {
    return <div className="container"><div className="loading">Loading...</div></div>;
  }

  if (!incident) {
    return <div className="container"><div className="error-message">Incident not found</div></div>;
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Containment & Remediation</h1>
        <p className="subtitle">Incident ID: {incident.incident_id}</p>
      </div>

      <div className="card">
        <h2>Current Status</h2>
        <div className="info-grid">
          <div>
            <strong>Status:</strong> <span className="status-badge">{incident.status}</span>
          </div>
          <div>
            <strong>Actions Taken:</strong> {incident.actions_taken.length}
          </div>
        </div>

        {incident.actions_taken.length > 0 && (
          <div className="info-box">
            <h4>Actions Already Taken:</h4>
            <ul>
              {incident.actions_taken.map((action, idx) => (
                <li key={idx}>{action}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {!guidance && (
        <div className="card">
          <h2>Generate Containment Guidance</h2>
          <p>
            Get AI-powered containment and remediation recommendations based on the
            investigation findings.
          </p>
          <button
            className="btn btn-primary"
            onClick={generateGuidance}
            disabled={generating}
          >
            {generating ? 'Generating Guidance...' : 'Generate Guidance'}
          </button>
        </div>
      )}

      {guidance && (
        <>
          <div className="card">
            <h2>Containment Actions</h2>

            {guidance.containment_actions && guidance.containment_actions.length > 0 && (
              <div>
                <h3>AI Recommendations:</h3>
                <Checklist title="" items={guidance.containment_actions} />
              </div>
            )}

            {guidance.playbook_containment_actions &&
              guidance.playbook_containment_actions.length > 0 && (
                <div className="info-box">
                  <h4>Playbook-Based Actions:</h4>
                  <Checklist title="" items={guidance.playbook_containment_actions} />
                </div>
              )}
          </div>

          <div className="card">
            <h2>Remediation Steps</h2>

            {guidance.remediation_steps && guidance.remediation_steps.length > 0 && (
              <div>
                <h3>AI Recommendations:</h3>
                <Checklist title="" items={guidance.remediation_steps} />
              </div>
            )}

            {guidance.playbook_remediation && (
              <div className="info-box">
                <h4>Standard Remediation Steps:</h4>
                <Checklist title="" items={guidance.playbook_remediation.standard_steps} />

                <h4>User Education:</h4>
                <Checklist title="" items={guidance.playbook_remediation.user_education} />
              </div>
            )}
          </div>

          {guidance.risk_notes && guidance.risk_notes.length > 0 && (
            <div className="card">
              <h2>Risk Considerations</h2>
              <div className="alert alert-warning">
                <Checklist title="" items={guidance.risk_notes} />
              </div>
            </div>
          )}

          <div className="card">
            <h2>Record Actions Taken</h2>
            <p>Document the containment and remediation actions you have completed.</p>

            <div className="form-group">
              <label htmlFor="actions">Actions Taken (one per line):</label>
              <textarea
                id="actions"
                rows={6}
                value={actionsTaken}
                onChange={(e) => setActionsTaken(e.target.value)}
                placeholder="Password reset forced for affected user&#10;Active sessions revoked&#10;Phishing email removed from mailbox&#10;Sender domain blocked"
              />
            </div>

            <button
              className="btn btn-primary"
              onClick={recordActions}
              disabled={!actionsTaken.trim() || loading}
            >
              Record Actions
            </button>
          </div>

          <div className="card">
            <h2>Generate Summary</h2>
            <p>
              Once containment and remediation actions are complete, generate a final
              incident summary for documentation.
            </p>
            <button className="btn btn-primary" onClick={proceedToSummary}>
              Generate Summary
            </button>
          </div>
        </>
      )}

      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default Containment;
