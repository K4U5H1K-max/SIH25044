#!/usr/bin/env bash
# Build script for Render

# Install dependencies
pip install -r requirements.txt

# Run the Flask app with gunicorn
gunicorn --bind 0.0.0.0:$PORT Backend1:app