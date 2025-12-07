"""
Resume Parser with Direct Structured Output
Uses llm.with_structured_output() for deterministic extraction (not ReAct agent)

"""

from typing import Dict, Any
import json
from langchain_google_genai import ChatGoogleGenerativeAI

# Import everything we need from tools.py - NO DUPLICATION!
from .tools import (
    CandidateInfo,
    extract_text_from_pdf,
    extract_text_from_txt,
    validate_candidate_data,
    save_candidate_to_db,
)
from .config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE
from .prompts import RESUME_PARSING_PROMPT


# ============================================================================
# HELPER FUNCTION (thin wrapper over tools)
# ============================================================================

def extract_resume_text(file_path: str) -> str:
    """Extract text from resume file based on extension (uses tools.py)"""
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf.invoke(file_path)
    else:
        return extract_text_from_txt.invoke(file_path)


# ============================================================================
# MAIN PARSING FUNCTION
# ============================================================================

def parse_with_structured_llm(file_path: str) -> Dict[str, Any]:
    """
    
    Args:
        file_path: Path to the resume file (PDF or TXT)
        
    Returns:
        Dict with 'success', 'data' (CandidateInfo dict), or 'error'
    """
    try:
        print(f"\n{'='*60}")
        print(f"Parsing resume with Structured Output: {file_path}")
        print(f"{'='*60}")
        
        # Step 1: Extract text from resume (using tools.py)
        print("Step 1: Extracting text from resume...")
        resume_text = extract_resume_text(file_path)
        
        if resume_text.startswith("Error"):
            return {'success': False, 'error': resume_text}
        
        
        print(f"  Extracted {len(resume_text)} characters")
        
        # Step 2: Parse with LLM using structured output
        print("Step 2: Parsing with LLM (structured output)...")
        
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=TEMPERATURE
        )
        
        # Use with_structured_output for direct Pydantic extraction
        structured_llm = llm.with_structured_output(CandidateInfo)
        
        # Create the prompt with resume content
        prompt = f"""{RESUME_PARSING_PROMPT}

Resume Content:
---
{resume_text}
---

Extract all candidate information and provide confidence scores for each field.
Set validation_status to 'valid' if name, email and phone are present, otherwise 'invalid'.
Leave candidate_id and db_status empty for now (will be set after database save).
"""
        
        # Single LLM call with structured output
        candidate_info: CandidateInfo = structured_llm.invoke(prompt)
        print("  Structured output received")
        
        # Step 3: Validate the extracted data (using tools.py)
        print("Step 3: Validating extracted data...")
        candidate_data = candidate_info.model_dump()
        
        # Use validate_candidate_data tool from tools.py
        validation_result = validate_candidate_data.invoke(json.dumps(candidate_data))
        
        # Update validation_status based on actual validation
        if validation_result.get('is_valid'):
            candidate_data['validation_status'] = 'valid'
            print("  ✓ Validation passed")
        else:
            candidate_data['validation_status'] = 'invalid'
            print(f"  ✗ Validation failed: {validation_result.get('format_validation', {})}")
        
        # Add validation details to response
        candidate_data['validation_details'] = {
            'mandatory_fields': validation_result.get('mandatory_fields', {}),
            'format_validation': validation_result.get('format_validation', {}),
            'calculated_confidence': validation_result.get('overall_confidence', 0)
        }
        
        # Step 4: Save to database (using tools.py)
        print("Step 4: Saving to database...")
        
        # Use save_candidate_to_db tool from tools.py
        db_result = save_candidate_to_db.invoke({
            "candidate_json": json.dumps(candidate_data),
            "resume_path": file_path
        })
        
        if db_result.get('success'):
            candidate_data['candidate_id'] = db_result['candidate_id']
            candidate_data['is_update'] = db_result.get('is_update', False)
            if db_result.get('is_update'):
                candidate_data['db_status'] = 'Candidate already existed - data updated'
                print(f"  Updated existing candidate ID: {db_result['candidate_id']}")
            else:
                candidate_data['db_status'] = 'New candidate saved successfully'
                print(f"  Saved new candidate ID: {db_result['candidate_id']}")
        else:
            candidate_data['db_status'] = f"Error: {db_result.get('error', 'Unknown')}"
            print(f"  DB Error: {db_result.get('error')}")
        
        print(f" Parsing complete!")
        
        return {
            'success': True,
            'data': candidate_data
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error parsing resume: {str(e)}")
        
        return {
            'success': False,
            'error': str(e),
            'traceback': error_trace
        }
