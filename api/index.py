"""
Vercel Serverless Function Entry Point
Flask application handler for Vercel's Python runtime
"""
import sys
import os
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

# Set working directory to backend for relative imports
os.chdir(str(backend_path))

# Import Flask app
from app import app

# Vercel's Python runtime expects the Flask app to be named 'app'
# It will automatically handle the WSGI conversion
