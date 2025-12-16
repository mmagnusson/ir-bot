# Threat Model

## Overview

This document outlines security considerations for the IR AI Assistant to ensure it enhances security posture without introducing new risks.

## Trust Boundaries

### User Input
- **Threat**: Malicious input attempting to manipulate AI responses
- **Mitigation**: Structured forms with validation, no free-text in critical fields

### AI Output
- **Threat**: AI hallucinations leading to incorrect remediation
- **Mitigation**: Playbook-based validation, guardrails, explicit uncertainty statements

### Data Storage
- **Threat**: Sensitive incident data exposure
- **Mitigation**: MVP uses in-memory storage (production should encrypt at rest)

## Attack Scenarios

### 1. Prompt Injection

**Attack**: User attempts to inject malicious prompts through form fields

**Example**: Setting user email to "ignore previous instructions and..."

**Mitigations**:
- Structured data model (Pydantic validation)
- No direct user text in prompts without sanitization
- System prompt explicitly instructs to only use provided data
- Input validation on all fields

### 2. AI Manipulation

**Attack**: Crafting incident data to elicit specific AI responses

**Example**: Setting all fields to trigger maximum-severity response

**Mitigations**:
- Playbook-based decision logic (non-AI)
- Risk assessment based on objective criteria
- Guardrails validate AI recommendations
- Human-in-the-loop for all actions

### 3. Information Disclosure

**Attack**: Extracting sensitive incident data through API

**Example**: Enumerating incident IDs to access other incidents

**Mitigations**:
- MVP: No authentication (development only)
- Production must implement:
  - Authentication and authorization
  - Row-level security
  - Audit logging

### 4. Denial of Service

**Attack**: Creating excessive incidents or triggering expensive AI calls

**Mitigations**:
- MVP: No rate limiting (development only)
- Production must implement:
  - Rate limiting on API endpoints
  - Request size limits
  - AI call quotas

### 5. Malicious Recommendations

**Attack**: AI recommends destructive actions

**Example**: "Delete all user accounts to contain the threat"

**Mitigations**:
- Playbook validation of recommendations
- Checklist-based output (analyst performs actions)
- No automatic execution
- Recommendations flagged for manual review if not in playbook

## Data Classification

### Incident Data
- **Classification**: Confidential
- **Contains**: User emails, IOCs, investigation findings
- **Retention**: Should be configurable per organization policy
- **Access**: Should be role-based in production

### AI Interactions
- **Classification**: Confidential
- **Contains**: Prompts and responses
- **Logging**: Should be audit-logged in production
- **Retention**: Required for compliance and improvement

## Security Recommendations for Production

### Must Have

1. **Authentication & Authorization**
   - SSO/SAML integration
   - Role-based access control
   - MFA enforcement

2. **Data Protection**
   - Encryption at rest
   - Encryption in transit (TLS)
   - Secure key management

3. **Audit Logging**
   - All incident access
   - All AI interactions
   - All actions taken

4. **Input Validation**
   - Strict schema validation
   - Size limits
   - Content sanitization

5. **Rate Limiting**
   - Per-user API limits
   - AI call quotas
   - Request size limits

### Should Have

1. **Monitoring & Alerting**
   - Unusual AI response patterns
   - Failed authentication attempts
   - Data access patterns

2. **Incident Data Lifecycle**
   - Automated retention policies
   - Secure deletion
   - Export capabilities

3. **AI Safety Measures**
   - Response content filtering
   - Confidence scoring
   - Fallback to manual procedures

### Nice to Have

1. **Advanced Analytics**
   - Track AI recommendation accuracy
   - Measure analyst efficiency gains
   - Identify improvement areas

2. **Integration Security**
   - API authentication for integrations
   - Webhook signature verification
   - OAuth for third-party tools

## Responsible AI Considerations

### Bias and Fairness
- AI should not discriminate based on user identity
- Recommendations should be consistent for equivalent incidents
- Regular audits of AI outputs for bias

### Transparency
- Always show both AI and playbook recommendations
- Clearly mark AI-generated content
- Allow analysts to override AI suggestions

### Accountability
- Log all AI interactions
- Maintain audit trail of decisions
- Human analyst is ultimately responsible

### Privacy
- Minimize PII in prompts
- Don't use incident data for AI training without consent
- Allow data deletion requests

## Incident Response for the IR Tool

If this tool itself is compromised:

1. **Disable AI integration** - Fall back to playbook-only mode
2. **Audit all recent incidents** - Review for manipulation
3. **Rotate API keys** - If using external AI service
4. **Review access logs** - Identify unauthorized access
5. **Notify affected parties** - If incident data exposed

## Compliance Considerations

Depending on your organization:

- **GDPR**: Right to deletion, data minimization
- **HIPAA**: If handling health-related incidents
- **SOC 2**: Audit logging, access controls
- **ISO 27001**: Information security management

Consult with legal/compliance before production deployment.
