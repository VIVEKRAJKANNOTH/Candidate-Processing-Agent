"""
Resume Parser Agent with LangGraph ReAct Agent and Structured Output
Uses create_react_agent with Pydantic response_format for guaranteed JSON structure
"""

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from .tools import tools_list, CandidateInfo
from .config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE
from .prompts import SYSTEM_PROMPT, RESUME_PARSING_PROMPT


# ============================================================================
# MAIN PARSING FUNCTION
# ============================================================================

def parse_resume_with_agent(file_path: str) -> Dict[str, Any]:
    """
    Parse resume using LangGraph ReAct agent with structured output.
    
    Uses create_react_agent with response_format parameter to ensure
    the output always conforms to the CandidateInfo Pydantic schema.
    
    Args:
        file_path: Path to the resume file (PDF or TXT)
        
    Returns:
        Dict with 'success', 'data' (CandidateInfo dict), or 'error'
    """
    try:
        print(f"\n{'='*60}")
        print(f"Running LangGraph ReAct Agent on: {file_path}")
        print(f"{'='*60}")
        
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=TEMPERATURE
        )
        
        # Combine system prompt with parsing instructions
        full_prompt = f"{SYSTEM_PROMPT}\n\n{RESUME_PARSING_PROMPT}"
        
        # Create ReAct agent with structured output via response_format
        graph = create_react_agent(
            model=llm,
            tools=tools_list,
            prompt=full_prompt,
            response_format=CandidateInfo  # Pydantic schema ensures JSON structure
        )
        
        # Invoke agent with the file path
        result = graph.invoke({
            "messages": [("user", f"Parse the resume at this file path and extract all candidate information: {file_path}")]
        })
        
        # Extract the structured response
        structured_response = result.get("structured_response")
        
        if structured_response:
            print(f"\nStructured output received")
            return {
                'success': True,
                'data': structured_response.model_dump() if hasattr(structured_response, 'model_dump') else structured_response
            }
        else:
            # Fallback: check messages for any response
            messages = result.get("messages", [])
            if messages:
                last_message = messages[-1]
                print(f"\nNo structured_response, using last message")
                return {
                    'success': True,
                    'data': {'raw_response': str(last_message.content) if hasattr(last_message, 'content') else str(last_message)},
                    'warning': 'structured_response was None, returning raw message'
                }
            return {
                'success': False,
                'error': 'No response received from agent'
            }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error parsing resume: {str(e)}")
        print(error_trace)
        
        return {
            'success': False,
            'error': str(e),
            'traceback': error_trace
        }
