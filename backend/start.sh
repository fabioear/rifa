#! /usr/bin/env bash

# Let the DB start
python app/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data
python app/initial_data.py

# Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000
