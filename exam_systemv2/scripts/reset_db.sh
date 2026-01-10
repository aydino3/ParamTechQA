#!/bin/bash

# Reset database (drop and recreate)

echo "Dropping database..."
rm -f exam_system.db

echo "Running migrations..."
alembic upgrade head

echo "Seeding data..."
python -m app.seed.seed_data

echo "Database reset complete!"

