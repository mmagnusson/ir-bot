# Quick Start Guide

Get the IR AI Assistant running in 5 minutes.

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Anthropic API key ([get one here](https://console.anthropic.com/))

## Step-by-Step Setup

### 1. Backend Setup (2 minutes)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
# On Windows:
set ANTHROPIC_API_KEY=your-api-key-here
# On macOS/Linux:
export ANTHROPIC_API_KEY=your-api-key-here

# Start the backend
python -m app.main
```

The backend will start on `http://localhost:8000`

### 2. Frontend Setup (2 minutes)

Open a **new terminal window**:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start on `http://localhost:3000`

### 3. Use the Application (1 minute)

1. Open your browser to `http://localhost:3000`
2. Fill out the phishing incident intake form
3. Click "Start Investigation"
4. Follow the guided workflow!

## Test It Out

Try this sample incident:

- **Reporting User**: `john.doe@company.com`
- **User Clicked Link**: Yes
- **Attachment Opened**: No
- **Credentials Entered**: Unknown
- **Headers Available**: Yes
- **Suspicious URL**: `hxxp://evil-phishing-site.com/login`

Click through the workflow to see the AI in action!

## Troubleshooting

### "AI service is currently unavailable"

✅ Check that your `ANTHROPIC_API_KEY` is set correctly

### "Cannot connect to backend"

✅ Ensure the backend is running on port 8000
✅ Check the terminal for any error messages

### "Module not found" errors

✅ Make sure you activated the virtual environment
✅ Run `pip install -r requirements.txt` again

### Port already in use

✅ Backend: Change port with `uvicorn app.main:app --port 8001`
✅ Frontend: Change port in `vite.config.ts`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Review [docs/mvp-scope.md](docs/mvp-scope.md) to understand capabilities
- Check [docs/limitations.md](docs/limitations.md) to understand constraints
- Customize the playbook at `backend/app/data/playbooks/phishing.yaml`

## Need Help?

Check the [README.md](README.md) troubleshooting section or open an issue.

Happy incident responding! 🔒
