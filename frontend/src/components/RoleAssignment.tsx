/**
 * Role Assignment Component
 *
 * Role management component with:
 * - Grid of role cards
 * - Required badge for mandatory roles
 * - Assignment status display
 * - Assign/Reassign buttons
 * - Modal for user input
 */

import React, { useState } from 'react';
import './RoleAssignment.css';

export interface Role {
  name: string;
  description: string;
  required: boolean;
  escalation_triggers?: string[];
  assigned_user?: string;
  assigned_at?: string;
}

interface RoleAssignmentProps {
  roles: { [key: string]: Role };
  onAssign: (roleName: string, user: string) => void;
  readOnly?: boolean;
}

export const RoleAssignment: React.FC<RoleAssignmentProps> = ({
  roles,
  onAssign,
  readOnly = false
}) => {
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [username, setUsername] = useState('');

  const handleAssignClick = (roleName: string) => {
    setSelectedRole(roleName);
    setUsername('');
  };

  const handleAssignSubmit = () => {
    if (selectedRole && username.trim()) {
      onAssign(selectedRole, username.trim());
      setSelectedRole(null);
      setUsername('');
    }
  };

  const handleCancel = () => {
    setSelectedRole(null);
    setUsername('');
  };

  return (
    <div className="role-assignment">
      <h3>Role Assignments</h3>
      <p className="role-description">
        Assign team members to incident response roles
      </p>

      <div className="role-grid">
        {Object.entries(roles).map(([roleKey, role]) => (
          <div
            key={roleKey}
            className={`role-card ${role.assigned_user ? 'assigned' : 'unassigned'} ${role.required ? 'required' : 'optional'}`}
          >
            <div className="role-header">
              <h4>{role.name}</h4>
              {role.required && <span className="required-badge">REQUIRED</span>}
            </div>

            <p className="role-desc">{role.description}</p>

            <div className="role-status">
              {role.assigned_user ? (
                <>
                  <div className="assigned-info">
                    <span className="status-icon">✓</span>
                    <div>
                      <strong>{role.assigned_user}</strong>
                      {role.assigned_at && (
                        <div className="assigned-time">
                          Assigned: {new Date(role.assigned_at).toLocaleString()}
                        </div>
                      )}
                    </div>
                  </div>
                  {!readOnly && (
                    <button
                      className="btn btn-secondary"
                      onClick={() => handleAssignClick(roleKey)}
                    >
                      Reassign
                    </button>
                  )}
                </>
              ) : (
                <>
                  <span className="unassigned-text">Not assigned</span>
                  {!readOnly && (
                    <button
                      className="btn btn-primary"
                      onClick={() => handleAssignClick(roleKey)}
                    >
                      Assign
                    </button>
                  )}
                </>
              )}
            </div>

            {role.escalation_triggers && role.escalation_triggers.length > 0 && (
              <div className="escalation-triggers">
                <small>
                  <strong>Escalation triggers:</strong> {role.escalation_triggers.join(', ')}
                </small>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Assignment Modal */}
      {selectedRole && (
        <div className="modal-overlay" onClick={handleCancel}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Assign {roles[selectedRole]?.name}</h3>
            <p>{roles[selectedRole]?.description}</p>

            <div className="form-group">
              <label htmlFor="username">Username/Email:</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username or email"
                autoFocus
                onKeyPress={(e) => {
                  if (e.key === 'Enter') handleAssignSubmit();
                }}
              />
            </div>

            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={handleCancel}>
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleAssignSubmit}
                disabled={!username.trim()}
              >
                Assign
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoleAssignment;
