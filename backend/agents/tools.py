"""
Agent Tools - Phase 1: Resume Parsing
Tools for extracting and processing resume data
"""

from langchain.tools import tool
import PyPDF2
import re
from typing import Dict, Any, List
from pydantic import BaseModel, Field


# ============================================================================
# PYDANTIC OUTPUT MODEL
# ============================================================================

class ConfidenceScores(BaseModel):
    """Confidence scores for each extracted field"""
    name: float = Field(description="Confidence for name extraction", ge=0.0, le=1.0)
    email: float = Field(description="Confidence for email extraction", ge=0.0, le=1.0)
    phone: float = Field(description="Confidence for phone extraction", ge=0.0, le=1.0)
    company: float = Field(description="Confidence for company extraction", ge=0.0, le=1.0)
    designation: float = Field(description="Confidence for designation extraction", ge=0.0, le=1.0)
    skills: float = Field(description="Confidence for skills extraction", ge=0.0, le=1.0)
    experience_years: float = Field(description="Confidence for experience years extraction", ge=0.0, le=1.0)


class CandidateInfo(BaseModel):
    """Structured output model for candidate information with confidence tracking"""
    
    # Core fields - simple values
    name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address of the candidate")
    phone: str = Field(description="Phone number with country code")
    company: str = Field(default="", description="Current or most recent company")
    designation: str = Field(default="", description="Current or most recent job title")
    skills: List[str] = Field(default_factory=list, description="List of technical skills")
    experience_years: int = Field(default=0, description="Total years of professional experience")
    
    # Confidence scores as separate dict
    confidence_scores: ConfidenceScores = Field(description="Confidence scores for each extracted field")
    
    # Agent tracking fields
    ai_message: str = Field(description="Condensed summary of the parsing reasoning and key observations")
    tool_calls: List[str] = Field(default_factory=list, description="List of tools called during parsing")
    overall_confidence: float = Field(description="Overall confidence in the extraction accuracy", ge=0.0, le=1.0)
    validation_status: str = Field(description="'valid' or 'invalid' based on data validation results")
    
    # Database operation fields
    candidate_id: str = Field(default="", description="UUID of the candidate in the database (set after saving)")
    db_status: str = Field(default="", description="Database operation status message (e.g., 'saved successfully' or error)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+91-9876543210",
                "company": "Tech Corp",
                "designation": "Senior Software Engineer",
                "skills": ["Python", "Django", "React"],
                "experience_years": 5,
                "confidence_scores": {
                    "name": 0.95,
                    "email": 0.98,
                    "phone": 0.90,
                    "company": 0.85,
                    "designation": 0.88,
                    "skills": 0.92,
                    "experience_years": 0.80
                },
                "ai_message": "Extracted candidate info from PDF resume.",
                "tool_calls": ["extract_text_from_pdf", "save_candidate_to_db"],
                "overall_confidence": 0.90,
                "validation_status": "valid",
                "candidate_id": "550e8400-e29b-41d4-a716-446655440000",
                "db_status": "Candidate saved successfully"
            }
        }


class DocumentRequestEmail(BaseModel):
    """Simplified structured output for document request email"""
    
    candidate_name: str = Field(description="Name of the candidate")
    candidate_email: str = Field(description="Email address of the candidate")
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Complete email body text")
    upload_link: str = Field(description="Document upload link for the candidate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "candidate_name": "John Doe",
                "candidate_email": "john@example.com",
                "subject": "Document Verification Request - TraqCheck",
                "body": "Dear John Doe,\n\nWe are reaching out regarding...",
                "upload_link": "https://traqcheck.com/upload/uuid-123"
            }
        }


# ============================================================================
# EMAIL SENDER TOOL (Gmail SMTP)
# ============================================================================

@tool
def send_email_gmail(
    to_email: str,
    subject: str,
    body: str
) -> Dict[str, Any]:
    """
    Send an email using Gmail SMTP.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        body: Email body content
        
    Returns:
        Dict with status and message
    """
    import os
    import smtplib
    from email.message import EmailMessage
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Get Gmail credentials from environment
        gmail_address = os.getenv('GMAIL_ADDRESS')
        gmail_app_password = os.getenv('GMAIL_APP_PASSWORD')
        
        # Debug: print env status (redacted password)
        print(f"[DEBUG] GMAIL_ADDRESS: {gmail_address}")
        
        if not gmail_address or not gmail_app_password:
            # Return mock response for testing when credentials not configured
            print(f"[MOCK] Gmail credentials not configured - simulating email send")
            return {
                'success': True,
                'mock': True,
                'status': 'pending',
                'to': to_email,
                'subject': subject,
                'message': 'Email simulated (no Gmail credentials configured)'
            }
        
        # Create the email message
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = gmail_address
        msg['To'] = to_email
        msg.set_content(body)
        
        # Also set HTML content for better formatting
        html_body = body.replace('\n', '<br>')
        msg.add_alternative(f"<html><body>{html_body}</body></html>", subtype='html')
        
        # Send via Gmail SMTP
        # Strip spaces from app password (Gmail shows it with spaces but should be used without)
        gmail_app_password = gmail_app_password.replace(' ', '')
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_address, gmail_app_password)
            smtp.send_message(msg)
        
        print(f"Email sent successfully to: {to_email}")
        
        return {
            'success': True,
            'status': 'sent',
            'to': to_email,
            'from': gmail_address,
            'subject': subject,
            'message': 'Email sent successfully via Gmail'
        }
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"[ERROR] SMTP Auth Error: {e}")
        return {
            'success': False,
            'error': f'Gmail authentication failed: {str(e)}. Ensure 2FA is ON and use App Password from https://myaccount.google.com/apppasswords',
            'details': str(e),
            'to': to_email,
            'subject': subject
        }
    except Exception as e:
        print(f"[ERROR] SMTP Error: {e}")
        return {
            'success': False,
            'error': str(e),
            'to': to_email,
            'subject': subject
        }


# ============================================================================
# DATABASE UPDATE TOOL - Candidate Document Status
# ============================================================================

@tool
def update_candidate_document_status(
    candidate_id: str,
    document_status: str = "REQUESTED"
) -> Dict[str, Any]:
    """
    Update candidate's document_status and documents_requested_at in the database.
    
    Args:
        candidate_id: UUID of the candidate
        document_status: Status to set (e.g., 'REQUESTED', 'SUBMITTED', 'VERIFIED')
        
    Returns:
        Dict with success status and updated fields
    """
    from database.connection import get_db_connection
    from datetime import datetime
    
    try:
        # Current timestamp
        now = datetime.now().isoformat()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update candidate document status
        if document_status == "REQUESTED":
            cursor.execute("""
                UPDATE candidates 
                SET document_status = ?, 
                    documents_requested_at = ?,
                    updated_at = ?
                WHERE id = ?
            """, (document_status, now, now, candidate_id))
        elif document_status == "SUBMITTED":
            cursor.execute("""
                UPDATE candidates 
                SET document_status = ?, 
                    documents_submitted_at = ?,
                    updated_at = ?
                WHERE id = ?
            """, (document_status, now, now, candidate_id))
        else:
            cursor.execute("""
                UPDATE candidates 
                SET document_status = ?, 
                    updated_at = ?
                WHERE id = ?
            """, (document_status, now, candidate_id))
        
        if cursor.rowcount == 0:
            conn.close()
            return {
                'success': False,
                'error': f'Candidate {candidate_id} not found'
            }
        
        conn.commit()
        conn.close()
        
        print(f"[DB] Updated candidate {candidate_id}: document_status={document_status}")
        
        return {
            'success': True,
            'candidate_id': candidate_id,
            'document_status': document_status,
            'updated_at': now
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'candidate_id': candidate_id
        }


# ============================================================================
# TOOLS
# ============================================================================

@tool
def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"


@tool
def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text content from a text file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        str: Content of the text file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text content from a DOCX (Word) file.
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        str: Extracted text from the DOCX
    """
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"


@tool
def get_candidate_by_id(candidate_id: str) -> Dict[str, Any]:
    """
    Fetch candidate details from the database by ID.
    
    Args:
        candidate_id: UUID of the candidate to fetch
        
    Returns:
        Dict with candidate data or error message
    """
    from database.connection import get_db_connection
    import json
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use explicit column names for Turso compatibility (SELECT * doesn't work with empty description)
        cursor.execute("""
            SELECT id, name, email, phone, company, designation, skills, 
                   experience_years, resume_path, confidence_scores, status, 
                   document_status, documents_requested_at, documents_submitted_at,
                   created_at, updated_at
            FROM candidates WHERE id = ?
        """, (candidate_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {'success': False, 'error': f'Candidate not found: {candidate_id}'}
        
        candidate = dict(row)
        # Parse JSON fields
        if candidate.get('skills'):
            candidate['skills'] = json.loads(candidate['skills'])
        if candidate.get('confidence_scores'):
            candidate['confidence_scores'] = json.loads(candidate['confidence_scores'])
            
        return {'success': True, 'candidate': candidate}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ============================================================================
# DATA VALIDATOR TOOL
# ============================================================================

def _validate_email(email: str) -> bool:
    """Check if email format is valid"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def _validate_phone(phone: str) -> bool:
    """Check if phone format is valid (allows various formats with country codes)"""
    if not phone:
        return False
    # Remove spaces, dashes, parentheses for validation
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    # Should have at least 10 digits, optionally starting with +
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, cleaned))


def _check_mandatory_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """Check if mandatory fields are present and non-empty"""
    mandatory = ['name', 'email', 'phone']
    results = {}
    
    for field in mandatory:
        value = data.get(field, '')
        # Handle both direct values and dict with 'value' key
        if isinstance(value, dict):
            value = value.get('value', '')
        results[field] = {
            'present': bool(value and str(value).strip()),
            'value': value
        }
    
    return results


def _calculate_confidence(data: Dict[str, Any], validation_results: Dict[str, Any]) -> float:
    """Calculate overall confidence score based on field presence and validation"""
    scores = []
    
    # Mandatory fields weight more
    mandatory_weight = 0.6
    validation_weight = 0.4
    
    # Check mandatory fields presence
    mandatory_present = sum(1 for v in validation_results['mandatory_fields'].values() if v['present'])
    mandatory_score = mandatory_present / 3  # 3 mandatory fields
    
    # Check format validations
    validation_score = 0
    if validation_results['format_validation']['email_valid']:
        validation_score += 0.5
    if validation_results['format_validation']['phone_valid']:
        validation_score += 0.5
    
    # Calculate weighted average
    overall = (mandatory_score * mandatory_weight) + (validation_score * validation_weight)
    
    return round(overall, 2)


@tool
def validate_candidate_data(candidate_data: str) -> Dict[str, Any]:
    """
    Validate extracted candidate data.
    Checks mandatory fields, validates email/phone formats, calculates confidence.
    
    Args:
        candidate_data: JSON string containing candidate information
                       (name, email, phone, company, designation, skills, experience_years)
    
    Returns:
        Dict with validation results including:
        - mandatory_fields: Status of each mandatory field
        - format_validation: Email and phone format checks
        - overall_confidence: Confidence score (0.0 to 1.0)
        - is_valid: Boolean indicating if data passes minimum validation
    """
    import json
    
    # Parse JSON string to dict if needed
    if isinstance(candidate_data, str):
        try:
            data = json.loads(candidate_data)
        except json.JSONDecodeError:
            return {'error': 'Invalid JSON format', 'is_valid': False}
    else:
        data = candidate_data
    
    # Extract values (handle both direct values and dict with 'value' key)
    def get_value(d, key):
        value = d.get(key, '')
        if isinstance(value, dict):
            return value.get('value', '')
        return value
    
    email = get_value(data, 'email')
    phone = get_value(data, 'phone')
    
    # Check mandatory fields
    mandatory_results = _check_mandatory_fields(data)
    
    # Validate formats
    email_valid = _validate_email(email)
    phone_valid = _validate_phone(phone)
    
    validation_results = {
        'mandatory_fields': mandatory_results,
        'format_validation': {
            'email_valid': email_valid,
            'phone_valid': phone_valid,
            'email_error': None if email_valid else 'Invalid email format',
            'phone_error': None if phone_valid else 'Invalid phone format'
        }
    }
    
    # Calculate overall confidence
    confidence = _calculate_confidence(data, validation_results)
    
    # Data is valid if all mandatory fields present and at least email OR phone is valid
    all_mandatory_present = all(v['present'] for v in mandatory_results.values())
    has_valid_contact = email_valid or phone_valid
    
    validation_results['overall_confidence'] = confidence
    validation_results['is_valid'] = all_mandatory_present and has_valid_contact
    
    return validation_results


# ============================================================================
# DATABASE TOOLS
# ============================================================================

@tool
def save_candidate_to_db(candidate_json: str, resume_path: str) -> Dict[str, Any]:
    """
    Save parsed candidate information to the database.
    If candidate with same email exists, updates the existing record.
    
    Args:
        candidate_json: JSON string with candidate data (name, email, phone, company, 
                       designation, skills, experience_years, confidence_scores)
        resume_path: Path to the original resume file
    
    Returns:
        Dict with success status, candidate_id, is_update flag, and message
    """
    from database.connection import get_db_connection
    import uuid
    import json
    from datetime import datetime
    
    try:
        # Parse candidate data
        candidate = json.loads(candidate_json)
        email = candidate.get('email', '')
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if candidate with same email already exists
        cursor.execute("SELECT id FROM candidates WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        # Convert skills list to JSON string
        skills_json = json.dumps(candidate.get('skills', []))
        confidence_json = json.dumps(candidate.get('confidence_scores', {}))
        
        if existing:
            # UPDATE existing candidate
            candidate_id = existing[0]
            cursor.execute("""
                UPDATE candidates SET
                    name = ?,
                    phone = ?,
                    company = ?,
                    designation = ?,
                    skills = ?,
                    experience_years = ?,
                    resume_path = ?,
                    confidence_scores = ?,
                    status = ?,
                    updated_at = ?
                WHERE email = ?
            """, (
                candidate.get('name', ''),
                candidate.get('phone', ''),
                candidate.get('company', ''),
                candidate.get('designation', ''),
                skills_json,
                candidate.get('experience_years', 0),
                resume_path,
                confidence_json,
                'PARSED',
                datetime.utcnow().isoformat(),
                email
            ))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'candidate_id': candidate_id,
                'is_update': True,
                'message': f'Candidate already existed. Data updated for ID: {candidate_id}'
            }
        else:
            # INSERT new candidate
            candidate_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO candidates (
                    id, name, email, phone, company, designation, 
                    skills, experience_years, resume_path, confidence_scores,
                    status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                candidate_id,
                candidate.get('name', ''),
                email,
                candidate.get('phone', ''),
                candidate.get('company', ''),
                candidate.get('designation', ''),
                skills_json,
                candidate.get('experience_years', 0),
                resume_path,
                confidence_json,
                'PARSED',
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'candidate_id': candidate_id,
                'is_update': False,
                'message': f'New candidate saved with ID: {candidate_id}'
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@tool
def log_agent_action(candidate_id: str, action: str, tool_used: str, input_data: str, output_data: str) -> Dict[str, Any]:
    """
    Log an agent action to the agent_logs table.
    
    Args:
        candidate_id: ID of the candidate being processed
        action: Description of the action (e.g., 'parsed_resume', 'validated_data')
        tool_used: Name of the tool used
        input_data: JSON string of the input to the tool
        output_data: JSON string of the output from the tool
    
    Returns:
        Dict with success status and log_id or error message
    """
    from database.connection import get_db_connection
    import uuid
    from datetime import datetime
    
    try:
        # Generate UUID for log entry
        log_id = str(uuid.uuid4())
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert log entry
        cursor.execute("""
            INSERT INTO agent_logs (
                id, candidate_id, action, tool_used, input, output, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            log_id,
            candidate_id,
            action,
            tool_used,
            input_data,
            output_data,
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'log_id': log_id,
            'message': f'Agent action logged successfully'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# ============================================================================
# EXPORT TOOLS LIST
# ============================================================================

tools_list = [
    extract_text_from_pdf,
    extract_text_from_txt,
    validate_candidate_data,
    save_candidate_to_db,
    log_agent_action,
]
