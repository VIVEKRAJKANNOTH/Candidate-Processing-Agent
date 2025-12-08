"""
Documents Blueprint - Document upload, download, and view routes
"""
from flask import Blueprint, request, jsonify, send_file
import os
import json
import uuid
import mimetypes
from datetime import datetime
from pathlib import Path
from database.connection import get_db_connection

documents_bp = Blueprint('documents', __name__)

BASE_DIR = Path(__file__).parent.parent


@documents_bp.route('/candidates/<candidate_id>/submit-documents', methods=['POST'])
def submit_documents(candidate_id):
    """Submit documents for a candidate (PAN Card and Aadhaar)
    ---
    tags:
      - Documents
    consumes:
      - multipart/form-data
    parameters:
      - in: path
        name: candidate_id
        required: true
        type: string
        description: Candidate UUID
      - in: formData
        name: pan_card
        type: file
        required: true
        description: PAN Card document (image or PDF)
      - in: formData
        name: aadhaar_card
        type: file
        required: true
        description: Aadhaar Card document (image or PDF)
    responses:
      200:
        description: Documents submitted successfully
      400:
        description: Bad request (missing files or invalid format)
      404:
        description: Candidate not found
      500:
        description: Server error
    """
    try:
        from werkzeug.utils import secure_filename
        
        # Validate candidate exists
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, document_status FROM candidates WHERE id = ?", (candidate_id,))
        candidate = cursor.fetchone()
        
        if not candidate:
            conn.close()
            return jsonify({'success': False, 'error': 'Candidate not found'}), 404
        
        # Check if documents already submitted
        if candidate['document_status'] == 'SUBMITTED':
            conn.close()
            return jsonify({'success': False, 'error': 'Documents have already been submitted'}), 400
        
        # Validate files are present
        if 'pan_card' not in request.files or 'aadhaar_card' not in request.files:
            conn.close()
            return jsonify({'success': False, 'error': 'Both PAN Card and Aadhaar Card are required'}), 400
        
        pan_file = request.files['pan_card']
        aadhaar_file = request.files['aadhaar_card']
        
        if pan_file.filename == '' or aadhaar_file.filename == '':
            conn.close()
            return jsonify({'success': False, 'error': 'No files selected'}), 400
        
        # Validate file types
        allowed_extensions = {'jpg', 'jpeg', 'png', 'pdf'}
        
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
        
        if not allowed_file(pan_file.filename) or not allowed_file(aadhaar_file.filename):
            conn.close()
            return jsonify({'success': False, 'error': 'Invalid file type. Only JPG, PNG, and PDF are allowed'}), 400
        
        # Create upload directory - use /tmp for serverless environments
        import tempfile
        upload_folder = os.path.join(tempfile.gettempdir(), 'uploads', 'documents')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate secure filenames with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        pan_ext = pan_file.filename.rsplit('.', 1)[1].lower()
        aadhaar_ext = aadhaar_file.filename.rsplit('.', 1)[1].lower()
        
        pan_filename = f"{candidate_id}_PAN_{timestamp}.{pan_ext}"
        aadhaar_filename = f"{candidate_id}_AADHAAR_{timestamp}.{aadhaar_ext}"
        
        pan_path = os.path.join(upload_folder, pan_filename)
        aadhaar_path = os.path.join(upload_folder, aadhaar_filename)
        
        # Save files
        pan_file.save(pan_path)
        aadhaar_file.save(aadhaar_path)
        
        # Get file sizes
        pan_size = os.path.getsize(pan_path)
        aadhaar_size = os.path.getsize(aadhaar_path)
        
        # Insert document records
        pan_doc_id = str(uuid.uuid4())
        aadhaar_doc_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO documents (id, candidate_id, document_type, file_path, file_name, file_size, verification_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (pan_doc_id, candidate_id, 'PAN', pan_path, pan_filename, pan_size, 'PENDING'))
        
        cursor.execute("""
            INSERT INTO documents (id, candidate_id, document_type, file_path, file_name, file_size, verification_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (aadhaar_doc_id, candidate_id, 'AADHAAR', aadhaar_path, aadhaar_filename, aadhaar_size, 'PENDING'))
        
        # Update candidate status
        cursor.execute("""
            UPDATE candidates 
            SET document_status = 'SUBMITTED', documents_submitted_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), candidate_id))
        
        # Log the action
        log_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO agent_logs (id, candidate_id, action, input, output)
            VALUES (?, ?, ?, ?, ?)
        """, (log_id, candidate_id, 'DOCUMENTS_SUBMITTED', 
              json.dumps({'pan_file': pan_filename, 'aadhaar_file': aadhaar_filename}),
              json.dumps({'success': True})))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Documents submitted successfully',
            'candidate_id': candidate_id,
            'documents': {
                'pan': pan_filename,
                'aadhaar': aadhaar_filename
            }
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@documents_bp.route('/api/documents/<document_id>/download', methods=['GET'])
def download_document(document_id):
    """Download a submitted document
    ---
    tags:
      - Documents
    parameters:
      - in: path
        name: document_id
        required: true
        type: string
        description: Document UUID
    responses:
      200:
        description: File download
      404:
        description: Document not found
      500:
        description: Server error
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT file_path, file_name FROM documents WHERE id = ?", (document_id,))
        document = cursor.fetchone()
        conn.close()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        file_path = document['file_path']
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found on server'}), 404
        
        return send_file(
            file_path,
            download_name=document['file_name'],
            as_attachment=True
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@documents_bp.route('/api/documents/<document_id>/view', methods=['GET'])
def view_document(document_id):
    """View a submitted document in browser (inline)
    ---
    tags:
      - Documents
    parameters:
      - in: path
        name: document_id
        required: true
        type: string
        description: Document UUID
    responses:
      200:
        description: File served inline
      404:
        description: Document not found
      500:
        description: Server error
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT file_path, file_name FROM documents WHERE id = ?", (document_id,))
        document = cursor.fetchone()
        conn.close()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        file_path = document['file_path']
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found on server'}), 404
        
        # Determine mimetype
        mimetype, _ = mimetypes.guess_type(file_path)
        
        return send_file(
            file_path,
            mimetype=mimetype,
            as_attachment=False  # View inline instead of download
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
