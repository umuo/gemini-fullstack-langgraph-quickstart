#!/usr/bin/env python3
"""
Custom server startup script that combines LangGraph with FastAPI.
"""
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Production server startup."""
    uvicorn.run(
        "src.agent.app:app",
        host="0.0.0.0",
        port=8123,
        log_level="info"
    )

if __name__ == "__main__":
    main()