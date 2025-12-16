# IR AI Assistant

> An AI-powered Incident Response assistant that guides analysts through phishing investigations using structured workflows and intelligent recommendations.

## Overview

The IR AI Assistant is a web-based tool designed to help security analysts handle phishing incidents consistently and effectively. It combines AI-powered analysis with procedural playbooks to provide guided investigation steps, containment recommendations, and structured documentation.

### Key Features

- **Structured Incident Intake** - Guided forms ensure all critical information is collected
- **AI-Powered Assessment** - Analyzes incident data to identify gaps and recommend next steps
- **Playbook Integration** - Validates AI recommendations against established procedures
- **Risk Assessment** - Automatically categorizes incident severity
- **Guided Workflows** - Step-by-step progression from triage to closure
- **Export & Documentation** - Generate professional incident summaries

### What Makes This Safe

- **No Hallucinations** - AI only works with provided data, never invents facts
- **Human-in-the-Loop** - All actions require analyst approval and execution
- **Playbook Validation** - AI recommendations are checked against procedural guardrails
- **Explicit Uncertainty** - When data is missing, the system explicitly says so
- **No Auto-Remediation** - The tool guides, it doesn't execute

## Architecture

```
┌─────────────────┐
│  Analyst Browser │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│   Frontend UI    │  (React + TypeScript)
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│ FastAPI Backend  │
└────────┬─────────┘
         │
         ├──► Incident State Model (Pydantic)
         │
         ├──► Decision Guardrails (Playbook validation)
         │
         ├──► Prompt Builder (Structured prompts)
         │
         ▼
┌─────────────────┐
│  LLM (Claude)    │
└─────────────────┘
```

## Project Structure

```
ir-ai-assistant/
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── api/
│   │   │   ├── incidents.py        # Incident endpoints
│   │   │   └── ai.py               # AI service wrapper
│   │   ├── models/
│   │   │   └── incident.py         # Data models (Pydantic)
│   │   ├── services/
│   │   │   ├── prompt_builder.py   # Prompt construction
│   │   │   └── decision_logic.py   # Guardrails & validation
│   │   └── data/
│   │       └── playbooks/
│   │           └── phishing.yaml   # Phishing playbook
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── IntakeForm.tsx      # Initial triage form
│   │   │   ├── Investigation.tsx   # Investigation workflow
│   │   │   ├── Containment.tsx     # Containment guidance
│   │   │   └── Summary.tsx         # Incident summary export
│   │   ├── components/
│   │   │   └── Checklist.tsx       # Reusable checklist component
│   │   └── api/
│   │       └── client.ts           # API client
│   └── package.json
│
├── docs/
│   ├── threat-model.md             # Security considerations
│   ├── mvp-scope.md                # MVP scope and limitations
│   └── limitations.md              # Known limitations
│
├── prompts/
│   ├── system.txt                  # AI system prompt
│   └── phishing_flow.txt           # Phishing investigation flow
│
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Anthropic API key (for Claude)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"  # On Windows: set ANTHROPIC_API_KEY=your-api-key-here
```

5. Run the backend:
```bash
python -m app.main
# Or using uvicorn directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The UI will be available at `http://localhost:3000`

### Access the Application

Open your browser and navigate to `http://localhost:3000`

## Usage Guide

### Step 1: Initial Triage

1. Open the application
2. Fill out the phishing incident intake form:
   - Reporting user's email
   - User interaction level (clicked link, opened attachment, entered credentials)
   - Email headers availability
   - Observable indicators (URLs, hashes, sender info)
3. Click "Start Investigation"

### Step 2: Investigation

1. Click "Run Assessment" to get AI-powered analysis
2. Review the assessment:
   - **What We Know** - Confirmed facts
   - **What We Need to Determine** - Information gaps
   - **Next Steps** - Recommended investigative actions
   - **Risk Level** - Automated risk assessment
3. Perform the investigation steps
4. Click "Add Investigation Findings" to update the incident with your discoveries
5. Click "Proceed to Containment"

### Step 3: Containment & Remediation

1. Click "Generate Guidance" for containment recommendations
2. Review:
   - **Containment Actions** - Immediate steps to prevent damage
   - **Remediation Steps** - Recovery and cleanup actions
   - **Risk Notes** - Residual risks and considerations
3. Execute approved actions
4. Record actions taken in the text area
5. Click "Generate Summary"

### Step 4: Summary & Export

1. Review the incident summary
2. Export as:
   - **JSON** - Structured data for integrations
   - **Text** - Human-readable report
3. Click "Start New Incident" to handle another case

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

### Key Endpoints

- `POST /api/incidents/` - Create a new incident
- `GET /api/incidents/{incident_id}` - Get incident details
- `PUT /api/incidents/{incident_id}` - Update incident
- `POST /api/incidents/{incident_id}/assess` - Run initial assessment
- `POST /api/incidents/{incident_id}/containment` - Get containment guidance
- `GET /api/incidents/{incident_id}/export` - Export incident summary

## Configuration

### Backend Configuration

Environment variables:

- `ANTHROPIC_API_KEY` - Your Anthropic API key (required for AI features)

### Frontend Configuration

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

## Customization

### Adding Custom Playbooks

Edit `backend/app/data/playbooks/phishing.yaml` to customize:

- Investigation steps
- Containment actions
- Risk assessment criteria
- Escalation thresholds

### Modifying AI Prompts

Edit files in the `prompts/` directory to adjust AI behavior:

- `system.txt` - System instructions for the AI
- `phishing_flow.txt` - Phishing investigation workflow reference

### Extending to New Incident Types

1. Add new incident type to `IncidentType` enum in `backend/app/models/incident.py`
2. Create data model for the new type (similar to `PhishingIncidentData`)
3. Create playbook YAML in `backend/app/data/playbooks/`
4. Add frontend forms for the new type

## Security Considerations

This is an MVP for development and testing. **Do not use in production without:**

1. **Authentication & Authorization** - Currently no user access controls
2. **Data Persistence** - Currently uses in-memory storage only
3. **Encryption** - No data encryption at rest or in transit (beyond HTTPS)
4. **Audit Logging** - No persistent audit trail
5. **Rate Limiting** - No API rate limits
6. **Input Validation** - Basic validation only

See [docs/threat-model.md](docs/threat-model.md) for detailed security considerations.

## Limitations

Current MVP limitations:

- **Single incident type** - Only phishing incidents supported
- **No live integrations** - No EDR, SIEM, email gateway connections
- **No automation** - All actions require manual execution
- **English only** - No multi-language support
- **In-memory storage** - Data lost on restart

See [docs/limitations.md](docs/limitations.md) for complete list.

## Development

### Running Tests

Backend tests (coming soon):
```bash
cd backend
pytest
```

Frontend tests (coming soon):
```bash
cd frontend
npm test
```

### Code Quality

Backend linting:
```bash
cd backend
flake8 app/
black app/
```

Frontend linting:
```bash
cd frontend
npm run lint
```

## Troubleshooting

### AI Service Not Working

**Problem**: Error message "AI service is currently unavailable"

**Solutions**:
1. Check that `ANTHROPIC_API_KEY` environment variable is set
2. Verify your API key is valid
3. Check internet connectivity
4. Review API quota limits

**Fallback**: The system will provide basic playbook-based guidance if AI is unavailable.

### CORS Errors

**Problem**: Frontend can't connect to backend

**Solutions**:
1. Ensure backend is running on port 8000
2. Check `allow_origins` in `backend/app/main.py`
3. Verify frontend proxy configuration in `frontend/vite.config.ts`

### Module Import Errors

**Problem**: Python import errors when starting backend

**Solutions**:
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version (requires 3.10+)

## Contributing

Contributions are welcome! This project is designed to be extensible.

Areas for contribution:
- Additional incident types (malware, account compromise, etc.)
- Integration modules (EDR, SIEM, email gateways)
- Improved AI parsing and validation
- Testing and quality improvements
- Documentation and examples

## License

This project is provided as-is for educational and development purposes.

## Acknowledgments

Built following the MVP specification for a safe, credible AI-powered incident response assistant.

Key design principles:
- Human-in-the-loop always
- No AI hallucinations
- Playbook-validated recommendations
- Calm, structured guidance
- Extensible architecture

## Support

For questions, issues, or feature requests, please open an issue in the project repository.

## Roadmap

### v0.2 (Next Steps)
- [ ] Add persistent database (PostgreSQL/SQLite)
- [ ] Implement user authentication
- [ ] Add malware incident type
- [ ] Basic audit logging

### v0.3 (Future)
- [ ] Account compromise incident type
- [ ] MITRE ATT&CK technique mapping
- [ ] Basic SIEM log query integration
- [ ] Multi-analyst collaboration

### v1.0 (Production Ready)
- [ ] Full authentication & authorization
- [ ] Comprehensive audit logging
- [ ] High availability deployment
- [ ] Production-grade error handling
- [ ] Compliance reporting

---

**Remember**: This tool guides analysts, it doesn't replace them. All recommendations require analyst review and approval. The analyst is always in control.
