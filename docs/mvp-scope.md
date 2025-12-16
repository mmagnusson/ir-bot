# MVP Scope

## What This MVP Does

A web-based AI assistant that **guides an analyst through a phishing-related incident** using structured questions and produces **next investigative and remediation steps** based only on provided inputs and known procedures.

## What This MVP Does NOT Do

- ❌ No automatic remediation
- ❌ No live EDR/SIEM integration
- ❌ No detection logic
- ❌ No "AI decides" behavior

This keeps scope tight and credibility high.

## Current Incident Type Support

### Phishing (User-Reported)

This is the only incident type supported in the MVP.

**Why phishing is perfect for MVP:**
- Extremely common
- Clear procedural steps
- Easy to validate logic
- Minimal vendor dependency

## User Flow

1. **Landing Page** - Analyst selects incident type (Phishing)
2. **Initial Triage Intake** - Structured form collects incident details
3. **AI Context Normalization** - Converts input to structured JSON
4. **Procedural Assessment** - AI provides initial analysis
5. **Analyst Feedback Loop** - Update findings from investigation
6. **Containment & Remediation Guidance** - AI provides action recommendations
7. **Incident Summary Export** - Generate final documentation

## Success Criteria

The MVP works if:

✅ A junior analyst can follow it without confusion
✅ The AI never invents facts
✅ The output is calm, structured, and repeatable
✅ You can add a second incident type without refactoring everything

## Future Enhancements (Post-MVP)

Once this works, add:

- Malware execution flow
- Account compromise flow
- MITRE technique mapping
- Organization-specific customization
- Live integration with security tools
- Multi-incident correlation
