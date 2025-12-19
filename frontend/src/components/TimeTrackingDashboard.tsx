import React from 'react';
import './TimeTrackingDashboard.css';

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

interface TimeTrackingDashboardProps {
  phases: { [key: string]: PhaseProgress };
  currentPhase: string;
  incidentCreatedAt: string;
}

export const TimeTrackingDashboard: React.FC<TimeTrackingDashboardProps> = ({
  phases,
  currentPhase,
  incidentCreatedAt
}) => {
  const getSLAStatusClass = (status: string): string => {
    switch (status) {
      case 'on_track':
        return 'sla-on-track';
      case 'warning':
        return 'sla-warning';
      case 'breached':
        return 'sla-breached';
      default:
        return 'sla-na';
    }
  };

  const getSLAIcon = (status: string): string => {
    switch (status) {
      case 'on_track':
        return '✓';
      case 'warning':
        return '⚠';
      case 'breached':
        return '✗';
      default:
        return '○';
    }
  };

  const formatDateTime = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  const formatDuration = (minutes: number): string => {
    if (minutes < 60) {
      return `${minutes}m`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  const calculateIncidentAge = (): string => {
    const created = new Date(incidentCreatedAt);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - created.getTime()) / 60000);
    return formatDuration(diffMinutes);
  };

  const formatTimeRemaining = (hours: number): string => {
    if (hours < 0) {
      return `${Math.abs(hours).toFixed(1)}h overdue`;
    }
    if (hours < 1) {
      return `${Math.floor(hours * 60)}m remaining`;
    }
    return `${hours.toFixed(1)}h remaining`;
  };

  const phaseOrder = ['intake', 'investigation', 'containment', 'remediation', 'closure'];
  const orderedPhases = phaseOrder
    .filter(phaseName => phases[phaseName])
    .map(phaseName => ({ name: phaseName, ...phases[phaseName] }));

  return (
    <div className="time-tracking-dashboard">
      <div className="dashboard-header">
        <h3>Incident Progress Dashboard</h3>
        <div className="incident-age">
          <span className="label">Incident Age:</span>
          <span className="value">{calculateIncidentAge()}</span>
        </div>
      </div>

      <div className="phases-timeline">
        {orderedPhases.map((phase, index) => {
          const isCurrent = phase.name === currentPhase;
          const isCompleted = phase.status === 'completed';
          const isInProgress = phase.status === 'in_progress';
          const isNotStarted = phase.status === 'not_started';

          return (
            <div
              key={phase.name}
              className={`phase-card ${isCurrent ? 'current' : ''} ${
                isCompleted ? 'completed' : ''
              } ${isInProgress ? 'in-progress' : ''} ${
                isNotStarted ? 'not-started' : ''
              }`}
            >
              {/* Phase Header */}
              <div className="phase-header">
                <div className="phase-title">
                  <span className="phase-number">{index + 1}</span>
                  <h4>{phase.name}</h4>
                </div>
                <div className={`phase-status ${phase.status}`}>
                  {phase.status === 'completed' && '✓'}
                  {phase.status === 'in_progress' && '⟳'}
                  {phase.status === 'not_started' && '○'}
                </div>
              </div>

              {/* Progress Bar */}
              <div className="progress-section">
                <div className="progress-bar-container">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${phase.completion_percentage}%` }}
                  />
                </div>
                <span className="progress-percentage">
                  {phase.completion_percentage.toFixed(0)}%
                </span>
              </div>

              {/* Time Information */}
              {(isInProgress || isCompleted) && (
                <div className="time-info">
                  <div className="time-row">
                    <span className="time-label">Started:</span>
                    <span className="time-value">
                      {phase.started_at ? formatDateTime(phase.started_at) : 'N/A'}
                    </span>
                  </div>
                  {isCompleted && phase.completed_at && (
                    <div className="time-row">
                      <span className="time-label">Completed:</span>
                      <span className="time-value">{formatDateTime(phase.completed_at)}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Duration Tracking */}
              {(phase.estimated_total_minutes || phase.actual_total_minutes) && (
                <div className="duration-info">
                  {phase.estimated_total_minutes && (
                    <div className="duration-row">
                      <span className="duration-label">Estimated:</span>
                      <span className="duration-value">
                        {formatDuration(phase.estimated_total_minutes)}
                      </span>
                    </div>
                  )}
                  {phase.actual_total_minutes && (
                    <div className="duration-row">
                      <span className="duration-label">Actual:</span>
                      <span className="duration-value">
                        {formatDuration(phase.actual_total_minutes)}
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* SLA Status */}
              {phase.sla_status !== 'na' && (
                <div className={`sla-section ${getSLAStatusClass(phase.sla_status)}`}>
                  <div className="sla-header">
                    <span className="sla-icon">{getSLAIcon(phase.sla_status)}</span>
                    <span className="sla-label">SLA Status</span>
                  </div>

                  {phase.time_remaining_hours !== undefined && isInProgress && (
                    <div className="sla-time">
                      {formatTimeRemaining(phase.time_remaining_hours)}
                    </div>
                  )}

                  {phase.sla_target_completion && (
                    <div className="sla-target">
                      <span className="sla-target-label">Target:</span>
                      <span className="sla-target-value">
                        {formatDateTime(phase.sla_target_completion)}
                      </span>
                    </div>
                  )}

                  {phase.sla_status === 'breached' && (
                    <div className="sla-breach-warning">
                      SLA threshold exceeded - escalation required
                    </div>
                  )}
                </div>
              )}

              {/* Connector Line to Next Phase */}
              {index < orderedPhases.length - 1 && (
                <div className="phase-connector">
                  <div className="connector-line" />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Overall Summary */}
      <div className="overall-summary">
        <div className="summary-stat">
          <span className="stat-label">Phases Completed:</span>
          <span className="stat-value">
            {Object.values(phases).filter(p => p.status === 'completed').length} /{' '}
            {Object.keys(phases).length}
          </span>
        </div>
        <div className="summary-stat">
          <span className="stat-label">Overall Progress:</span>
          <span className="stat-value">
            {(
              Object.values(phases).reduce((sum, p) => sum + p.completion_percentage, 0) /
              Object.keys(phases).length
            ).toFixed(0)}
            %
          </span>
        </div>
      </div>
    </div>
  );
};
