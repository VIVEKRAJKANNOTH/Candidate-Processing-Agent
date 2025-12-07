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

class CandidateInfo(BaseModel):
    """Structured output model for candidate information"""
    name: str = Field(description="Full name of the candidate")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number with country code")
    company: str = Field(default="", description="Current or most recent company")
    designation: str = Field(default="", description="Current or most recent job title")
    skills: List[str] = Field(default_factory=list, description="List of technical skills")
    experience_years: int = Field(default=0, description="Total years of professional experience")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+91-9876543210",
                "company": "Tech Corp",
                "designation": "Senior Software Engineer",
                "skills": ["Python", "Django", "React"],
                "experience_years": 5
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
# EXPORT TOOLS LIST
# ============================================================================

tools_list = [
    extract_text_from_pdf,
    extract_text_from_txt,
]
