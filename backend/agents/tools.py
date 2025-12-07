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
    import sqlite3
    import uuid
    import json
    from datetime import datetime
    
    try:
        # Parse candidate data
        candidate = json.loads(candidate_json)
        email = candidate.get('email', '')
        
        # Connect to database
        db_path = "database/traqcheck.db"
        conn = sqlite3.connect(db_path)
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
    import sqlite3
    import uuid
    from datetime import datetime
    
    try:
        # Generate UUID for log entry
        log_id = str(uuid.uuid4())
        
        # Connect to database
        db_path = "database/traqcheck.db"
        conn = sqlite3.connect(db_path)
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
