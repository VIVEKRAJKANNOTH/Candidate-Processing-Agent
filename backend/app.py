"""
Flask Backend API for TraqCheck CandidateVerify

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


@app.route('/candidates', methods=['GET'])
def list_candidates():
    """List all candidates
    ---
    tags:
      - Candidates
    responses:
      200:
        description: List of candidates
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
              name:
                type: string
              email:
                type: string
              company:
                type: string
              status:
                type: string
      500:
        description: Server error
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, email, company, status, document_status FROM candidates")
        candidates = cursor.fetchall()
        conn.close()
        
        candidates_list = [
            {
                'id': c['id'],
                'name': c['name'],
                'email': c['email'],
                'company': c['company'] or '-',
                'status': c['status'],
                'document_status': c['document_status'] or 'NOT_REQUESTED'
            }
            for c in candidates
        ]
        
        return jsonify(candidates_list), 200
        
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
                   skills, experience_years, resume_path, confidence_scores,
                   status, document_status, created_at
            FROM candidates 
            WHERE id = ?
        """, (candidate_id,))
        
        candidate = cursor.fetchone()
        conn.close()
        
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404
        
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
            'confidence_scores': json.loads(candidate['confidence_scores']) if candidate['confidence_scores'] else {},
            'status': candidate['status'],
            'document_status': candidate['document_status'],
            'created_at': candidate['created_at']
        }
        
        return jsonify(candidate_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/candidates/<candidate_id>/request-documents', methods=['POST'])
def request_documents(candidate_id):
    """Request documents from a candidate (sends email)
    ---
    tags:
      - Candidates
    parameters:
      - in: path
        name: candidate_id
        required: true
        type: string
        description: Candidate UUID
    responses:
      200:
        description: Email generated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            candidate_id:
              type: string
            candidate_name:
              type: string
            candidate_email:
              type: string
            email:
              type: object
              properties:
                subject:
                  type: string
                body:
                  type: string
            deadline:
              type: string
            upload_link:
              type: string
      404:
        description: Candidate not found
      500:
        description: Server error
    """
    try:
        from agents.agent import generate_document_request_email_agent
        
        result = generate_document_request_email_agent(candidate_id)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            if 'not found' in result.get('error', '').lower():
                return jsonify(result), 404
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/candidates/upload', methods=['POST'])
def parse_with_structured_llm():
    """Upload resume and parse using direct structured output parser
    ---
    tags:
      - Candidates
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: resume
        type: file
        required: true
        description: Resume file (PDF or TXT format)
    responses:
      200:
        description: Resume parsed and candidate saved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                name:
                  type: string
                  example: John Doe
                email:
                  type: string
                  example: john@example.com
                phone:
                  type: string
                  example: +91-9876543210
                company:
                  type: string
                  example: Tech Corp
                designation:
                  type: string
                  example: Senior Software Engineer
                skills:
                  type: array
                  items:
                    type: string
                  example: ["Python", "JavaScript", "SQL"]
                experience_years:
                  type: integer
                  example: 5
                confidence_scores:
                  type: object
                  description: Confidence scores for each extracted field
                validation_status:
                  type: string
                  example: valid
                candidate_id:
                  type: string
                  example: 550e8400-e29b-41d4-a716-446655440000
                db_status:
                  type: string
                  example: Saved successfully
      400:
        description: Bad request (no file provided)
      500:
        description: Server error or parsing failed
    """
    try:
        from agents.parser import parse_with_structured_llm
        import os
        from werkzeug.utils import secure_filename
        
        # Check if file is present
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        upload_folder = 'uploads/resumes'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Parse with direct structured output parser
        result = parse_with_structured_llm(file_path)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        import traceback
        return jsonify({
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
