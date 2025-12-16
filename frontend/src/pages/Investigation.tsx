import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { incidentAPI, IncidentState, Assessment, PhishingIncidentData } from '../api/client';
import Checklist from '../components/Checklist';

const Investigation: React.FC = () => {
  const { incidentId } = useParams<{ incidentId: string }>();
  const navigate = useNavigate();

  const [incident, setIncident] = useState<IncidentState | null>(null);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [assessing, setAssessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showUpdateForm, setShowUpdateForm] = useState(false);

  const [updateData, setUpdateData] = useState({
    credential_submission_confirmed: 'unknown' as 'yes' | 'no' | 'unknown',
    suspicious_signins_observed: 'unknown' as 'yes' | 'no' | 'unknown',
    mfa_enabled: 'unknown' as 'yes' | 'no' | 'unknown',
    other_affected_users: 'unknown' as 'yes' | 'no' | 'unknown',
  });

  useEffect(() => {
    loadIncident();
  }, [incidentId]);

  const loadIncident = async () => {
    if (!incidentId) return;

    try {
      const data = await incidentAPI.getIncident(incidentId);
      setIncident(data);

      if (data.current_assessment) {
        setAssessment(data.current_assessment);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load incident');
    } finally {
      setLoading(false);
    }
  };

  const runAssessment = async () => {
    if (!incidentId) return;

    setAssessing(true);
    setError(null);

    try {
      const result = await incidentAPI.assessIncident(incidentId);
      setAssessment(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to run assessment');
    } finally {
      setAssessing(false);
    }
  };

  const updateInvestigation = async () => {
    if (!incidentId || !incident?.phishing_data) return;

    setLoading(true);
    setError(null);

    try {
      const updatedPhishingData: PhishingIncidentData = {
        ...incident.phishing_data,
        ...updateData,
      };

      await incidentAPI.updateIncident(incidentId, {
        phishing_data: updatedPhishingData,
        status: 'investigation',
      });

      await loadIncident();
      setShowUpdateForm(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update incident');
    } finally {
      setLoading(false);
    }
  };

  const proceedToContainment = () => {
    navigate(`/containment/${incidentId}`);
  };

  if (loading) {
    return <div className="container"><div className="loading">Loading incident...</div></div>;
  }

  if (!incident) {
    return <div className="container"><div className="error-message">Incident not found</div></div>;
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Investigation</h1>
        <p className="subtitle">Incident ID: {incident.incident_id}</p>
      </div>

      <div className="card">
        <h2>Incident Details</h2>
        <div className="info-grid">
          <div>
            <strong>Reporting User:</strong> {incident.phishing_data?.reporting_user_email}
          </div>
          <div>
            <strong>Created:</strong> {new Date(incident.created_at).toLocaleString()}
          </div>
          <div>
            <strong>Status:</strong> <span className="status-badge">{incident.status}</span>
          </div>
          <div>
            <strong>User Clicked Link:</strong> {incident.phishing_data?.user_clicked}
          </div>
          <div>
            <strong>Attachment Opened:</strong> {incident.phishing_data?.attachment_opened}
          </div>
          <div>
            <strong>Credentials Entered:</strong> {incident.phishing_data?.credentials_entered}
          </div>
        </div>
      </div>

      {!assessment && (
        <div className="card">
          <h2>AI Assessment</h2>
          <p>Run an AI-powered assessment to analyze this incident and get recommendations.</p>
          <button
            className="btn btn-primary"
            onClick={runAssessment}
            disabled={assessing}
          >
            {assessing ? 'Analyzing...' : 'Run Assessment'}
          </button>
        </div>
      )}

      {assessment && (
        <>
          <div className="card">
            <h2>Assessment Results</h2>

            {assessment.risk_level && (
              <div className={`alert alert-${assessment.risk_level}`}>
                <strong>Risk Level:</strong> {assessment.risk_level.toUpperCase()}
              </div>
            )}

            {assessment.escalation?.required && (
              <div className="alert alert-warning">
                <strong>Escalation Required:</strong> {assessment.escalation.level} priority
              </div>
            )}

            {assessment.what_we_know && assessment.what_we_know.length > 0 && (
              <Checklist title="What We Know" items={assessment.what_we_know} />
            )}

            {assessment.what_we_need && assessment.what_we_need.length > 0 && (
              <Checklist title="What We Need to Determine" items={assessment.what_we_need} />
            )}

            {assessment.next_steps && assessment.next_steps.length > 0 && (
              <Checklist
                title="Recommended Next Investigative Steps"
                items={assessment.next_steps}
              />
            )}

            {assessment.playbook_steps && assessment.playbook_steps.length > 0 && (
              <div className="info-box">
                <h4>Playbook-Based Steps</h4>
                <Checklist title="" items={assessment.playbook_steps} />
              </div>
            )}
          </div>

          <div className="card">
            <h2>Update Investigation Findings</h2>

            {!showUpdateForm ? (
              <button
                className="btn btn-secondary"
                onClick={() => setShowUpdateForm(true)}
              >
                Add Investigation Findings
              </button>
            ) : (
              <div>
                <div className="form-group">
                  <label>Credential submission confirmed?</label>
                  <div className="radio-group">
                    {['yes', 'no', 'unknown'].map((option) => (
                      <label key={option} className="radio-label">
                        <input
                          type="radio"
                          name="credential_submission_confirmed"
                          value={option}
                          checked={updateData.credential_submission_confirmed === option}
                          onChange={(e) =>
                            setUpdateData({
                              ...updateData,
                              credential_submission_confirmed: e.target.value as any,
                            })
                          }
                        />
                        {option.charAt(0).toUpperCase() + option.slice(1)}
                      </label>
                    ))}
                  </div>
                </div>

                <div className="form-group">
                  <label>Suspicious sign-ins observed?</label>
                  <div className="radio-group">
                    {['yes', 'no', 'unknown'].map((option) => (
                      <label key={option} className="radio-label">
                        <input
                          type="radio"
                          name="suspicious_signins_observed"
                          value={option}
                          checked={updateData.suspicious_signins_observed === option}
                          onChange={(e) =>
                            setUpdateData({
                              ...updateData,
                              suspicious_signins_observed: e.target.value as any,
                            })
                          }
                        />
                        {option.charAt(0).toUpperCase() + option.slice(1)}
                      </label>
                    ))}
                  </div>
                </div>

                <div className="form-group">
                  <label>MFA enabled on account?</label>
                  <div className="radio-group">
                    {['yes', 'no', 'unknown'].map((option) => (
                      <label key={option} className="radio-label">
                        <input
                          type="radio"
                          name="mfa_enabled"
                          value={option}
                          checked={updateData.mfa_enabled === option}
                          onChange={(e) =>
                            setUpdateData({
                              ...updateData,
                              mfa_enabled: e.target.value as any,
                            })
                          }
                        />
                        {option.charAt(0).toUpperCase() + option.slice(1)}
                      </label>
                    ))}
                  </div>
                </div>

                <div className="form-group">
                  <label>Other affected users identified?</label>
                  <div className="radio-group">
                    {['yes', 'no', 'unknown'].map((option) => (
                      <label key={option} className="radio-label">
                        <input
                          type="radio"
                          name="other_affected_users"
                          value={option}
                          checked={updateData.other_affected_users === option}
                          onChange={(e) =>
                            setUpdateData({
                              ...updateData,
                              other_affected_users: e.target.value as any,
                            })
                          }
                        />
                        {option.charAt(0).toUpperCase() + option.slice(1)}
                      </label>
                    ))}
                  </div>
                </div>

                <div className="button-group">
                  <button className="btn btn-primary" onClick={updateInvestigation}>
                    Update Findings
                  </button>
                  <button
                    className="btn btn-secondary"
                    onClick={() => setShowUpdateForm(false)}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>

          <div className="card">
            <h2>Next Steps</h2>
            <p>
              Once you've completed the investigation steps and updated your findings,
              proceed to get containment and remediation guidance.
            </p>
            <button className="btn btn-primary" onClick={proceedToContainment}>
              Proceed to Containment
            </button>
          </div>
        </>
      )}

      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default Investigation;
