"""
Candidates Blueprint - Candidate CRUD and management routes
"""
from flask import Blueprint, request, jsonify
import json
import os
from werkzeug.utils import secure_filename
from database.connection import get_db_connection

candidates_bp = Blueprint('candidates', __name__)


@candidates_bp.route('/candidates', methods=['GET'])
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


@candidates_bp.route('/candidates/<candidate_id>', methods=['GET'])
def get_candidate(candidate_id):
    """Get candidate by ID with documents
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
        description: Candidate details retrieved successfully
      404:
        description: Candidate not found
      500:
        description: Server error
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
        
        if not candidate:
            conn.close()
            return jsonify({'error': 'Candidate not found'}), 404
        
        # Fetch uploaded documents for this candidate
        cursor.execute("""
            SELECT id, document_type, file_name, file_size, uploaded_at, verification_status
            FROM documents 
            WHERE candidate_id = ?
            ORDER BY uploaded_at DESC
        """, (candidate_id,))
        
        documents = cursor.fetchall()
        conn.close()
        
        # Build documents list
        documents_list = [
            {
                'id': doc['id'],
                'type': doc['document_type'],
                'file_name': doc['file_name'],
                'file_size': doc['file_size'],
                'uploaded_at': doc['uploaded_at'],
                'verification_status': doc['verification_status'],
                'download_url': f"/api/documents/{doc['id']}/download"
            }
            for doc in documents
        ]
        
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
            'created_at': candidate['created_at'],
            'documents': documents_list
        }
        
        return jsonify(candidate_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@candidates_bp.route('/candidates/<candidate_id>/request-documents', methods=['POST'])
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


@candidates_bp.route('/candidates/upload', methods=['POST'])
def upload_resume():
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
      400:
        description: Bad request (no file provided)
      500:
        description: Server error or parsing failed
    """
    try:
        from agents.parser import parse_with_structured_llm
        from utils.blob_storage import upload_to_blob, is_blob_enabled
        
        # Check if file is present
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        filename = secure_filename(file.filename)
        file_bytes = file.read()
        file.seek(0)  # Reset for local save if needed
        
        # Try Vercel Blob first, fallback to local /tmp
        blob_url = None
        if is_blob_enabled():
            blob_result = upload_to_blob(file_bytes, filename, "resumes")
            if blob_result.get("success"):
                blob_url = blob_result.get("url")
                print(f"[BLOB] Resume uploaded to: {blob_url}")
        
        # Always save locally for parsing (LLM needs file path)
        import tempfile
        upload_folder = os.path.join(tempfile.gettempdir(), 'uploads', 'resumes')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Parse with direct structured output parser
        result = parse_with_structured_llm(file_path, blob_url=blob_url)
        
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
