cd backend

# Activate virtual environment if not already active
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Check if main.py or app.py exists
ls

# Start the FastAPI server using uvicorn
uvicorn main:app --reload --port 8002# This file is intentionally left empty to make the directory a proper Python package 