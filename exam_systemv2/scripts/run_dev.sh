#!/bin/bash

# Run development server

echo "Starting development server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

