@echo off
echo Starting IR-bot Backend Server (accessible from network)...
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
