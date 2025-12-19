import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { incidentAPI, IncidentState } from '../api/client';
import { playbookAPI, DashboardData } from '../api/playbookAPI';

interface IncidentSummary {
  incident_id: string;
  incident_type: string;
  created_at: string;
  closed_at?: string;
  incident_summary: string;
  actions_taken: string[];
  open_risks: string[];
  recommended_followups: string[];
  timeline: Array<{ timestamp: string; event: string; details?: string }>;
  phases_completed: string[];
  total_time_spent_hours: number;
}

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
      const [incident, dashboard] = await Promise.all([
        incidentAPI.getIncident(incidentId),
        playbookAPI.getDashboard(incidentId)
      ]);

      const summaryData = buildSummaryFromPlaybook(incident, dashboard);
      setSummary(summaryData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate summary');
    } finally {
      setLoading(false);
    }
  };

  const buildSummaryFromPlaybook = (
    incident: IncidentState,
    dashboard: DashboardData
  ): IncidentSummary => {
    // Build timeline from phase executions
    const timeline: Array<{ timestamp: string; event: string; details?: string }> = [];

    timeline.push({
      timestamp: new Date(incident.created_at).toLocaleString(),
      event: 'Incident Created',
      details: `Type: ${incident.incident_type}`
    });

    Object.values(dashboard.phase_progress).forEach(phase => {
      if (phase.started_at) {
        timeline.push({
          timestamp: new Date(phase.started_at).toLocaleString(),
          event: `${phase.phase_name} Phase Started`
        });
      }
      if (phase.completed_at) {
        timeline.push({
          timestamp: new Date(phase.completed_at).toLocaleString(),
          event: `${phase.phase_name} Phase Completed`,
          details: `${phase.completion_percentage}% complete`
        });
      }
    });

    // Collect actions taken from step evidence
    const actions_taken: string[] = [];
    Object.values(dashboard.phase_progress).forEach(phase => {
      Object.values(phase.steps || {}).forEach((step: any) => {
        if (step.status === 'completed' && step.evidence) {
          step.evidence.forEach((ev: any) => {
            if (ev.evidence_type === 'text' && ev.name.includes('action')) {
              actions_taken.push(`[${phase.phase_name}] ${step.step}: ${ev.value}`);
            }
          });
        }
      });
    });

    // Identify open risks from blocked steps and notes
    const open_risks: string[] = [];
    Object.values(dashboard.phase_progress).forEach(phase => {
      Object.values(phase.steps || {}).forEach((step: any) => {
        if (step.status === 'blocked') {
          open_risks.push(
            `${phase.phase_name}: ${step.step} - ${step.blocked_reason || 'Blocked'}`
          );
        }
        if (step.notes && step.notes.toLowerCase().includes('risk')) {
          open_risks.push(`${phase.phase_name}: ${step.notes}`);
        }
      });
    });

    // Build recommended follow-ups
    const recommended_followups: string[] = [
      'Conduct post-incident review with all stakeholders',
      'Update incident response playbooks based on lessons learned',
      'Schedule follow-up security awareness training if needed',
      'Review and update detection rules to catch similar incidents earlier'
    ];

    // Calculate phases completed
    const phases_completed = Object.values(dashboard.phase_progress)
      .filter(p => p.status === 'completed')
      .map(p => p.phase_name);

    // Calculate total time spent
    const total_time_spent_hours = Object.values(dashboard.phase_progress).reduce(
      (sum, phase) => sum + (phase.actual_total_minutes || 0),
      0
    ) / 60;

    // Build incident summary narrative
    const incident_summary = `
This ${incident.incident_type} incident was managed through a playbook-driven workflow across ${phases_completed.length} phases.
The incident response team completed ${Object.values(dashboard.phase_progress).reduce((sum, p) => sum + Object.keys(p.steps || {}).length, 0)}
total steps with ${actions_taken.length} documented actions taken.

${incident.incident_type === 'phishing'
  ? 'The phishing incident was investigated, contained, and remediated according to established procedures.'
  : incident.incident_type === 'malware'
  ? 'The malware incident was analyzed, contained, and systems were cleaned following security protocols.'
  : incident.incident_type === 'ransomware'
  ? 'The ransomware attack was contained, affected systems isolated, and recovery procedures initiated.'
  : incident.incident_type === 'data_breach'
  ? 'The data breach was investigated, affected data identified, and notification procedures followed.'
  : incident.incident_type === 'ddos'
  ? 'The DDoS attack was mitigated through upstream filtering and rate limiting measures.'
  : incident.incident_type === 'unauthorized_access'
  ? 'Unauthorized access was terminated, credentials reset, and access controls strengthened.'
  : 'The security incident was investigated and appropriate containment measures were applied.'
}

Total incident response time: ${total_time_spent_hours.toFixed(1)} hours.
${open_risks.length > 0 ? `${open_risks.length} open risk(s) identified for follow-up.` : 'No open risks identified.'}
    `.trim();

    return {
      incident_id: incident.incident_id,
      incident_type: incident.incident_type,
      created_at: incident.created_at,
      closed_at: incident.status === 'closed' ? new Date().toISOString() : undefined,
      incident_summary,
      actions_taken: actions_taken.length > 0 ? actions_taken : ['No actions documented'],
      open_risks,
      recommended_followups,
      timeline,
      phases_completed,
      total_time_spent_hours
    };
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
    text += `Total Time: ${summary.total_time_spent_hours.toFixed(1)} hours\n`;
    text += `Phases Completed: ${summary.phases_completed.join(', ')}\n`;
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
        text += `[${entry.timestamp}] ${entry.event}`;
        if (entry.details) {
          text += ` - ${entry.details}`;
        }
        text += `\n`;
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
          <div>
            <strong>Total Time:</strong> {summary.total_time_spent_hours.toFixed(1)} hours
          </div>
          <div>
            <strong>Phases Completed:</strong> {summary.phases_completed.join(', ')}
          </div>
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
