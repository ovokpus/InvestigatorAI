#!/bin/bash

# Railway startup script for InvestigatorAI
set -e

echo "🚀 Starting InvestigatorAI API..."
echo "Python path: $PYTHONPATH"
echo "Port: ${PORT:-8000}"
echo "Working directory: $(pwd)"

# List contents to debug
echo "Contents of /app:"
ls -la /app/

echo "Contents of /app/api:"
ls -la /app/api/

# Start the application
exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}
