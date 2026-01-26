#! /usr/bin/env bash

# Set PYTHONPATH to current directory
export PYTHONPATH=$PYTHONPATH:.

# Let the DB start
python app/backend_pre_start.py

# Run migrations
# Check if versions directory is empty or missing migration
if [ -z "$(ls -A app/alembic/versions/*.py 2>/dev/null)" ]; then
    echo "No migrations found. Generating initial migration..."
    alembic revision --autogenerate -m "Initial migration"
fi

alembic upgrade head

# Create initial data
python app/initial_data.py

# Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000
