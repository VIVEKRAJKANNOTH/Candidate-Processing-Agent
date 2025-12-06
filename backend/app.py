"""
Flask Backend API for TraqCheck CandidateVerify
Simple API with basic candidate endpoints
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
import sqlite3
import uuid
import json
from datetime import datetime
from pathlib import Path
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Swagger UI Configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs"
}

swagger_template = {
    "info": {
        "title": "TraqCheck CandidateVerify API",
        "description": "API for managing candidate verification workflow",
        "version": "1.0.0"
    },
    "schemes": ["http"],
    "tags": [
        {
            "name": "Candidates",
            "description": "Candidate management endpoints"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Database configuration
BASE_DIR = Path(__file__).parent
DATABASE = os.path.join(BASE_DIR, 'database', 'traqcheck.db')


def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint
    ---
    tags:
      - Health
    responses:
      200:
        description: API is running
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            message:
              type: string
              example: API is running
    """
    return jsonify({'status': 'ok', 'message': 'API is running'})


@app.route('/candidates', methods=['POST'])
def create_candidate():
    """Create a new candidate
    ---
    tags:
      - Candidates
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - phone
            - resume_path
          properties:
            name:
              type: string
              example: John Doe
            email:
              type: string
              example: john@example.com
            phone:
              type: string
              example: +91-1234567890
            company:
              type: string
              example: Tech Corp
            designation:
              type: string
              example: Senior Developer
            skills:
              type: array
              items:
                type: string
              example: ["Python", "SQL", "Machine Learning"]
            experience_years:
              type: integer
              example: 5
            resume_path:
              type: string
              example: /uploads/resume.pdf
    responses:
      201:
        description: Candidate created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Candidate created successfully
            candidate_id:
              type: string
              example: 123e4567-e89b-12d3-a456-426614174000
      400:
        description: Bad request (missing required fields or duplicate entry)
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'resume_path']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate UUID for candidate
        candidate_id = str(uuid.uuid4())
        
        # Convert skills to JSON string if present
        skills = json.dumps(data.get('skills', [])) if data.get('skills') else None
        
        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO candidates (
                id, name, email, phone, company, designation,
                skills, experience_years, resume_path, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            candidate_id,
            data['name'],
            data['email'],
            data['phone'],
            data.get('company'),
            data.get('designation'),
            skills,
            data.get('experience_years'),
            data['resume_path'],
            'PARSED'
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Candidate created successfully',
            'candidate_id': candidate_id
        }), 201
        
    except sqlite3.IntegrityError as e:
        return jsonify({'error': 'Duplicate entry or constraint violation'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/candidates/<candidate_id>', methods=['GET'])
def get_candidate(candidate_id):
    """Get candidate by ID
    ---
    tags:
      - Candidates
    parameters:
      - in: path
        name: candidate_id
        required: true
        type: string
        description: Candidate UUID
        example: 84d8cae2-d942-4a2d-b6a1-f14828c18e92
    responses:
      200:
        description: Candidate details retrieved successfully
        schema:
          type: object
          properties:
            id:
              type: string
              example: 84d8cae2-d942-4a2d-b6a1-f14828c18e92
            name:
              type: string
              example: Jane Smith
            email:
              type: string
              example: jane@example.com
            phone:
              type: string
              example: +91-9876543210
            company:
              type: string
              example: DevCorp
            designation:
              type: string
              example: Software Engineer
            skills:
              type: array
              items:
                type: string
              example: ["JavaScript", "React", "Node.js"]
            experience_years:
              type: integer
              example: 3
            resume_path:
              type: string
              example: /uploads/resume.pdf
            status:
              type: string
              example: PARSED
            document_status:
              type: string
              example: NOT_REQUESTED
            created_at:
              type: string
              example: 2025-12-06 15:03:02
      404:
        description: Candidate not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: Candidate not found
      500:
        description: Server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, email, phone, company, designation,
                   skills, experience_years, resume_path, 
                   status, document_status, created_at
            FROM candidates 
            WHERE id = ?
        """, (candidate_id,))
        
        candidate = cursor.fetchone()
        conn.close()
        
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404
        
        # Convert to dict and parse JSON fields
        candidate_data = {
            'id': candidate['id'],
            'name': candidate['name'],
            'email': candidate['email'],
            'phone': candidate['phone'],
            'company': candidate['company'],
            'designation': candidate['designation'],
            'skills': json.loads(candidate['skills']) if candidate['skills'] else [],
            'experience_years': candidate['experience_years'],
            'resume_path': candidate['resume_path'],
            'status': candidate['status'],
            'document_status': candidate['document_status'],
            'created_at': candidate['created_at']
        }
        
        return jsonify(candidate_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
