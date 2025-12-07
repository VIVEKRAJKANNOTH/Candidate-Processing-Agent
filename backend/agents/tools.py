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

class FieldWithConfidence(BaseModel):
    """Field value with confidence score"""
    value: str = Field(description="Extracted value from the resume")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0", ge=0.0, le=1.0)


class ToolCallRecord(BaseModel):
    """Record of a tool call made by the agent"""
    tool_name: str = Field(description="Name of the tool that was called")
    summary: str = Field(description="Brief summary of what the tool did (input/output)")


class CandidateInfo(BaseModel):
    """Structured output model for candidate information with confidence tracking"""
    
    # Core fields with confidence scores
    name: FieldWithConfidence = Field(description="Full name of the candidate")
    email: FieldWithConfidence = Field(description="Email address of the candidate")
    phone: FieldWithConfidence = Field(description="Phone number with country code")
    company: FieldWithConfidence = Field(description="Current or most recent company")
    designation: FieldWithConfidence = Field(description="Current or most recent job title")
    skills: List[str] = Field(default_factory=list, description="List of technical skills")
    experience_years: int = Field(default=0, description="Total years of professional experience")
    
    # Agent tracking fields
    ai_message: str = Field(description="Condensed summary of the parsing reasoning and key observations")
    tool_calls: List[str] = Field(description="List of tools called during parsing")
    overall_confidence: float = Field(description="Overall confidence in the extraction accuracy", ge=0.0, le=1.0)
    validation_status: str = Field(description="'valid' or 'invalid' based on data validation results")

    class Config:
        json_schema_extra = {
            "example": {
                "name": {"value": "John Doe", "confidence": 0.95},
                "email": {"value": "john.doe@example.com", "confidence": 0.98},
                "phone": {"value": "+91-9876543210", "confidence": 0.90},
                "company": {"value": "Tech Corp", "confidence": 0.85},
                "designation": {"value": "Senior Software Engineer", "confidence": 0.88},
                "skills": ["Python", "Django", "React"],
                "experience_years": 5,
                "ai_message": "Extracted candidate info from PDF resume. Contact details clearly visible in header.",
                "tool_calls": [{"tool_name": "extract_text_from_pdf", "summary": "Extracted 2 pages of text"}],
                "overall_confidence": 0.90,
                "validation_status": "valid"
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
# EXPORT TOOLS LIST
# ============================================================================

tools_list = [
    extract_text_from_pdf,
    extract_text_from_txt,
    validate_candidate_data,
]
