# IR AI Assistant - RUNNING ✓

## Application Status: LIVE

Both backend and frontend servers are running and ready to use!

### Backend Server ✓
- **Status:** Running
- **URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Process:** Background (ID: 6a3f56)

### Frontend Server ✓
- **Status:** Running
- **URL:** http://localhost:3000
- **Framework:** Vite + React
- **Process:** Background (ID: ac3f65)

## How to Access

### Open the Application
**Navigate to:** http://localhost:3000

You should see the IR AI Assistant intake form ready to use!

### Test the Application

Try creating a sample phishing incident:

1. **Open:** http://localhost:3000
2. **Fill in the form:**
   - Reporting User: `test@example.com`
   - User Clicked Link: `Yes`
   - Attachment Opened: `No`
   - Credentials Entered: `Unknown`
   - Email Headers Available: Check the box
   - Suspicious URL: `hxxp://evil-phishing.com/login`

3. **Click:** "Start Investigation"

4. **On the Investigation page:**
   - Click "Run Assessment" to see AI analysis
   - Review the guidance provided
   - Try updating findings
   - Proceed through the workflow

### API Documentation

Interactive API docs available at:
**http://localhost:8000/docs**

## Important Note

⚠️ **AI Features Require API Key**

The AI-powered features require an Anthropic API key. To enable AI:

```bash
# Set the API key (in a new terminal)
set ANTHROPIC_API_KEY=your-api-key-here  # Windows
export ANTHROPIC_API_KEY=your-api-key-here  # Mac/Linux
```

Without an API key, the system will provide playbook-based guidance only (AI features will show a fallback message).

## Current Services

### Running Processes
1. **Backend:** FastAPI server with Uvicorn
2. **Frontend:** Vite dev server with hot reload

### Features Available
- ✓ Incident intake form
- ✓ Structured data collection
- ✓ Playbook-based validation
- ✓ Risk assessment (non-AI)
- ✓ Investigation workflows
- ✓ Incident export (JSON/Text)
- ⚠️ AI assessments (requires API key)
- ⚠️ AI containment guidance (requires API key)

## Next Steps

1. **Access the app:** http://localhost:3000
2. **Create test incident:** Follow the sample data above
3. **Explore features:** Try the full workflow
4. **Add API key:** To enable AI features (optional for testing)
5. **Customize:** Edit playbooks in `backend/app/data/playbooks/`

## Managing the Servers

### Check Server Status
Both servers are running in the background. You can see their output in the console where you started them.

### To Stop Servers
Press `Ctrl+C` in the terminals where the servers are running, or use task manager to kill the processes.

### To Restart
Just run the commands again from the respective directories.

## Troubleshooting

### If you see connection errors:
1. Check both servers are running
2. Verify ports 3000 and 8000 are not in use
3. Check backend logs for errors
4. Clear browser cache and reload

### If AI features aren't working:
1. Set `ANTHROPIC_API_KEY` environment variable
2. Restart the backend server
3. Check API key is valid

---

**Application is LIVE and ready to test!**

Open http://localhost:3000 in your browser now! 🎉
