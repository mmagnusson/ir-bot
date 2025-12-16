Excellent. I’ll give you something you can **hand directly to an AI coding assistant** and start building immediately.

Below is a **clear MVP scope**, a **single end-to-end IR flow**, and a **repository / component diagram** designed to keep this build *small, safe, and useful*.

---

# 1. MVP GOAL (VERY IMPORTANT)

### What this MVP does

> A web-based AI assistant that **guides an analyst through a phishing-related incident** using structured questions and produces **next investigative and remediation steps** based only on provided inputs and known procedures.

### What this MVP does NOT do

* No automatic remediation
* No live EDR/SIEM integration
* No detection logic
* No “AI decides” behavior

This keeps scope tight and credibility high.

---

# 2. MVP INCIDENT TYPE (START WITH ONE)

### 🎯 Incident Type: **User-Reported Phishing Email**

Why this is perfect:

* Extremely common
* Clear procedural steps
* Easy to validate logic
* Minimal vendor dependency

---

# 3. MVP USER FLOW (END-TO-END)

## Step 0: Landing Page

**Purpose:** Define context

**User selects:**

* Incident Type → *Phishing (User Reported)*

---

## Step 1: Initial Triage Intake

**Form Fields (structured input):**

* Reporting user email
* User clicked link? (Yes / No / Unknown)
* Attachment opened? (Yes / No / Unknown)
* Credentials entered? (Yes / No / Unknown)
* Time of report
* Email headers available? (Yes / No)
* URL or attachment hash (optional)

> ⚠️ These fields directly drive the reasoning path.

---

## Step 2: AI Context Normalization

**Behind the scenes:**

* Convert form input into a structured incident object:

```json
{
  "incident_type": "phishing",
  "user_clicked": true,
  "credentials_entered": "unknown",
  "attachment_opened": false,
  "headers_available": true,
  "observables": {
    "url": "hxxp://example",
    "hash": null
  }
}
```

No free-text yet. This prevents hallucinations.

---

## Step 3: Procedural Assessment (AI Output #1)

### Display to analyst:

#### 🧠 What We Know

* User clicked a link
* No attachment execution reported
* Credentials exposure unknown

#### ❓ What We Need to Determine Next

* Whether credentials were submitted
* Whether MFA protected the account
* Whether sign-in anomalies exist

#### 🔍 Recommended Next Investigative Steps

1. Review authentication logs for the user
2. Check for sign-ins from new IPs or locations
3. Confirm MFA status on account
4. Search inbox for similar phishing messages

> Output is checklist-based and calm.

---

## Step 4: Analyst Feedback Loop

The analyst confirms or updates findings:

**Form Update:**

* Credential submission confirmed? (Yes / No)
* Suspicious sign-ins observed? (Yes / No)
* MFA enabled? (Yes / No)
* Other affected users? (Yes / No)

This updates the incident object.

---

## Step 5: Containment & Remediation Guidance (AI Output #2)

Now the AI can safely recommend:

### 🔐 Containment Actions

* Force password reset
* Revoke active sessions
* Reset MFA tokens (if applicable)

### 🧹 Remediation Steps

* Block sender/domain
* Remove phishing email from mailboxes
* Educate affected users

### ⚠️ Risk Notes

* If credentials were reused elsewhere, risk extends beyond email
* Delayed response increases account takeover likelihood

---

## Step 6: Incident Summary Export (MVP WIN)

Generate a structured report:

```json
{
  "incident_summary": "...",
  "actions_taken": [...],
  "open_risks": [...],
  "recommended_followups": [...]
}
```

This alone makes the MVP valuable.

---

# 4. AI PROMPTING STRATEGY (CRITICAL)

### System Prompt (Fixed)

> You are an Incident Response procedural assistant.
> You must only provide guidance based on the supplied incident data and established IR best practices.
> If information is missing, explicitly state what cannot be determined.
> Do not speculate.

### User Prompt (Generated)

* JSON incident object
* Explicit task:

  > “Based on this incident state, provide: what we know, what we don’t know, and the next investigative steps.”

This keeps output constrained and reliable.

---

# 5. MVP REPOSITORY STRUCTURE

```
ir-ai-assistant/
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry
│   │   ├── api/
│   │   │   ├── incidents.py        # Incident endpoints
│   │   │   └── ai.py               # AI interaction wrapper
│   │   ├── models/
│   │   │   └── incident.py         # Incident schema (Pydantic)
│   │   ├── services/
│   │   │   ├── prompt_builder.py   # Controlled prompt creation
│   │   │   └── decision_logic.py   # Non-AI guardrails
│   │   └── data/
│   │       └── playbooks/
│   │           └── phishing.yaml   # Procedural steps
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── IntakeForm.tsx
│   │   │   ├── Investigation.tsx
│   │   │   └── Summary.tsx
│   │   ├── components/
│   │   │   └── Checklist.tsx
│   │   └── api/
│   │       └── client.ts
│   └── package.json
│
├── docs/
│   ├── threat-model.md
│   ├── mvp-scope.md
│   └── limitations.md
│
├── prompts/
│   ├── system.txt
│   └── phishing_flow.txt
│
└── README.md
```

---

# 6. HIGH-LEVEL COMPONENT DIAGRAM (TEXTUAL)

```
[ Analyst Browser ]
        |
        v
[ Frontend UI ]
        |
        v
[ FastAPI Backend ]
        |
        +--> [ Incident State Model ]
        |
        +--> [ Decision Guardrails ]
        |
        +--> [ Prompt Builder ]
        |
        v
[ LLM (Local or API) ]
        |
        v
[ Structured IR Guidance ]
```

---

# 7. MVP SUCCESS CRITERIA

You’ll know this MVP works if:

* A junior analyst can follow it without confusion
* The AI never invents facts
* The output is calm, structured, and repeatable
* You can add a second incident type without refactoring everything

---

# 8. NEXT AFTER MVP (OPTIONAL)

Once this works:

* Add malware execution flow
* Add account compromise flow
* Add MITRE technique mapping
* Add org-specific customization

---

If you want next, I can:

* Write **exact prompts** for phishing.yaml
* Design the **incident schema**
* Draft the **decision guardrails**
* Or help you harden this against misuse

Tell me your next step.
