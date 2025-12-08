"""
Public Blueprint - Public-facing endpoints for candidate portal
"""
from flask import Blueprint, jsonify, send_file
import os
from pathlib import Path
from utils.db import get_db_connection

public_bp = Blueprint('public', __name__)

BASE_DIR = Path(__file__).parent.parent


@public_bp.route('/api/candidates/<candidate_id>/public', methods=['GET'])
def get_public_candidate_info(candidate_id):
    """Get public candidate info (only name for personalization)
    ---
    tags:
      - Public
    parameters:
      - in: path
        name: candidate_id
        required: true
        type: string
        description: Candidate UUID
    responses:
      200:
        description: Public candidate info
        schema:
          type: object
          properties:
            name:
              type: string
              example: Rahul Sharma
      404:
        description: Candidate not found
      500:
        description: Server error
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM candidates WHERE id = ?", (candidate_id,))
        candidate = cursor.fetchone()
        conn.close()
        
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404
        
        return jsonify({'name': candidate['name']}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@public_bp.route('/api/resume/<candidate_id>/download', methods=['GET'])
def download_resume(candidate_id):
    """Download a candidate's resume
    ---
    tags:
      - Public
    parameters:
      - in: path
        name: candidate_id
        required: true
        type: string
        description: Candidate UUID
    responses:
      200:
        description: File download
      404:
        description: Candidate or resume not found
      500:
        description: Server error
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT resume_path, name FROM candidates WHERE id = ?", (candidate_id,))
        candidate = cursor.fetchone()
        conn.close()
        
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404
        
        resume_path = candidate['resume_path']
        
        if not resume_path:
            return jsonify({'error': 'Resume file not found'}), 404
        
        # Handle relative paths
        if not os.path.isabs(resume_path):
            resume_path = os.path.join(BASE_DIR, resume_path)
        
        if not os.path.exists(resume_path):
            return jsonify({'error': 'Resume file not found on server'}), 404
        
        # Extract filename from path
        filename = os.path.basename(resume_path)
        
        return send_file(
            resume_path,
            download_name=filename,
            as_attachment=True
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@public_bp.route('/health', methods=['GET'])
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
    return jsonify({'status': 'ok', 'message': 'TraqCheck API is running'}), 200
