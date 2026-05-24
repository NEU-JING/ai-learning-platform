#!/usr/bin/env python3
"""
Start the AILP backend server with Docker sandbox disabled.
This script handles proper signal handling for background execution.
"""

import os
import signal
import sys

# Must set before any imports
os.environ["DISABLE_DOCKER_SANDBOX"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"

# Add backend to path
sys.path.insert(0, "/root/workspace/ai-learning-platform/backend")


# Signal handlers to prevent SIGTERM/SIGINT from stopping the server immediately
def signal_handler(signum, frame):
    print(f"\nReceived signal {signum}, ignoring for background execution")


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

import uvicorn

if __name__ == "__main__":
    print("Starting AILP backend server...")
    print(f"DISABLE_DOCKER_SANDBOX={os.environ.get('DISABLE_DOCKER_SANDBOX')}")
    print(f"Working directory: {os.getcwd()}")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True,
        # Don't reload in production
        reload=False,
        # Keep server running
        lifespan="on",
    )
