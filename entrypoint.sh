#!/bin/sh

echo "Running database population script..."
python scripts/populate_db.py || true  

echo "Starting Dash application..."
exec poetry run python src/dash/main.py 