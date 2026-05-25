#!/bin/bash
# AILP Backend Server Start Script

cd /root/workspace/ai-learning-platform/backend
source /tmp/ailp-venv/bin/activate

export DISABLE_DOCKER_SANDBOX=1
export PYTHONUNBUFFERED=1

echo "Starting AILP backend server..."
echo "DISABLE_DOCKER_SANDBOX=$DISABLE_DOCKER_SANDBOX"

exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info
