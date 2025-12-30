import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { incidentAPI } from '../api/client';

type IncidentType =
  | 'phishing'
  | 'malware'
  | 'account_compromise'
  | 'data_breach'
  | 'ransomware'
  | 'insider_threat'
  | 'ddos'
  | 'unauthorized_access'
  | 'bec'
  | 'web_application_attack'
  | 'data_exfiltration'
  | 'supply_chain_attack'
  | 'cloud_account_compromise'
  | 'api_security_breach'
  | 'credential_stuffing'
  | 'zero_day_exploit'
  | 'container_compromise'
  | 'iot_device_compromise'
  | 'backup_system_compromise'
  | 'dns_hijacking'
  | 'saas_application_compromise'
  | 'mobile_device_compromise'
  | 'regulatory_compliance_incident';

const INCIDENT_TYPES = [
  { value: 'account_compromise', label: 'Account Compromise' },
  { value: 'api_security_breach', label: 'API Security Breach' },
  { value: 'backup_system_compromise', label: 'Backup System Compromise' },
  { value: 'bec', label: 'Business Email Compromise (BEC)' },
  { value: 'cloud_account_compromise', label: 'Cloud Account Compromise' },
  { value: 'container_compromise', label: 'Container/Kubernetes Compromise' },
  { value: 'credential_stuffing', label: 'Credential Stuffing' },
  { value: 'data_breach', label: 'Data Breach' },
  { value: 'data_exfiltration', label: 'Data Exfiltration' },
  { value: 'ddos', label: 'DDoS Attack' },
  { value: 'dns_hijacking', label: 'DNS Hijacking' },
  { value: 'insider_threat', label: 'Insider Threat' },
  { value: 'iot_device_compromise', label: 'IoT Device Compromise' },
  { value: 'malware', label: 'Malware Infection' },
  { value: 'mobile_device_compromise', label: 'Mobile Device Compromise' },
  { value: 'phishing', label: 'Phishing (User-Reported Email)' },
  { value: 'ransomware', label: 'Ransomware Attack' },
  { value: 'regulatory_compliance_incident', label: 'Regulatory Compliance Incident' },
  { value: 'saas_application_compromise', label: 'SaaS Application Compromise' },
  { value: 'supply_chain_attack', label: 'Supply Chain Attack' },
  { value: 'unauthorized_access', label: 'Unauthorized Access' },
  { value: 'web_application_attack', label: 'Web Application Attack' },
  { value: 'zero_day_exploit', label: 'Zero-Day Exploit' },
];

const IntakeForm: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [incidentType, setIncidentType] = useState<IncidentType>('account_compromise');
  const [formData, setFormData] = useState<any>({});

  // Check for pre-selected incident type from URL
  useEffect(() => {
    const typeParam = searchParams.get('type');
    if (typeParam && INCIDENT_TYPES.some(t => t.value === typeParam)) {
      setIncidentType(typeParam as IncidentType);
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload: any = { incident_type: incidentType };

      // Map form data to the appropriate data field based on incident type
      const dataField = `${incidentType}_data`;

      // Process form data - convert datetime-local to ISO format
      const processedData = { ...formData };

      // Convert datetime-local to ISO 8601 format
      if (processedData.time_of_discovery) {
        processedData.time_of_discovery = new Date(processedData.time_of_discovery).toISOString();
      }

      // Ensure numeric fields are numbers, not strings
      if (processedData.estimated_records !== undefined && processedData.estimated_records !== '') {
        const parsed = typeof processedData.estimated_records === 'string'
          ? parseInt(processedData.estimated_records, 10)
          : processedData.estimated_records;
        processedData.estimated_records = isNaN(parsed) ? 0 : parsed;
      }

      payload[dataField] = processedData;

      console.log('Form data:', formData); // Debug log
      console.log('Processed data:', processedData); // Debug log
      console.log('Submitting payload:', JSON.stringify(payload, null, 2)); // Debug log

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

      console.error('Error creating incident:', err.response?.data); // Debug log
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: any) => {
    console.log(`Field changed: ${field} =`, value); // Debug log
    setFormData((prev: any) => {
      const updated = { ...prev, [field]: value };
      console.log('Updated formData:', updated); // Debug log
      return updated;
    });
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
        <label htmlFor="estimated_records">
          Estimated Number of Records Affected <span className="required">*</span>
        </label>
        <input
          type="number"
          id="estimated_records"
          value={formData.estimated_records || ''}
          onChange={(e) => handleChange('estimated_records', e.target.value)}
          required
          placeholder="e.g., 1000"
          min="0"
        />
      </div>

      <div className="form-group">
        <label htmlFor="breach_method">
          How was the data breached? <span className="required">*</span>
        </label>
        <textarea
          id="breach_method"
          value={formData.breach_method || ''}
          onChange={(e) => handleChange('breach_method', e.target.value)}
          required
          rows={4}
          placeholder="e.g., SQL injection, exposed S3 bucket, phishing..."
        />
      </div>

      <div className="form-group">
        <label htmlFor="time_of_discovery">
          When was the breach discovered? <span className="required">*</span>
        </label>
        <input
          type="datetime-local"
          id="time_of_discovery"
          value={formData.time_of_discovery || ''}
          onChange={(e) => handleChange('time_of_discovery', e.target.value)}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="breach_source">Additional Details</label>
        <textarea
          id="breach_source"
          value={formData.breach_source || ''}
          onChange={(e) => handleChange('breach_source', e.target.value)}
          rows={4}
          placeholder="Any additional context about the breach..."
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

  const renderBECForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="compromised_account_email">
          Compromised Account Email <span className="required">*</span>
        </label>
        <input
          type="email"
          id="compromised_account_email"
          value={formData.compromised_account_email || ''}
          onChange={(e) => handleChange('compromised_account_email', e.target.value)}
          required
          placeholder="compromised@example.com"
        />
      </div>

      <div className="form-group">
        <label htmlFor="fraudulent_request_type">
          Fraudulent Request Type <span className="required">*</span>
        </label>
        <input
          type="text"
          id="fraudulent_request_type"
          value={formData.fraudulent_request_type || ''}
          onChange={(e) => handleChange('fraudulent_request_type', e.target.value)}
          required
          placeholder="e.g., Wire transfer, gift cards, payroll change"
        />
      </div>

      <div className="form-group">
        <label htmlFor="target_recipient_email">
          Target Recipient Email <span className="required">*</span>
        </label>
        <input
          type="email"
          id="target_recipient_email"
          value={formData.target_recipient_email || ''}
          onChange={(e) => handleChange('target_recipient_email', e.target.value)}
          required
          placeholder="recipient@example.com"
        />
      </div>

      <div className="form-group">
        <label htmlFor="impersonated_executive">Impersonated Executive</label>
        <input
          type="text"
          id="impersonated_executive"
          value={formData.impersonated_executive || ''}
          onChange={(e) => handleChange('impersonated_executive', e.target.value)}
          placeholder="e.g., CEO, CFO"
        />
      </div>
    </>
  );

  const renderWebApplicationAttackForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="affected_application">
          Affected Application <span className="required">*</span>
        </label>
        <input
          type="text"
          id="affected_application"
          value={formData.affected_application || ''}
          onChange={(e) => handleChange('affected_application', e.target.value)}
          required
          placeholder="e.g., https://example.com or Application name"
        />
      </div>

      <div className="form-group">
        <label htmlFor="attack_type">
          Attack Type <span className="required">*</span>
        </label>
        <input
          type="text"
          id="attack_type"
          value={formData.attack_type || ''}
          onChange={(e) => handleChange('attack_type', e.target.value)}
          required
          placeholder="e.g., SQL injection, XSS, CSRF"
        />
      </div>

      <div className="form-group">
        <label htmlFor="attack_vector">Attack Vector</label>
        <textarea
          id="attack_vector"
          value={formData.attack_vector || ''}
          onChange={(e) => handleChange('attack_vector', e.target.value)}
          rows={3}
          placeholder="How was the attack delivered?"
        />
      </div>
    </>
  );

  const renderDataExfiltrationForm = () => (
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
          placeholder="System from which data was exfiltrated"
        />
      </div>

      <div className="form-group">
        <label htmlFor="data_classification">
          Data Classification <span className="required">*</span>
        </label>
        <input
          type="text"
          id="data_classification"
          value={formData.data_classification || ''}
          onChange={(e) => handleChange('data_classification', e.target.value)}
          required
          placeholder="e.g., Public, Internal, Confidential, Secret"
        />
      </div>

      <div className="form-group">
        <label htmlFor="exfiltration_method">
          Exfiltration Method <span className="required">*</span>
        </label>
        <input
          type="text"
          id="exfiltration_method"
          value={formData.exfiltration_method || ''}
          onChange={(e) => handleChange('exfiltration_method', e.target.value)}
          required
          placeholder="e.g., FTP, HTTP, email, cloud storage"
        />
      </div>

      <div className="form-group">
        <label htmlFor="estimated_data_volume">Estimated Data Volume</label>
        <input
          type="text"
          id="estimated_data_volume"
          value={formData.estimated_data_volume || ''}
          onChange={(e) => handleChange('estimated_data_volume', e.target.value)}
          placeholder="e.g., 100GB, 1 million records"
        />
      </div>
    </>
  );

  const renderSupplyChainAttackForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="affected_vendor">
          Affected Vendor <span className="required">*</span>
        </label>
        <input
          type="text"
          id="affected_vendor"
          value={formData.affected_vendor || ''}
          onChange={(e) => handleChange('affected_vendor', e.target.value)}
          required
          placeholder="Name of affected vendor/supplier"
        />
      </div>

      <div className="form-group">
        <label htmlFor="compromised_component">
          Compromised Component <span className="required">*</span>
        </label>
        <input
          type="text"
          id="compromised_component"
          value={formData.compromised_component || ''}
          onChange={(e) => handleChange('compromised_component', e.target.value)}
          required
          placeholder="e.g., Software library, hardware device"
        />
      </div>

      <div className="form-group">
        <label htmlFor="attack_vector">
          Attack Vector <span className="required">*</span>
        </label>
        <textarea
          id="attack_vector"
          value={formData.attack_vector || ''}
          onChange={(e) => handleChange('attack_vector', e.target.value)}
          required
          rows={3}
          placeholder="How was the supply chain compromised?"
        />
      </div>
    </>
  );

  const renderCloudAccountCompromiseForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="cloud_provider">
          Cloud Provider <span className="required">*</span>
        </label>
        <input
          type="text"
          id="cloud_provider"
          value={formData.cloud_provider || ''}
          onChange={(e) => handleChange('cloud_provider', e.target.value)}
          required
          placeholder="e.g., AWS, Azure, GCP"
        />
      </div>

      <div className="form-group">
        <label htmlFor="compromised_account_id">
          Compromised Account ID <span className="required">*</span>
        </label>
        <input
          type="text"
          id="compromised_account_id"
          value={formData.compromised_account_id || ''}
          onChange={(e) => handleChange('compromised_account_id', e.target.value)}
          required
          placeholder="Account/subscription ID"
        />
      </div>

      <div className="form-group">
        <label htmlFor="account_type">
          Account Type <span className="required">*</span>
        </label>
        <input
          type="text"
          id="account_type"
          value={formData.account_type || ''}
          onChange={(e) => handleChange('account_type', e.target.value)}
          required
          placeholder="e.g., Root, Admin, Service account"
        />
      </div>

      <div className="form-group">
        <label htmlFor="unauthorized_actions">Unauthorized Actions</label>
        <textarea
          id="unauthorized_actions"
          value={formData.unauthorized_actions || ''}
          onChange={(e) => handleChange('unauthorized_actions', e.target.value)}
          rows={3}
          placeholder="Unauthorized actions observed"
        />
      </div>
    </>
  );

  const renderAPISecurityBreachForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="affected_api">
          Affected API <span className="required">*</span>
        </label>
        <input
          type="text"
          id="affected_api"
          value={formData.affected_api || ''}
          onChange={(e) => handleChange('affected_api', e.target.value)}
          required
          placeholder="API endpoint or service affected"
        />
      </div>

      <div className="form-group">
        <label htmlFor="attack_type">
          Attack Type <span className="required">*</span>
        </label>
        <input
          type="text"
          id="attack_type"
          value={formData.attack_type || ''}
          onChange={(e) => handleChange('attack_type', e.target.value)}
          required
          placeholder="e.g., Broken auth, excessive data exposure, rate limit abuse"
        />
      </div>

      <div className="form-group">
        <label htmlFor="api_authentication_method">API Authentication Method</label>
        <input
          type="text"
          id="api_authentication_method"
          value={formData.api_authentication_method || ''}
          onChange={(e) => handleChange('api_authentication_method', e.target.value)}
          placeholder="e.g., API keys, OAuth, JWT"
        />
      </div>
    </>
  );

  const renderCredentialStuffingForm = () => (
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
          placeholder="Service/application targeted"
        />
      </div>

      <div className="form-group">
        <label htmlFor="attack_volume">Attack Volume</label>
        <input
          type="text"
          id="attack_volume"
          value={formData.attack_volume || ''}
          onChange={(e) => handleChange('attack_volume', e.target.value)}
          placeholder="Number of login attempts observed"
        />
      </div>

      <div className="form-group">
        <label htmlFor="source_ips_count">Source IPs Count</label>
        <input
          type="number"
          id="source_ips_count"
          value={formData.source_ips_count || ''}
          onChange={(e) => handleChange('source_ips_count', e.target.value)}
          placeholder="Number of unique source IPs"
          min="0"
        />
      </div>
    </>
  );

  const renderZeroDayExploitForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="affected_software">
          Affected Software <span className="required">*</span>
        </label>
        <input
          type="text"
          id="affected_software"
          value={formData.affected_software || ''}
          onChange={(e) => handleChange('affected_software', e.target.value)}
          required
          placeholder="Software/system with zero-day vulnerability"
        />
      </div>

      <div className="form-group">
        <label htmlFor="vulnerability_type">
          Vulnerability Type <span className="required">*</span>
        </label>
        <input
          type="text"
          id="vulnerability_type"
          value={formData.vulnerability_type || ''}
          onChange={(e) => handleChange('vulnerability_type', e.target.value)}
          required
          placeholder="e.g., RCE, privilege escalation, information disclosure"
        />
      </div>

      <div className="form-group">
        <label htmlFor="exploit_source">Exploit Source</label>
        <input
          type="text"
          id="exploit_source"
          value={formData.exploit_source || ''}
          onChange={(e) => handleChange('exploit_source', e.target.value)}
          placeholder="e.g., Vendor disclosure, active exploitation, threat intel"
        />
      </div>
    </>
  );

  const renderContainerCompromiseForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="affected_platform">
          Affected Platform <span className="required">*</span>
        </label>
        <input
          type="text"
          id="affected_platform"
          value={formData.affected_platform || ''}
          onChange={(e) => handleChange('affected_platform', e.target.value)}
          required
          placeholder="e.g., Docker, Kubernetes, Podman"
        />
      </div>

      <div className="form-group">
        <label htmlFor="compromised_component">
          Compromised Component <span className="required">*</span>
        </label>
        <input
          type="text"
          id="compromised_component"
          value={formData.compromised_component || ''}
          onChange={(e) => handleChange('compromised_component', e.target.value)}
          required
          placeholder="e.g., Container, pod, node, registry"
        />
      </div>

      <div className="form-group">
        <label htmlFor="namespace_affected">Kubernetes Namespace</label>
        <input
          type="text"
          id="namespace_affected"
          value={formData.namespace_affected || ''}
          onChange={(e) => handleChange('namespace_affected', e.target.value)}
          placeholder="Kubernetes namespace if applicable"
        />
      </div>
    </>
  );

  const renderIoTDeviceCompromiseForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="device_type">
          Device Type <span className="required">*</span>
        </label>
        <input
          type="text"
          id="device_type"
          value={formData.device_type || ''}
          onChange={(e) => handleChange('device_type', e.target.value)}
          required
          placeholder="e.g., Camera, sensor, smart device"
        />
      </div>

      <div className="form-group">
        <label htmlFor="device_count">
          Device Count <span className="required">*</span>
        </label>
        <input
          type="number"
          id="device_count"
          value={formData.device_count || ''}
          onChange={(e) => handleChange('device_count', e.target.value)}
          required
          placeholder="Number of devices compromised"
          min="1"
        />
      </div>

      <div className="form-group">
        <label htmlFor="compromise_method">
          Compromise Method <span className="required">*</span>
        </label>
        <textarea
          id="compromise_method"
          value={formData.compromise_method || ''}
          onChange={(e) => handleChange('compromise_method', e.target.value)}
          required
          rows={3}
          placeholder="How devices were compromised"
        />
      </div>
    </>
  );

  const renderBackupSystemCompromiseForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="backup_system_type">
          Backup System Type <span className="required">*</span>
        </label>
        <input
          type="text"
          id="backup_system_type"
          value={formData.backup_system_type || ''}
          onChange={(e) => handleChange('backup_system_type', e.target.value)}
          required
          placeholder="e.g., Cloud, tape, disk, hybrid"
        />
      </div>

      <div className="form-group">
        <label htmlFor="backup_scope">
          Backup Scope <span className="required">*</span>
        </label>
        <input
          type="text"
          id="backup_scope"
          value={formData.backup_scope || ''}
          onChange={(e) => handleChange('backup_scope', e.target.value)}
          required
          placeholder="e.g., Files, databases, VMs, entire systems"
        />
      </div>

      <div className="form-group">
        <label htmlFor="compromise_method">
          Compromise Method <span className="required">*</span>
        </label>
        <textarea
          id="compromise_method"
          value={formData.compromise_method || ''}
          onChange={(e) => handleChange('compromise_method', e.target.value)}
          required
          rows={3}
          placeholder="How were backups compromised"
        />
      </div>
    </>
  );

  const renderDNSHijackingForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="affected_domain">
          Affected Domain <span className="required">*</span>
        </label>
        <input
          type="text"
          id="affected_domain"
          value={formData.affected_domain || ''}
          onChange={(e) => handleChange('affected_domain', e.target.value)}
          required
          placeholder="e.g., example.com"
        />
      </div>

      <div className="form-group">
        <label htmlFor="hijack_type">
          Hijack Type <span className="required">*</span>
        </label>
        <input
          type="text"
          id="hijack_type"
          value={formData.hijack_type || ''}
          onChange={(e) => handleChange('hijack_type', e.target.value)}
          required
          placeholder="e.g., Registrar takeover, DNS poisoning, subdomain takeover"
        />
      </div>

      <div className="form-group">
        <label htmlFor="dns_provider">
          DNS Provider <span className="required">*</span>
        </label>
        <input
          type="text"
          id="dns_provider"
          value={formData.dns_provider || ''}
          onChange={(e) => handleChange('dns_provider', e.target.value)}
          required
          placeholder="e.g., Route53, Cloudflare, Google Cloud DNS"
        />
      </div>
    </>
  );

  const renderSaaSApplicationCompromiseForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="saas_platform">
          SaaS Platform <span className="required">*</span>
        </label>
        <input
          type="text"
          id="saas_platform"
          value={formData.saas_platform || ''}
          onChange={(e) => handleChange('saas_platform', e.target.value)}
          required
          placeholder="e.g., Microsoft 365, Salesforce, Slack, Google Workspace"
        />
      </div>

      <div className="form-group">
        <label htmlFor="compromise_type">
          Compromise Type <span className="required">*</span>
        </label>
        <input
          type="text"
          id="compromise_type"
          value={formData.compromise_type || ''}
          onChange={(e) => handleChange('compromise_type', e.target.value)}
          required
          placeholder="e.g., OAuth abuse, admin takeover, consent phishing"
        />
      </div>

      <div className="form-group">
        <label htmlFor="affected_accounts">
          Affected Accounts <span className="required">*</span>
        </label>
        <input
          type="number"
          id="affected_accounts"
          value={formData.affected_accounts || ''}
          onChange={(e) => handleChange('affected_accounts', e.target.value)}
          required
          placeholder="Number of user accounts affected"
          min="1"
        />
      </div>
    </>
  );

  const renderMobileDeviceCompromiseForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="device_type">
          Device Type <span className="required">*</span>
        </label>
        <input
          type="text"
          id="device_type"
          value={formData.device_type || ''}
          onChange={(e) => handleChange('device_type', e.target.value)}
          required
          placeholder="e.g., iPhone, Android, iPad"
        />
      </div>

      <div className="form-group">
        <label htmlFor="device_ownership">
          Device Ownership <span className="required">*</span>
        </label>
        <input
          type="text"
          id="device_ownership"
          value={formData.device_ownership || ''}
          onChange={(e) => handleChange('device_ownership', e.target.value)}
          required
          placeholder="e.g., Corporate, BYOD, Contractor"
        />
      </div>

      <div className="form-group">
        <label htmlFor="compromise_method">
          Compromise Method <span className="required">*</span>
        </label>
        <textarea
          id="compromise_method"
          value={formData.compromise_method || ''}
          onChange={(e) => handleChange('compromise_method', e.target.value)}
          required
          rows={3}
          placeholder="How device was compromised"
        />
      </div>
    </>
  );

  const renderRegulatoryComplianceIncidentForm = () => (
    <>
      <div className="form-group">
        <label htmlFor="regulation_type">
          Regulation Type <span className="required">*</span>
        </label>
        <input
          type="text"
          id="regulation_type"
          value={formData.regulation_type || ''}
          onChange={(e) => handleChange('regulation_type', e.target.value)}
          required
          placeholder="e.g., GDPR, HIPAA, PCI-DSS, SOX, CCPA"
        />
      </div>

      <div className="form-group">
        <label htmlFor="affected_data_type">
          Affected Data Type <span className="required">*</span>
        </label>
        <input
          type="text"
          id="affected_data_type"
          value={formData.affected_data_type || ''}
          onChange={(e) => handleChange('affected_data_type', e.target.value)}
          required
          placeholder="e.g., PII, PHI, payment card data"
        />
      </div>

      <div className="form-group">
        <label htmlFor="affected_records_count">
          Affected Records Count <span className="required">*</span>
        </label>
        <input
          type="number"
          id="affected_records_count"
          value={formData.affected_records_count || ''}
          onChange={(e) => handleChange('affected_records_count', e.target.value)}
          required
          placeholder="Number of records/individuals affected"
          min="1"
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
      case 'bec':
        return renderBECForm();
      case 'web_application_attack':
        return renderWebApplicationAttackForm();
      case 'data_exfiltration':
        return renderDataExfiltrationForm();
      case 'supply_chain_attack':
        return renderSupplyChainAttackForm();
      case 'cloud_account_compromise':
        return renderCloudAccountCompromiseForm();
      case 'api_security_breach':
        return renderAPISecurityBreachForm();
      case 'credential_stuffing':
        return renderCredentialStuffingForm();
      case 'zero_day_exploit':
        return renderZeroDayExploitForm();
      case 'container_compromise':
        return renderContainerCompromiseForm();
      case 'iot_device_compromise':
        return renderIoTDeviceCompromiseForm();
      case 'backup_system_compromise':
        return renderBackupSystemCompromiseForm();
      case 'dns_hijacking':
        return renderDNSHijackingForm();
      case 'saas_application_compromise':
        return renderSaaSApplicationCompromiseForm();
      case 'mobile_device_compromise':
        return renderMobileDeviceCompromiseForm();
      case 'regulatory_compliance_incident':
        return renderRegulatoryComplianceIncidentForm();
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
