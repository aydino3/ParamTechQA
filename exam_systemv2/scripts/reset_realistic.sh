#!/bin/bash

# Reset database and seed with realistic data

echo "Dropping database..."
rm -f exam_system.db

echo "Running migrations..."
alembic upgrade head

echo "Seeding realistic data..."
python -m app.seed.realistic_seed

echo "✅ Database reset with realistic data complete!"

