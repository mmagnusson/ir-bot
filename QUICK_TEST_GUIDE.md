# Quick Testing Guide - IR-Bot Classification Feature

## Prerequisites
- Python 3.8+
- Node.js 16+
- Anthropic API key (get one at https://console.anthropic.com/)

---

## Step 1: Backend Setup

### 1.1 Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 1.2 Create .env File
```bash
# Copy the example file
cp .env.example .env

# Or create it manually with:
# ANTHROPIC_API_KEY=your-actual-api-key-here
```

**IMPORTANT**: Edit `backend/.env` and add your real Anthropic API key

### 1.3 Start Backend Server
```bash
# From the backend directory
uvicorn app.main:app --reload
```

The backend will start at: **http://localhost:8000**

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## Step 2: Frontend Setup

### 2.1 Install Node Dependencies
```bash
cd frontend
npm install
```

### 2.2 Start Frontend Dev Server
```bash
npm run dev
```

The frontend will start at: **http://localhost:5173**

---

## Step 3: Test Classification Feature

### Option A: Using the Web UI

1. **Open your browser**: Navigate to `http://localhost:5173/classify`

2. **Try the Ransomware Example**:
   - Click the "Ransomware Example" button
   - Click "Classify Incident"
   - You should see:
     - Primary Classification: **Ransomware** (85-95% confidence)
     - Alternative classifications with lower confidence
     - Key indicators extracted from the text
     - Suggested next steps

3. **Test the Flow**:
   - Click "Use This Type" on the primary classification
   - You'll be redirected to the intake form with Ransomware pre-selected

### Option B: Using API Directly (cURL)

Test the classification endpoint directly:

```bash
curl -X POST http://localhost:8000/api/incidents/classify \
  -H "Content-Type: application/json" \
  -d '{
    "raw_data": "Multiple users reporting files encrypted with .locked extension. Ransom note found demanding 5 BTC. File server shows mass file modifications.",
    "context": "Detected at 2PM, affecting finance department"
  }'
```

Expected response:
```json
{
  "primary_classification": {
    "incident_type": "ransomware",
    "confidence": 92.5,
    "reasoning": "Clear indicators of ransomware: file encryption, ransom demand, mass modifications",
    "key_indicators": ["files encrypted", "ransom note", "5 BTC demand", "mass file modifications"]
  },
  "alternative_classifications": [
    {
      "incident_type": "malware",
      "confidence": 45.0,
      "reasoning": "Could be malware with encryption capabilities",
      "key_indicators": ["file modifications"]
    }
  ],
  "raw_data_summary": "Ransomware attack affecting multiple users...",
  "suggested_next_steps": [
    "Isolate affected systems immediately",
    "Do NOT pay the ransom",
    "Check backup integrity"
  ]
}
```

---

## Step 4: Test Different Incident Types

### Phishing Example
```json
{
  "raw_data": "User reported suspicious email from sender claiming to be IT support requesting credential verification. Link points to fake-microsoft-login.com"
}
```
**Expected**: Phishing (85-95% confidence)

### DDoS Example
```json
{
  "raw_data": "Website experiencing severe slowdown. Traffic spike from 2 Gbps to 45 Gbps. SYN flood detected. Service unavailable."
}
```
**Expected**: DDoS (90%+ confidence)

### Account Compromise Example
```json
{
  "raw_data": "Multiple failed SSH login attempts detected. 127 attempts in 5 minutes from IP 203.0.113.45. Successful login after failed attempts. Unusual commands executed."
}
```
**Expected**: Account Compromise (85%+ confidence)

### Insider Threat Example
```json
{
  "raw_data": "Employee accessed sensitive files outside normal duties. Bulk download of customer database to USB drive detected. User is resigning next week."
}
```
**Expected**: Insider Threat (80%+ confidence)

---

## Step 5: Test Full Workflow

1. **Classify Incident**:
   - Go to `/classify`
   - Paste: "Suspicious email with attachment. User clicked and downloaded file. System now running slow with unknown processes."

2. **Review AI Suggestion**:
   - Primary: Malware (70-80% confidence)
   - Alternative: Phishing (60% confidence)

3. **Select Type**:
   - Click "Use This Type" on Malware

4. **Fill Intake Form**:
   - Form opens with Malware pre-selected
   - Fill in required fields (reporting user email, etc.)
   - Submit

5. **Investigation**:
   - View AI-generated investigation steps
   - Get containment recommendations
   - Complete incident workflow

---

## Troubleshooting

### Backend Issues

**Error: "anthropic module not found"**
```bash
pip install anthropic
```

**Error: "No module named 'app'"**
```bash
# Make sure you're in the backend directory
cd backend
uvicorn app.main:app --reload
```

**Error: "ANTHROPIC_API_KEY not found"**
- Check that `.env` file exists in `backend/` directory
- Verify API key is set: `ANTHROPIC_API_KEY=sk-ant-...`

### Frontend Issues

**Error: "Cannot connect to backend"**
- Ensure backend is running on port 8000
- Check CORS settings (should be configured in `backend/app/main.py`)

**Classification returns "AI unavailable"**
- Backend will use keyword-based fallback
- Still functional, but less accurate
- Check backend logs for API errors

---

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:5173
- [ ] `/classify` page displays correctly
- [ ] Example buttons load sample data
- [ ] "Classify Incident" button triggers analysis
- [ ] Results show primary + alternative classifications
- [ ] Confidence badges display with colors
- [ ] "Use This Type" navigates to intake form
- [ ] Intake form pre-selects correct incident type
- [ ] All 8 incident types work end-to-end

---

## Quick Verification

Run this command to verify all playbooks are present:
```bash
ls -la backend/app/data/playbooks/*.yaml
```

Expected files:
- phishing.yaml
- malware.yaml
- ransomware.yaml
- account_compromise.yaml
- data_breach.yaml
- insider_threat.yaml
- ddos.yaml
- unauthorized_access.yaml (if created)

---

## API Endpoints Available

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/incidents/classify` | POST | Classify raw incident data |
| `/api/incidents/` | POST | Create new incident |
| `/api/incidents/{id}` | GET | Get incident details |
| `/api/incidents/{id}/assess` | POST | AI assessment |
| `/api/incidents/{id}/containment` | POST | Containment guidance |
| `/docs` | GET | Interactive API docs (Swagger) |

---

## Next Steps After Testing

1. **Review Classification Accuracy**: Test with real security logs
2. **Tune Keyword Patterns**: Adjust patterns in `classifier.py` if needed
3. **Add Custom Examples**: Add organization-specific examples to the UI
4. **Integration**: Connect to SIEM/IDS for automatic classification
5. **Feedback Loop**: Add analyst feedback to improve AI accuracy

---

## Success Criteria

✅ Classification works with AI
✅ Fallback to keywords if AI fails
✅ Confidence scores are reasonable (40-95%)
✅ Alternative suggestions make sense
✅ One-click navigation to intake form works
✅ Pre-selected incident type persists

**If all checks pass, the feature is ready for production testing!**
