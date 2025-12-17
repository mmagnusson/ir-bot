import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { incidentAPI, ClassificationResponse } from '../api/client';

const ClassifyIncident: React.FC = () => {
  const navigate = useNavigate();
  const [rawData, setRawData] = useState('');
  const [context, setContext] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ClassificationResponse | null>(null);

  const handleClassify = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!rawData.trim()) {
      setError('Please enter some data to classify');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const classification = await incidentAPI.classifyIncident({
        raw_data: rawData,
        context: context || undefined
      });
      setResult(classification);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to classify incident');
    } finally {
      setLoading(false);
    }
  };

  const handleUseClassification = (incidentType: string) => {
    // Navigate to intake form with pre-selected incident type
    navigate(`/?type=${incidentType}`);
  };

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 80) return '#22c55e'; // green
    if (confidence >= 60) return '#eab308'; // yellow
    if (confidence >= 40) return '#f97316'; // orange
    return '#ef4444'; // red
  };

  const examples = [
    {
      title: 'Phishing Example',
      data: 'User reported suspicious email from sender claiming to be IT support. Email requested user to click link and verify credentials. Link points to fake-microsoft-login.com domain. User did not click the link.'
    },
    {
      title: 'Ransomware Example',
      data: 'Multiple users reporting files encrypted with .locked extension. Ransom note found on desktop demanding 5 BTC payment. File server shows mass file modifications in last 30 minutes. Backup system also affected.'
    },
    {
      title: 'DDoS Example',
      data: 'Website experiencing severe slowdown. Network monitoring shows traffic spike from 2 Gbps to 45 Gbps. Traffic appears to be SYN flood from multiple source IPs. Service is currently unavailable to users.'
    },
  ];

  const loadExample = (exampleData: string) => {
    setRawData(exampleData);
    setContext('');
    setResult(null);
    setError(null);
  };

  return (
    <div className="container">
      <div className="header">
        <h1>AI Incident Classifier</h1>
        <p className="subtitle">Analyze logs or descriptions to identify incident type</p>
      </div>

      <div className="card">
        <h2>Incident Data Classification</h2>

        <form onSubmit={handleClassify}>
          <div className="form-group">
            <label htmlFor="raw_data">
              Raw Data / Logs / Description <span className="required">*</span>
            </label>
            <textarea
              id="raw_data"
              value={rawData}
              onChange={(e) => setRawData(e.target.value)}
              rows={8}
              required
              placeholder="Paste logs, event data, or describe the security incident here..."
              style={{ fontFamily: 'monospace', fontSize: '13px' }}
            />
            <small style={{ color: '#666', marginTop: '4px', display: 'block' }}>
              Paste security logs, IDS alerts, user reports, or any incident-related data
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="context">Additional Context (Optional)</label>
            <textarea
              id="context"
              value={context}
              onChange={(e) => setContext(e.target.value)}
              rows={3}
              placeholder="Add any additional context that might help with classification..."
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Analyzing...' : 'Classify Incident'}
            </button>
            <button
              type="button"
              className="btn"
              onClick={() => navigate('/')}
              style={{ background: '#6b7280' }}
            >
              Skip to Manual Entry
            </button>
          </div>
        </form>

        {/* Example buttons */}
        <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #e5e7eb' }}>
          <h4 style={{ marginBottom: '10px', color: '#374151' }}>Try an Example:</h4>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            {examples.map((example, idx) => (
              <button
                key={idx}
                type="button"
                className="btn"
                onClick={() => loadExample(example.data)}
                style={{
                  background: '#e5e7eb',
                  color: '#374151',
                  fontSize: '14px',
                  padding: '8px 16px'
                }}
              >
                {example.title}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="card" style={{ marginTop: '20px', background: '#f9fafb' }}>
          <h2>Classification Results</h2>

          {/* Summary */}
          <div style={{ marginBottom: '20px', padding: '15px', background: 'white', borderRadius: '8px' }}>
            <h4 style={{ marginTop: 0, color: '#374151' }}>Summary</h4>
            <p style={{ margin: 0, color: '#6b7280' }}>{result.raw_data_summary}</p>
          </div>

          {/* Primary Classification */}
          <div style={{
            padding: '20px',
            background: 'white',
            borderRadius: '8px',
            border: '2px solid #3b82f6',
            marginBottom: '20px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                  <h3 style={{ margin: 0, textTransform: 'capitalize' }}>
                    {result.primary_classification.incident_type.replace('_', ' ')}
                  </h3>
                  <span style={{
                    padding: '4px 12px',
                    borderRadius: '12px',
                    background: getConfidenceColor(result.primary_classification.confidence),
                    color: 'white',
                    fontSize: '14px',
                    fontWeight: 'bold'
                  }}>
                    {result.primary_classification.confidence.toFixed(0)}% Confidence
                  </span>
                </div>

                <p style={{ color: '#6b7280', margin: '10px 0' }}>
                  {result.primary_classification.reasoning}
                </p>

                {result.primary_classification.key_indicators.length > 0 && (
                  <div style={{ marginTop: '15px' }}>
                    <strong style={{ color: '#374151' }}>Key Indicators:</strong>
                    <ul style={{ marginTop: '8px', marginBottom: 0 }}>
                      {result.primary_classification.key_indicators.map((indicator, idx) => (
                        <li key={idx} style={{ color: '#6b7280', marginBottom: '4px' }}>{indicator}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <button
                className="btn btn-primary"
                onClick={() => handleUseClassification(result.primary_classification.incident_type)}
                style={{ marginLeft: '20px', whiteSpace: 'nowrap' }}
              >
                Use This Type
              </button>
            </div>
          </div>

          {/* Alternative Classifications */}
          {result.alternative_classifications.length > 0 && (
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ color: '#374151', marginBottom: '12px' }}>Alternative Classifications</h4>
              {result.alternative_classifications.map((alt, idx) => (
                <div key={idx} style={{
                  padding: '15px',
                  background: 'white',
                  borderRadius: '8px',
                  marginBottom: '10px',
                  border: '1px solid #e5e7eb'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <strong style={{ textTransform: 'capitalize', color: '#374151' }}>
                          {alt.incident_type.replace('_', ' ')}
                        </strong>
                        <span style={{
                          padding: '2px 8px',
                          borderRadius: '8px',
                          background: getConfidenceColor(alt.confidence),
                          color: 'white',
                          fontSize: '12px'
                        }}>
                          {alt.confidence.toFixed(0)}%
                        </span>
                      </div>
                      <p style={{ color: '#9ca3af', fontSize: '14px', margin: '5px 0 0 0' }}>
                        {alt.reasoning}
                      </p>
                    </div>
                    <button
                      className="btn"
                      onClick={() => handleUseClassification(alt.incident_type)}
                      style={{
                        background: '#e5e7eb',
                        color: '#374151',
                        marginLeft: '15px',
                        fontSize: '14px',
                        padding: '6px 12px'
                      }}
                    >
                      Use This
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Next Steps */}
          {result.suggested_next_steps.length > 0 && (
            <div style={{ padding: '15px', background: 'white', borderRadius: '8px' }}>
              <h4 style={{ marginTop: 0, color: '#374151' }}>Suggested Next Steps</h4>
              <ol style={{ marginBottom: 0, paddingLeft: '20px' }}>
                {result.suggested_next_steps.map((step, idx) => (
                  <li key={idx} style={{ color: '#6b7280', marginBottom: '8px' }}>{step}</li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}

      <div className="info-box" style={{ marginTop: '20px' }}>
        <h4>How Classification Works</h4>
        <ul>
          <li>AI analyzes your input data for security incident patterns</li>
          <li>Provides confidence scores for the suggested incident type</li>
          <li>Shows alternative classifications if multiple types are possible</li>
          <li>Falls back to keyword matching if AI is unavailable</li>
        </ul>
        <p style={{ marginTop: '15px', marginBottom: 0 }}>
          <strong>Tip:</strong> More detailed data leads to more accurate classifications. Include timestamps,
          IP addresses, user actions, and system behaviors when available.
        </p>
      </div>
    </div>
  );
};

export default ClassifyIncident;
