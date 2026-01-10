#!/bin/bash

# Initialize database with migrations and seed data

echo "Running Alembic migrations..."
alembic upgrade head

echo "Seeding initial data..."
python -m app.seed.seed_data

echo "Database initialized successfully!"

