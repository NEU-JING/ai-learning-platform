#!/usr/bin/env python3
"""Start server in a separate process that won't be affected by parent signals"""

import os
import subprocess
import sys
import time

os.chdir("/root/workspace/ai-learning-platform/backend")

env = os.environ.copy()
env["DISABLE_DOCKER_SANDBOX"] = "1"
env["PYTHONUNBUFFERED"] = "1"

proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd="/root/workspace/ai-learning-platform/backend",
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    # Create new process group to avoid signals
    start_new_session=True,
)

print(f"Server started with PID {proc.pid}")

# Wait and check if it's still running
time.sleep(5)
if proc.poll() is None:
    print("Server is running")
else:
    print(f"Server exited with code {proc.returncode}")
    stdout, _ = proc.communicate()
    print("Output:", stdout.decode()[-2000:] if stdout else "None")

# Keep parent alive
try:
    while proc.poll() is None:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")
    proc.terminate()
    proc.wait()
