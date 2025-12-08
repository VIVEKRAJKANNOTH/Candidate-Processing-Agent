"""
Agent Configuration
Configuration for Gemini and other agent settings
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = 'gemini-2.5-flash'

# Model Settings
TEMPERATURE = 0.3  # Lower temperature for more deterministic outputs
MAX_TOKENS = 2000
TOP_P = 0.95

# Application Settings
REQUIRED_DOCUMENTS = ['AADHAR', 'PAN', 'DEGREE']
SUPPORTED_RESUME_FORMATS = ['.pdf', '.txt', '.doc', '.docx']

# Frontend URL for document upload links in emails
# Change this to your production URL when deploying
FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173')

