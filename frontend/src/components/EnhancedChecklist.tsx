/**
 * Enhanced Checklist Component
 *
 * Interactive checklist component with:
 * - Step status indicators (not started, in progress, blocked, completed)
 * - Start/Complete/Block buttons
 * - Dependency checking (grays out steps until dependencies met)
 * - Parallel step grouping indicator
 * - Time tracking display (estimated vs actual)
 * - Role assignment display
 * - Evidence collection forms
 * - Notes/blocked reason display
 */

import React, { useState } from 'react';
import './EnhancedChecklist.css';

export interface EvidenceRequirement {
  type: 'text' | 'file' | 'boolean' | 'number' | 'timestamp' | 'url';
  name: string;
  prompt: string;
  optional?: boolean;
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
  evidence_required: EvidenceRequirement[];

  // Execution state
  status: 'not_started' | 'in_progress' | 'blocked' | 'completed' | 'skipped';
  assigned_user?: string;
  started_at?: string;
  completed_at?: string;
  notes?: string;
  blocked_reason?: string;
  evidence?: any[];

  // Computed
  applies: boolean;
  dependencies_met: boolean;
}

interface EnhancedChecklistProps {
  steps: ChecklistStep[];
  onStepStart: (stepId: string) => void;
  onStepUpdate: (stepId: string, updates: Partial<ChecklistStep>) => void;
  onEvidenceAdd: (stepId: string, evidence: any[]) => void;
  currentUser: string;
  currentUserRole: string;
  readOnly?: boolean;
}

export const EnhancedChecklist: React.FC<EnhancedChecklistProps> = ({
  steps,
  onStepStart,
  onStepUpdate,
  onEvidenceAdd,
  currentUser,
  currentUserRole,
  readOnly = false
}) => {
  const [expandedStep, setExpandedStep] = useState<string | null>(null);
  const [evidenceData, setEvidenceData] = useState<{ [key: string]: any }>({});

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✓';
      case 'in_progress':
        return '⟳';
      case 'blocked':
        return '⊗';
      case 'skipped':
        return '⤵';
      default:
        return '○';
    }
  };

  const getStatusClass = (status: string) => {
    return `status-${status.replace('_', '-')}`;
  };

  const calculateTimeSpent = (step: ChecklistStep): string => {
    if (!step.started_at) return 'Not started';

    const start = new Date(step.started_at);
    const end = step.completed_at ? new Date(step.completed_at) : new Date();
    const minutes = Math.floor((end.getTime() - start.getTime()) / 60000);

    return `${minutes} min${step.completed_at ? '' : ' (ongoing)'}`;
  };

  const canStartStep = (step: ChecklistStep): boolean => {
    if (!step.applies) return false;
    if (!step.dependencies_met) return false;
    if (step.status !== 'not_started') return false;
    if (step.assigned_to !== currentUserRole) return false;
    return true;
  };

  const handleStartStep = (stepId: string) => {
    if (readOnly) return;
    onStepStart(stepId);
  };

  const handleCompleteStep = (stepId: string) => {
    if (readOnly) return;
    onStepUpdate(stepId, { status: 'completed' });
  };

  const handleBlockStep = (stepId: string, reason: string) => {
    if (readOnly) return;
    onStepUpdate(stepId, { status: 'blocked', blocked_reason: reason });
  };

  const handleAddEvidence = (stepId: string) => {
    if (readOnly) return;
    const evidence = evidenceData[stepId] || {};
    const evidenceArray = Object.entries(evidence).map(([name, value]) => ({
      name,
      value,
      evidence_type: typeof value,
      collected_by: currentUser,
      collected_at: new Date().toISOString()
    }));
    onEvidenceAdd(stepId, evidenceArray);
    setEvidenceData({ ...evidenceData, [stepId]: {} });
  };

  const toggleExpand = (stepId: string) => {
    setExpandedStep(expandedStep === stepId ? null : stepId);
  };

  const groupStepsByParallel = (steps: ChecklistStep[]) => {
    const groups: { [key: string]: ChecklistStep[] } = {};
    const ungrouped: ChecklistStep[] = [];

    steps.forEach(step => {
      if (step.parallel_group) {
        if (!groups[step.parallel_group]) {
          groups[step.parallel_group] = [];
        }
        groups[step.parallel_group].push(step);
      } else {
        ungrouped.push(step);
      }
    });

    return { groups, ungrouped };
  };

  const renderEvidenceForm = (step: ChecklistStep) => {
    if (!step.evidence_required || step.evidence_required.length === 0) {
      return null;
    }

    return (
      <div className="evidence-form">
        <h4>Evidence Required:</h4>
        {step.evidence_required.map((req, idx) => (
          <div key={idx} className="evidence-field">
            <label>
              {req.prompt}
              {req.optional && <span className="optional-badge">(Optional)</span>}
            </label>
            {req.type === 'text' && (
              <textarea
                value={evidenceData[step.id]?.[req.name] || ''}
                onChange={(e) => setEvidenceData({
                  ...evidenceData,
                  [step.id]: {
                    ...evidenceData[step.id],
                    [req.name]: e.target.value
                  }
                })}
                placeholder={req.prompt}
              />
            )}
            {req.type === 'boolean' && (
              <select
                value={evidenceData[step.id]?.[req.name] || ''}
                onChange={(e) => setEvidenceData({
                  ...evidenceData,
                  [step.id]: {
                    ...evidenceData[step.id],
                    [req.name]: e.target.value === 'true'
                  }
                })}
              >
                <option value="">Select...</option>
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            )}
            {req.type === 'number' && (
              <input
                type="number"
                value={evidenceData[step.id]?.[req.name] || ''}
                onChange={(e) => setEvidenceData({
                  ...evidenceData,
                  [step.id]: {
                    ...evidenceData[step.id],
                    [req.name]: parseInt(e.target.value)
                  }
                })}
                placeholder={req.prompt}
              />
            )}
            {req.type === 'file' && (
              <input
                type="file"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    setEvidenceData({
                      ...evidenceData,
                      [step.id]: {
                        ...evidenceData[step.id],
                        [req.name]: file.name
                      }
                    });
                  }
                }}
              />
            )}
            {req.type === 'timestamp' && (
              <input
                type="datetime-local"
                value={evidenceData[step.id]?.[req.name] || ''}
                onChange={(e) => setEvidenceData({
                  ...evidenceData,
                  [step.id]: {
                    ...evidenceData[step.id],
                    [req.name]: e.target.value
                  }
                })}
              />
            )}
            {req.type === 'url' && (
              <input
                type="url"
                value={evidenceData[step.id]?.[req.name] || ''}
                onChange={(e) => setEvidenceData({
                  ...evidenceData,
                  [step.id]: {
                    ...evidenceData[step.id],
                    [req.name]: e.target.value
                  }
                })}
                placeholder="https://..."
              />
            )}
          </div>
        ))}
        <button
          className="btn btn-primary"
          onClick={() => handleAddEvidence(step.id)}
          disabled={readOnly}
        >
          Submit Evidence
        </button>
      </div>
    );
  };

  const renderStep = (step: ChecklistStep) => {
    const isExpanded = expandedStep === step.id;
    const canStart = canStartStep(step);

    return (
      <div
        key={step.id}
        className={`checklist-item ${getStatusClass(step.status)} ${!step.applies ? 'not-applicable' : ''} ${!step.dependencies_met ? 'dependencies-unmet' : ''}`}
      >
        <div className="step-header" onClick={() => toggleExpand(step.id)}>
          <span className="status-icon">{getStatusIcon(step.status)}</span>
          <div className="step-title">
            <strong>{step.step}</strong>
            {step.critical && <span className="critical-badge">CRITICAL</span>}
            {step.parallel_group && (
              <span className="parallel-badge">⚡ Parallel: {step.parallel_group}</span>
            )}
          </div>
          <div className="step-meta">
            <span className="time-estimate">{step.estimated_time_minutes} min</span>
            <span className="role-badge">{step.assigned_to}</span>
          </div>
        </div>

        {isExpanded && (
          <div className="step-details">
            <p className="step-description">{step.description}</p>

            {step.dependencies && step.dependencies.length > 0 && (
              <div className="dependencies">
                <strong>Dependencies:</strong> {step.dependencies.join(', ')}
                {!step.dependencies_met && <span className="warning"> (Not all complete)</span>}
              </div>
            )}

            {step.started_at && (
              <div className="time-tracking">
                <strong>Time:</strong> {calculateTimeSpent(step)} / {step.estimated_time_minutes} min estimated
              </div>
            )}

            {step.assigned_user && (
              <div className="assigned-user">
                <strong>Assigned to:</strong> {step.assigned_user}
              </div>
            )}

            {step.notes && (
              <div className="notes">
                <strong>Notes:</strong> {step.notes}
              </div>
            )}

            {step.blocked_reason && (
              <div className="blocked-reason">
                <strong>Blocked Reason:</strong> {step.blocked_reason}
              </div>
            )}

            {step.status === 'in_progress' && renderEvidenceForm(step)}

            {step.evidence && step.evidence.length > 0 && (
              <div className="collected-evidence">
                <strong>Collected Evidence:</strong>
                {step.evidence.map((ev, idx) => (
                  <div key={idx} className="evidence-item">
                    {ev.name}: {JSON.stringify(ev.value)}
                  </div>
                ))}
              </div>
            )}

            {!readOnly && (
              <div className="step-actions">
                {canStart && (
                  <button
                    className="btn btn-primary"
                    onClick={() => handleStartStep(step.id)}
                  >
                    Start Step
                  </button>
                )}

                {step.status === 'in_progress' && step.assigned_user === currentUser && (
                  <>
                    <button
                      className="btn btn-success"
                      onClick={() => handleCompleteStep(step.id)}
                    >
                      Complete
                    </button>
                    <button
                      className="btn btn-warning"
                      onClick={() => {
                        const reason = prompt('Enter blocked reason:');
                        if (reason) handleBlockStep(step.id, reason);
                      }}
                    >
                      Block
                    </button>
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const { groups, ungrouped } = groupStepsByParallel(steps);

  return (
    <div className="enhanced-checklist">
      <h3>Investigation Checklist</h3>

      {ungrouped.map(step => renderStep(step))}

      {Object.entries(groups).map(([groupName, groupSteps]) => (
        <div key={groupName} className="parallel-group">
          <div className="parallel-group-header">
            <span className="parallel-icon">⚡</span>
            <strong>Parallel Group: {groupName}</strong>
            <span className="parallel-note">(These steps can run simultaneously)</span>
          </div>
          {groupSteps.map(step => renderStep(step))}
        </div>
      ))}
    </div>
  );
};

export default EnhancedChecklist;
