import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { incidentAPI } from '../api/client';

type IncidentType = 'phishing' | 'malware' | 'account_compromise' | 'data_breach' | 'ransomware' | 'insider_threat' | 'ddos' | 'unauthorized_access';

const INCIDENT_TYPES = [
  { value: 'phishing', label: 'Phishing (User-Reported Email)' },
  { value: 'malware', label: 'Malware Infection' },
  { value: 'account_compromise', label: 'Account Compromise' },
  { value: 'data_breach', label: 'Data Breach' },
  { value: 'ransomware', label: 'Ransomware Attack' },
  { value: 'insider_threat', label: 'Insider Threat' },
  { value: 'ddos', label: 'DDoS Attack' },
  { value: 'unauthorized_access', label: 'Unauthorized Access' },
];

const IntakeForm: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [incidentType, setIncidentType] = useState<IncidentType>('phishing');
  const [formData, setFormData] = useState<any>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload: any = { incident_type: incidentType };

      // Map form data to the appropriate data field based on incident type
      const dataField = `${incidentType}_data`;
      payload[dataField] = formData;

      const incident = await incidentAPI.createIncident(payload);
      navigate(`/investigation/${incident.incident_id}`);
    } catch (err: any) {
      // Handle both string and array error formats from FastAPI
      let errorMessage = 'Failed to create incident';

      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (Array.isArray(detail)) {
          // FastAPI validation errors are arrays
          errorMessage = detail.map((e: any) => `${e.loc?.join(' > ') || 'Field'}: ${e.msg}`).join(', ');
        }
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }));
  };

  const handleIncidentTypeChange = (newType: IncidentType) => {
    setIncidentType(newType);
    setFormData({}); // Reset form data when changing type
  };

  const renderPhishingForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="reporting_user_email">
          Reporting User Email <span className="required">*</span>
        </label>
        <input
          type="email"
          id="reporting_user_email"
          value={formData.reporting_user_email || ''}
          onChange={(e) => handleChange('reporting_user_email', e.target.value)}
          required
          placeholder="user@example.com"
        />
      </div>

      <div className="form-group">
        <label>Did the user click a link?</label>
        <div className="radio-group">
          {['yes', 'no', 'unknown'].map((option) => (
            <label key={option} className="radio-label">
              <input
                type="radio"
                name="user_clicked"
                value={option}
                checked={formData.user_clicked === option}
                onChange={(e) => handleChange('user_clicked', e.target.value)}
              />
              {option.charAt(0).toUpperCase() + option.slice(1)}
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Did the user open an attachment?</label>
        <div className="radio-group">
          {['yes', 'no', 'unknown'].map((option) => (
            <label key={option} className="radio-label">
              <input
                type="radio"
                name="attachment_opened"
                value={option}
                checked={formData.attachment_opened === option}
                onChange={(e) => handleChange('attachment_opened', e.target.value)}
              />
              {option.charAt(0).toUpperCase() + option.slice(1)}
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Did the user enter credentials?</label>
        <div className="radio-group">
          {['yes', 'no', 'unknown'].map((option) => (
            <label key={option} className="radio-label">
              <input
                type="radio"
                name="credentials_entered"
                value={option}
                checked={formData.credentials_entered === option}
                onChange={(e) => handleChange('credentials_entered', e.target.value)}
              />
              {option.charAt(0).toUpperCase() + option.slice(1)}
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="headers_available" className="checkbox-label">
          <input
            type="checkbox"
            id="headers_available"
            checked={formData.headers_available || false}
            onChange={(e) => handleChange('headers_available', e.target.checked)}
          />
          Email headers available for analysis
        </label>
      </div>
    </>
  );

  const renderMalwareForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="reporting_user_email">
          Reporting User Email <span className="required">*</span>
        </label>
        <input
          type="email"
          id="reporting_user_email"
          value={formData.reporting_user_email || ''}
          onChange={(e) => handleChange('reporting_user_email', e.target.value)}
          required
          placeholder="user@example.com"
        />
      </div>

      <div className="form-group">
        <label>Was the file executed?</label>
        <div className="radio-group">
          {['yes', 'no', 'unknown'].map((option) => (
            <label key={option} className="radio-label">
              <input
                type="radio"
                name="file_executed"
                value={option}
                checked={formData.file_executed === option}
                onChange={(e) => handleChange('file_executed', e.target.value)}
              />
              {option.charAt(0).toUpperCase() + option.slice(1)}
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="suspicious_behavior">Describe Suspicious Behavior</label>
        <textarea
          id="suspicious_behavior"
          value={formData.suspicious_behavior || ''}
          onChange={(e) => handleChange('suspicious_behavior', e.target.value)}
          rows={4}
          placeholder="e.g., System slowdown, unknown processes, network connections..."
        />
      </div>
    </>
  );

  const renderAccountCompromiseForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="affected_user_email">
          Affected User Email <span className="required">*</span>
        </label>
        <input
          type="email"
          id="affected_user_email"
          value={formData.affected_user_email || ''}
          onChange={(e) => handleChange('affected_user_email', e.target.value)}
          required
          placeholder="compromised@example.com"
        />
      </div>

      <div className="form-group">
        <label htmlFor="suspicious_activities">Describe Suspicious Activities <span className="required">*</span></label>
        <textarea
          id="suspicious_activities"
          value={formData.suspicious_activities || ''}
          onChange={(e) => handleChange('suspicious_activities', e.target.value)}
          required
          rows={4}
          placeholder="e.g., Login from unusual location, unauthorized email forwards..."
        />
      </div>
    </>
  );

  const renderDataBreachForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="data_type_affected">
          Type of Data Affected <span className="required">*</span>
        </label>
        <input
          type="text"
          id="data_type_affected"
          value={formData.data_type_affected || ''}
          onChange={(e) => handleChange('data_type_affected', e.target.value)}
          required
          placeholder="e.g., PII, credentials, financial records..."
        />
      </div>

      <div className="form-group">
        <label htmlFor="number_of_records">Estimated Number of Records Affected</label>
        <input
          type="number"
          id="number_of_records"
          value={formData.number_of_records || ''}
          onChange={(e) => handleChange('number_of_records', parseInt(e.target.value))}
          placeholder="e.g., 1000"
        />
      </div>

      <div className="form-group">
        <label htmlFor="breach_source">How was the data breached?</label>
        <textarea
          id="breach_source"
          value={formData.breach_source || ''}
          onChange={(e) => handleChange('breach_source', e.target.value)}
          rows={4}
          placeholder="e.g., SQL injection, exposed S3 bucket..."
        />
      </div>
    </>
  );

  const renderRansomwareForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="reporting_user_email">
          Reporting User Email <span className="required">*</span>
        </label>
        <input
          type="email"
          id="reporting_user_email"
          value={formData.reporting_user_email || ''}
          onChange={(e) => handleChange('reporting_user_email', e.target.value)}
          required
          placeholder="user@example.com"
        />
      </div>

      <div className="form-group">
        <label>Are files encrypted?</label>
        <div className="radio-group">
          {['yes', 'no', 'unknown'].map((option) => (
            <label key={option} className="radio-label">
              <input
                type="radio"
                name="files_encrypted"
                value={option}
                checked={formData.files_encrypted === option}
                onChange={(e) => handleChange('files_encrypted', e.target.value)}
              />
              {option.charAt(0).toUpperCase() + option.slice(1)}
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Was a ransom note found?</label>
        <div className="radio-group">
          {['yes', 'no', 'unknown'].map((option) => (
            <label key={option} className="radio-label">
              <input
                type="radio"
                name="ransom_note_present"
                value={option}
                checked={formData.ransom_note_present === option}
                onChange={(e) => handleChange('ransom_note_present', e.target.value)}
              />
              {option.charAt(0).toUpperCase() + option.slice(1)}
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="ransom_amount">Ransom Amount Demanded</label>
        <input
          type="text"
          id="ransom_amount"
          value={formData.ransom_amount || ''}
          onChange={(e) => handleChange('ransom_amount', e.target.value)}
          placeholder="e.g., 5 BTC or $50,000"
        />
      </div>
    </>
  );

  const renderInsiderThreatForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="suspect_user_email">
          Suspect User Email <span className="required">*</span>
        </label>
        <input
          type="email"
          id="suspect_user_email"
          value={formData.suspect_user_email || ''}
          onChange={(e) => handleChange('suspect_user_email', e.target.value)}
          required
          placeholder="suspect@example.com"
        />
      </div>

      <div className="form-group">
        <label htmlFor="suspicious_activity">
          Describe Suspicious Activity <span className="required">*</span>
        </label>
        <textarea
          id="suspicious_activity"
          value={formData.suspicious_activity || ''}
          onChange={(e) => handleChange('suspicious_activity', e.target.value)}
          required
          rows={4}
          placeholder="e.g., Accessing sensitive files outside normal duties..."
        />
      </div>

      <div className="form-group">
        <label>Unusual data access detected?</label>
        <div className="radio-group">
          {['yes', 'no', 'unknown'].map((option) => (
            <label key={option} className="radio-label">
              <input
                type="radio"
                name="data_access_anomaly"
                value={option}
                checked={formData.data_access_anomaly === option}
                onChange={(e) => handleChange('data_access_anomaly', e.target.value)}
              />
              {option.charAt(0).toUpperCase() + option.slice(1)}
            </label>
          ))}
        </div>
      </div>
    </>
  );

  const renderDDoSForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="affected_service">
          Affected Service <span className="required">*</span>
        </label>
        <input
          type="text"
          id="affected_service"
          value={formData.affected_service || ''}
          onChange={(e) => handleChange('affected_service', e.target.value)}
          required
          placeholder="e.g., Website, API endpoint..."
        />
      </div>

      <div className="form-group">
        <label htmlFor="attack_type">Type of DDoS Attack (if known)</label>
        <input
          type="text"
          id="attack_type"
          value={formData.attack_type || ''}
          onChange={(e) => handleChange('attack_type', e.target.value)}
          placeholder="e.g., SYN flood, HTTP flood..."
        />
      </div>

      <div className="form-group">
        <label>Is the service currently impacted?</label>
        <div className="radio-group">
          {['yes', 'no', 'unknown'].map((option) => (
            <label key={option} className="radio-label">
              <input
                type="radio"
                name="service_impacted"
                value={option}
                checked={formData.service_impacted === option}
                onChange={(e) => handleChange('service_impacted', e.target.value)}
              />
              {option.charAt(0).toUpperCase() + option.slice(1)}
            </label>
          ))}
        </div>
      </div>
    </>
  );

  const renderUnauthorizedAccessForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="affected_system">
          Affected System <span className="required">*</span>
        </label>
        <input
          type="text"
          id="affected_system"
          value={formData.affected_system || ''}
          onChange={(e) => handleChange('affected_system', e.target.value)}
          required
          placeholder="e.g., Production server, Database..."
        />
      </div>

      <div className="form-group">
        <label htmlFor="access_method">How was access obtained?</label>
        <input
          type="text"
          id="access_method"
          value={formData.access_method || ''}
          onChange={(e) => handleChange('access_method', e.target.value)}
          placeholder="e.g., Stolen credentials, exploited vulnerability..."
        />
      </div>

      <div className="form-group">
        <label htmlFor="unauthorized_actions">What actions were taken?</label>
        <textarea
          id="unauthorized_actions"
          value={formData.unauthorized_actions || ''}
          onChange={(e) => handleChange('unauthorized_actions', e.target.value)}
          rows={4}
          placeholder="e.g., Files accessed, commands executed..."
        />
      </div>
    </>
  );

  const renderFormFields = () => {
    switch (incidentType) {
      case 'phishing':
        return renderPhishingForm();
      case 'malware':
        return renderMalwareForm();
      case 'account_compromise':
        return renderAccountCompromiseForm();
      case 'data_breach':
        return renderDataBreachForm();
      case 'ransomware':
        return renderRansomwareForm();
      case 'insider_threat':
        return renderInsiderThreatForm();
      case 'ddos':
        return renderDDoSForm();
      case 'unauthorized_access':
        return renderUnauthorizedAccessForm();
      default:
        return null;
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h1>IR AI Assistant</h1>
        <p className="subtitle">Guided Incident Response</p>
      </div>

      <div className="card">
        <h2>Initial Triage Intake</h2>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="incident_type">
              Incident Type <span className="required">*</span>
            </label>
            <select
              id="incident_type"
              value={incidentType}
              onChange={(e) => handleIncidentTypeChange(e.target.value as IncidentType)}
              className="incident-type-select"
            >
              {INCIDENT_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {renderFormFields()}

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating Incident...' : 'Start Investigation'}
          </button>
        </form>
      </div>

      <div className="info-box">
        <h4>What happens next?</h4>
        <p>
          The AI assistant will analyze your incident data and provide:
        </p>
        <ul>
          <li>What we know (confirmed facts)</li>
          <li>What we need to determine (information gaps)</li>
          <li>Recommended investigative steps</li>
          <li>Risk assessment</li>
        </ul>
      </div>
    </div>
  );
};

export default IntakeForm;
