import React, { useState } from 'react';
import './HandoffPanel.css';

export interface HandoffRequirement {
  key: string;
  description: string;
  met: boolean;
}

export interface PendingHandoff {
  from_phase: string;
  to_phase: string;
  from_role: string;
  to_role: string;
  initiated_by: string;
  initiated_at: string;
  handoff_notes?: string;
  checklist_completion_at_handoff: number;
}

interface HandoffPanelProps {
  currentPhase: string;
  nextPhase: string;
  requirements: HandoffRequirement[];
  onInitiateHandoff: (notes: string) => void;
  onSignOff: (notes: string) => void;
  pendingHandoff?: PendingHandoff | null;
  canInitiate: boolean;
  canSignOff: boolean;
  readOnly?: boolean;
}

export const HandoffPanel: React.FC<HandoffPanelProps> = ({
  currentPhase,
  nextPhase,
  requirements,
  onInitiateHandoff,
  onSignOff,
  pendingHandoff,
  canInitiate,
  canSignOff,
  readOnly = false
}) => {
  const [handoffNotes, setHandoffNotes] = useState('');
  const [signOffNotes, setSignOffNotes] = useState('');
  const [showInitiateModal, setShowInitiateModal] = useState(false);
  const [showSignOffModal, setShowSignOffModal] = useState(false);

  const allRequirementsMet = requirements.every(req => req.met);
  const canProceed = allRequirementsMet && canInitiate && !readOnly;

  const handleInitiateClick = () => {
    if (canProceed) {
      setShowInitiateModal(true);
    }
  };

  const handleInitiateSubmit = () => {
    onInitiateHandoff(handoffNotes);
    setHandoffNotes('');
    setShowInitiateModal(false);
  };

  const handleSignOffClick = () => {
    if (canSignOff && !readOnly) {
      setShowSignOffModal(true);
    }
  };

  const handleSignOffSubmit = () => {
    onSignOff(signOffNotes);
    setSignOffNotes('');
    setShowSignOffModal(false);
  };

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  return (
    <div className="handoff-panel">
      <div className="handoff-header">
        <h3>Phase Handoff</h3>
        <div className="phase-transition">
          <span className="phase-name current">{currentPhase}</span>
          <span className="arrow">→</span>
          <span className="phase-name next">{nextPhase}</span>
        </div>
      </div>

      {/* Requirements Checklist */}
      <div className="requirements-section">
        <h4>Handoff Requirements</h4>
        <div className="requirements-list">
          {requirements.map((req) => (
            <div
              key={req.key}
              className={`requirement-item ${req.met ? 'met' : 'unmet'}`}
            >
              <span className="requirement-icon">
                {req.met ? '✓' : '○'}
              </span>
              <span className="requirement-description">{req.description}</span>
              <span className={`requirement-status ${req.met ? 'met' : 'unmet'}`}>
                {req.met ? 'Met' : 'Not Met'}
              </span>
            </div>
          ))}
        </div>

        {!allRequirementsMet && (
          <div className="requirements-warning">
            <span className="warning-icon">⚠</span>
            <span>All requirements must be met before initiating handoff</span>
          </div>
        )}
      </div>

      {/* Pending Handoff Display */}
      {pendingHandoff && (
        <div className="pending-handoff">
          <div className="pending-header">
            <span className="pending-icon">⏳</span>
            <h4>Handoff Pending Sign-Off</h4>
          </div>

          <div className="pending-details">
            <div className="detail-row">
              <span className="label">Initiated By:</span>
              <span className="value">{pendingHandoff.initiated_by}</span>
            </div>
            <div className="detail-row">
              <span className="label">Initiated At:</span>
              <span className="value">{formatDateTime(pendingHandoff.initiated_at)}</span>
            </div>
            <div className="detail-row">
              <span className="label">From Role:</span>
              <span className="value">{pendingHandoff.from_role}</span>
            </div>
            <div className="detail-row">
              <span className="label">To Role:</span>
              <span className="value">{pendingHandoff.to_role}</span>
            </div>
            <div className="detail-row">
              <span className="label">Checklist Completion:</span>
              <span className="value">{pendingHandoff.checklist_completion_at_handoff}%</span>
            </div>
            {pendingHandoff.handoff_notes && (
              <div className="detail-row notes">
                <span className="label">Notes:</span>
                <span className="value">{pendingHandoff.handoff_notes}</span>
              </div>
            )}
          </div>

          {canSignOff && !readOnly && (
            <button
              className="btn btn-primary sign-off-btn"
              onClick={handleSignOffClick}
            >
              Sign Off on Handoff
            </button>
          )}
        </div>
      )}

      {/* Initiate Handoff Button */}
      {!pendingHandoff && (
        <div className="handoff-actions">
          <button
            className={`btn btn-primary initiate-btn ${!canProceed ? 'disabled' : ''}`}
            onClick={handleInitiateClick}
            disabled={!canProceed}
            title={
              !allRequirementsMet
                ? 'All requirements must be met'
                : !canInitiate
                ? 'You do not have permission to initiate handoff'
                : ''
            }
          >
            Initiate Handoff to {nextPhase}
          </button>
        </div>
      )}

      {/* Initiate Handoff Modal */}
      {showInitiateModal && (
        <div className="modal-overlay" onClick={() => setShowInitiateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Initiate Handoff</h3>
            <p>
              You are about to hand off the <strong>{currentPhase}</strong> phase to the{' '}
              <strong>{nextPhase}</strong> phase.
            </p>

            <div className="form-group">
              <label htmlFor="handoff-notes">Handoff Notes (optional)</label>
              <textarea
                id="handoff-notes"
                value={handoffNotes}
                onChange={(e) => setHandoffNotes(e.target.value)}
                placeholder="Provide context or important information for the next phase team..."
                rows={4}
              />
            </div>

            <div className="modal-actions">
              <button
                className="btn btn-secondary"
                onClick={() => setShowInitiateModal(false)}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleInitiateSubmit}
              >
                Confirm Handoff
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Sign-Off Modal */}
      {showSignOffModal && (
        <div className="modal-overlay" onClick={() => setShowSignOffModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Sign Off on Handoff</h3>
            <p>
              You are accepting the handoff and taking responsibility for the{' '}
              <strong>{nextPhase}</strong> phase.
            </p>

            <div className="form-group">
              <label htmlFor="signoff-notes">Sign-Off Notes (optional)</label>
              <textarea
                id="signoff-notes"
                value={signOffNotes}
                onChange={(e) => setSignOffNotes(e.target.value)}
                placeholder="Acknowledge receipt and any initial observations..."
                rows={4}
              />
            </div>

            <div className="modal-actions">
              <button
                className="btn btn-secondary"
                onClick={() => setShowSignOffModal(false)}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleSignOffSubmit}
              >
                Sign Off
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
