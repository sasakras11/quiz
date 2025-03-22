#!/bin/bash

# Kill any existing process on port 8002
lsof -ti:8002 | xargs kill -9 2>/dev/null

# Activate virtual environment
source ../venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install beautifulsoup4

# Set Python path
export PYTHONPATH=/Users/alexander/projects/quiz/backend

# Start the server
python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload 