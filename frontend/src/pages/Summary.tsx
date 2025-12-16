import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { incidentAPI, IncidentSummary } from '../api/client';

const Summary: React.FC = () => {
  const { incidentId } = useParams<{ incidentId: string }>();
  const navigate = useNavigate();

  const [summary, setSummary] = useState<IncidentSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSummary();
  }, [incidentId]);

  const loadSummary = async () => {
    if (!incidentId) return;

    try {
      const data = await incidentAPI.exportSummary(incidentId);
      setSummary(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate summary');
    } finally {
      setLoading(false);
    }
  };

  const exportAsJSON = () => {
    if (!summary) return;

    const dataStr = JSON.stringify(summary, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `incident-${summary.incident_id}.json`;
    link.click();

    URL.revokeObjectURL(url);
  };

  const exportAsText = () => {
    if (!summary) return;

    let text = `INCIDENT RESPONSE SUMMARY\n`;
    text += `${'='.repeat(50)}\n\n`;
    text += `Incident ID: ${summary.incident_id}\n`;
    text += `Incident Type: ${summary.incident_type}\n`;
    text += `Created: ${new Date(summary.created_at).toLocaleString()}\n`;
    if (summary.closed_at) {
      text += `Closed: ${new Date(summary.closed_at).toLocaleString()}\n`;
    }
    text += `\n${'='.repeat(50)}\n\n`;

    text += `SUMMARY:\n${summary.incident_summary}\n\n`;

    text += `${'='.repeat(50)}\n\n`;
    text += `ACTIONS TAKEN:\n`;
    summary.actions_taken.forEach((action, idx) => {
      text += `${idx + 1}. ${action}\n`;
    });

    if (summary.open_risks.length > 0) {
      text += `\n${'='.repeat(50)}\n\n`;
      text += `OPEN RISKS:\n`;
      summary.open_risks.forEach((risk, idx) => {
        text += `${idx + 1}. ${risk}\n`;
      });
    }

    if (summary.recommended_followups.length > 0) {
      text += `\n${'='.repeat(50)}\n\n`;
      text += `RECOMMENDED FOLLOW-UPS:\n`;
      summary.recommended_followups.forEach((followup, idx) => {
        text += `${idx + 1}. ${followup}\n`;
      });
    }

    if (summary.timeline.length > 0) {
      text += `\n${'='.repeat(50)}\n\n`;
      text += `TIMELINE:\n`;
      summary.timeline.forEach((entry) => {
        text += `[${entry.timestamp}] ${entry.event}\n`;
      });
    }

    const dataBlob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `incident-${summary.incident_id}.txt`;
    link.click();

    URL.revokeObjectURL(url);
  };

  const startNewIncident = () => {
    navigate('/');
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Generating summary...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="container">
        <div className="error-message">Summary not available</div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Incident Summary</h1>
        <p className="subtitle">Incident ID: {summary.incident_id}</p>
      </div>

      <div className="card">
        <h2>Incident Information</h2>
        <div className="info-grid">
          <div>
            <strong>Incident Type:</strong> {summary.incident_type}
          </div>
          <div>
            <strong>Created:</strong> {new Date(summary.created_at).toLocaleString()}
          </div>
          {summary.closed_at && (
            <div>
              <strong>Closed:</strong> {new Date(summary.closed_at).toLocaleString()}
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <h2>Summary</h2>
        <div className="summary-text">{summary.incident_summary}</div>
      </div>

      {summary.actions_taken.length > 0 && (
        <div className="card">
          <h2>Actions Taken</h2>
          <ul className="action-list">
            {summary.actions_taken.map((action, idx) => (
              <li key={idx}>{action}</li>
            ))}
          </ul>
        </div>
      )}

      {summary.open_risks.length > 0 && (
        <div className="card">
          <h2>Open Risks</h2>
          <div className="alert alert-warning">
            <ul className="action-list">
              {summary.open_risks.map((risk, idx) => (
                <li key={idx}>{risk}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {summary.recommended_followups.length > 0 && (
        <div className="card">
          <h2>Recommended Follow-ups</h2>
          <ul className="action-list">
            {summary.recommended_followups.map((followup, idx) => (
              <li key={idx}>{followup}</li>
            ))}
          </ul>
        </div>
      )}

      {summary.timeline.length > 0 && (
        <div className="card">
          <h2>Timeline</h2>
          <div className="timeline">
            {summary.timeline.map((entry, idx) => (
              <div key={idx} className="timeline-entry">
                <div className="timeline-timestamp">{entry.timestamp}</div>
                <div className="timeline-event">
                  {entry.event}
                  {entry.details && <span className="timeline-details"> - {entry.details}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <h2>Export Options</h2>
        <p>Download this incident summary in your preferred format.</p>

        <div className="button-group">
          <button className="btn btn-primary" onClick={exportAsJSON}>
            Export as JSON
          </button>
          <button className="btn btn-primary" onClick={exportAsText}>
            Export as Text
          </button>
        </div>
      </div>

      <div className="card">
        <button className="btn btn-secondary" onClick={startNewIncident}>
          Start New Incident
        </button>
      </div>
    </div>
  );
};

export default Summary;
