"""
Vercel Serverless Function Entry Point
Wraps the Flask application for Vercel's Python runtime
"""
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

# Import Flask app
from app import app

# Vercel expects 'app' or 'handler' to be the WSGI/ASGI application
# Flask apps are WSGI compatible
handler = app
