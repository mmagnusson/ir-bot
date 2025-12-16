# Limitations

## Current MVP Limitations

This document outlines what the IR AI Assistant **cannot** do in its current state.

## Incident Types

### Supported
- ✅ User-reported phishing emails

### Not Supported
- ❌ Malware infections
- ❌ Account compromise (non-phishing)
- ❌ Data breaches
- ❌ Insider threats
- ❌ DDoS attacks
- ❌ Ransomware
- ❌ Supply chain attacks

**Why**: MVP focuses on one well-defined incident type to prove the concept.

## Automation

### What It Does
- ✅ Provides guided recommendations
- ✅ Generates structured checklists
- ✅ Assesses risk based on data
- ✅ Validates recommendations against playbooks

### What It Doesn't Do
- ❌ Execute remediation actions automatically
- ❌ Access live security tools (EDR, SIEM, email gateway)
- ❌ Trigger workflows in other systems
- ❌ Send notifications automatically
- ❌ Modify user accounts or systems

**Why**: Safety and control. The analyst must review and execute all actions.

## Integrations

### Current State
- ❌ No EDR integration
- ❌ No SIEM integration
- ❌ No email gateway integration
- ❌ No Active Directory integration
- ❌ No ticketing system integration
- ❌ No threat intelligence feeds

**Why**: MVP avoids vendor dependencies to remain portable and simple.

### Future State
Could integrate with:
- SIEM for log queries
- EDR for endpoint status
- Email gateway for message deletion
- Threat intel for IOC enrichment

## AI Capabilities

### What AI Can Do
- ✅ Analyze structured incident data
- ✅ Provide investigation steps
- ✅ Suggest containment actions
- ✅ Generate incident summaries
- ✅ Identify information gaps

### What AI Cannot Do
- ❌ Access external data sources
- ❌ Make autonomous decisions
- ❌ Execute commands
- ❌ Learn from incidents (no fine-tuning in MVP)
- ❌ Predict future attacks

**Why**: Controlled AI use prevents hallucinations and maintains reliability.

## Data Management

### MVP Approach
- Uses in-memory storage (data lost on restart)
- No database persistence
- No user authentication
- No multi-tenancy
- No data encryption

### Production Requirements
Would need:
- Persistent database
- User authentication & authorization
- Audit logging
- Data encryption
- Backup and recovery
- Data retention policies

**Why**: MVP prioritizes functionality over infrastructure.

## Scalability

### Current Limits
- Single-server deployment
- Limited concurrent users
- No load balancing
- No high availability
- API rate limits depend on LLM provider

### Not Suitable For
- Enterprise-wide deployment (yet)
- High-volume incident processing
- 24/7 mission-critical operations

**Why**: MVP proves concept before investing in scaling infrastructure.

## Intelligence and Detection

### What It Doesn't Do
- ❌ Detect phishing emails automatically
- ❌ Scan network traffic
- ❌ Monitor user behavior
- ❌ Identify anomalies
- ❌ Predict attack patterns

**Why**: This is an **incident response** tool, not a detection/prevention tool.

### Use Cases It's NOT For
- Automated phishing detection
- Real-time threat hunting
- Continuous monitoring
- Preventive security controls

## Compliance and Governance

### Not Included
- ❌ Compliance reporting
- ❌ Regulatory alignment (GDPR, HIPAA, etc.)
- ❌ Audit trail persistence
- ❌ Data residency controls
- ❌ SLA guarantees

**Why**: Organizations must implement these based on their requirements.

## AI Model Limitations

### Depends On
- External AI service availability (Anthropic Claude API)
- API rate limits and quotas
- Model knowledge cutoff dates
- Internet connectivity for API calls

### Constraints
- AI responses may vary slightly
- Temperature set low (0.3) for consistency, but not deterministic
- No control over model updates
- Costs scale with usage

### Fallback
- Basic playbook-only mode if AI unavailable
- System continues to function without AI

## Language and Localization

### Current Support
- ✅ English only

### Not Supported
- ❌ Multi-language interfaces
- ❌ Translated playbooks
- ❌ Regional compliance variations

## User Experience

### Assumes
- Analyst has basic IR knowledge
- Analyst has access to necessary tools separately
- Analyst can interpret technical guidance
- Analyst can execute command-line operations if needed

### Not Suitable For
- Complete beginners with no IR training
- Fully automated response (no human in loop)
- Non-technical users

## Known Issues

### MVP Known Limitations
1. **No session management** - Incidents persist only in memory
2. **No collaboration** - Single analyst per incident
3. **No notifications** - Analyst must check manually
4. **Limited error handling** - Some edge cases may cause errors
5. **Simple AI parsing** - Section extraction is basic pattern matching

### Will Not Fix in MVP
These are acceptable limitations for proving the concept.

## What This Means for Users

### Do Use This For
- ✅ Learning and training
- ✅ Guided phishing incident response
- ✅ Structured investigation workflows
- ✅ Consistent documentation

### Don't Use This For
- ❌ Production-critical incidents (yet)
- ❌ Automated response
- ❌ Incidents beyond phishing
- ❌ Compliance requirements without enhancement

## Roadmap Considerations

To move beyond MVP, prioritize:

1. **Data persistence** - Real database
2. **Authentication** - Secure access
3. **More incident types** - Malware, account compromise
4. **Integrations** - EDR, SIEM, email
5. **Collaboration** - Multi-analyst workflows
6. **Compliance** - Audit logs, reporting
7. **High availability** - Production-ready infrastructure

## Questions About Limitations?

If you need capabilities beyond these limitations, consider:

1. **Fork and extend** - It's designed to be modular
2. **Integrate** - Use it alongside existing tools
3. **Contribute** - Help build the missing features
4. **Adapt playbooks** - Customize for your needs

Remember: The MVP is intentionally limited to prove the concept safely and effectively.
