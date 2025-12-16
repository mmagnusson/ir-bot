"""
FastAPI Main Application
Entry point for the IR AI Assistant backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import incidents

app = FastAPI(
    title="IR AI Assistant",
    description="AI-powered Incident Response Assistant for guided phishing investigation",
    version="0.1.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React/Vite dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(incidents.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "IR AI Assistant API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
