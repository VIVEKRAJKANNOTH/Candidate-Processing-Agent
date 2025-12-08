"""

"""

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from .tools import tools_list, CandidateInfo
from .config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE, FRONTEND_BASE_URL
from .prompts import SYSTEM_PROMPT, RESUME_PARSING_PROMPT


# ============================================================================
# EMAIL GENERATION AGENT
# ============================================================================

def generate_document_request_email_agent(candidate_id: str) -> Dict[str, Any]:
    """
    Generate a personalized document request email for a candidate and send it.
    
    Uses LangGraph create_react_agent with:
    - Candidate data passed in the message
    - send_email_gmail tool to send the email
    - DocumentRequestEmail Pydantic model for structured output
    
    Args:
        candidate_id: UUID of the candidate
        
    Returns:
        Dict with 'success', 'email' (DocumentRequestEmail), or 'error'
    """
    from .tools import (
        get_candidate_by_id, 
        DocumentRequestEmail, 
        send_email_gmail,
        update_candidate_document_status,
        log_agent_action
    )
    from .prompts import EMAIL_GENERATION_PROMPT
    from datetime import datetime, timedelta
    
    try:
        print(f"\n{'='*60}")
        print(f"Running Email Generation Agent for: {candidate_id}")
        print(f"{'='*60}")
        
        # Step 1: Fetch candidate data FIRST (before agent call)
        candidate_result = get_candidate_by_id.invoke(candidate_id)
        
        if not candidate_result.get('success'):
            return {
                'success': False,
                'error': candidate_result.get('error', 'Failed to fetch candidate')
            }
        
        candidate = candidate_result['candidate']
        deadline = (datetime.now() + timedelta(days=7)).strftime('%B %d, %Y')
        upload_link = f"{FRONTEND_BASE_URL}/submit-docs?candidate_id={candidate_id}"
        
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0
        )
        
        # Email generation prompt with tool usage instructions
        agent_prompt = f"""
{EMAIL_GENERATION_PROMPT}

You have access to the send_email_gmail tool. After generating the email content, 
you MUST call the send_email_gmail tool to send the email.

Workflow:
1. Generate the email content using the candidate information provided
2. Call send_email_gmail tool with: to_email, subject, and body
3. Return the structured response with the email details
"""
        
        # Create ReAct agent with send_email_gmail tool only
        # DB update and logging will be done outside agent for better control
        graph = create_react_agent(
            model=llm,
            tools=[send_email_gmail],
            prompt=agent_prompt,
            response_format=DocumentRequestEmail
        )
        
        # Invoke agent with candidate data in message
        result = graph.invoke({
            "messages": [(
                "user", 
                f"""Generate and send a document request email:

Candidate Information:
- Name: {candidate.get('name', 'Candidate')}
- Email: {candidate.get('email', '')}

Upload Link: {upload_link}
Deadline: {deadline}

Generate a professional email requesting PAN and Aadhaar documents, then use the send_email_gmail tool to send it to the candidate."""
            )]
        })
        
        # Extract structured response
        structured_response = result.get("structured_response")
        
        # Count LLM calls by analyzing messages
        messages = result.get("messages", [])
        llm_calls = 0
        tool_calls = 0
        for msg in messages:
            msg_type = type(msg).__name__
            if msg_type == 'AIMessage':
                llm_calls += 1
            elif msg_type == 'ToolMessage':
                tool_calls += 1
        
        print(f"\n[AGENT STATS]")
        print(f"  LLM Calls: {llm_calls}")
        print(f"  Tool Calls: {tool_calls}")
        print(f"  Total Messages: {len(messages)}")
        
        # Check if email was sent by looking at tool messages
        send_result = None
        for msg in messages:
            if hasattr(msg, 'name') and msg.name == 'send_email_gmail':
                # Parse the string result as JSON
                import json
                try:
                    send_result = json.loads(msg.content) if isinstance(msg.content, str) else msg.content
                except:
                    send_result = msg.content
                break
        
        if structured_response:
            print(f"Email generated and sent successfully via agent")
            email_data = structured_response.model_dump() if hasattr(structured_response, 'model_dump') else structured_response
            
            # If email was sent successfully, update DB and log the action
            if send_result and send_result.get('success'):
                print(f"\n[DEBUG] Email sent successfully, updating DB...")
                print(f"[DEBUG] candidate_id: {candidate_id}")
                
                # Update candidate document status - call the underlying function directly
                db_update = update_candidate_document_status.func(
                    candidate_id=candidate_id,
                    document_status='REQUESTED'
                )
                print(f"[DEBUG] db_update result: {db_update}")
                
                # Log the agent action
                log_result = log_agent_action.func(
                    candidate_id=candidate_id,
                    action='DOCUMENT_REQUEST_SENT',
                    tool_used='send_email_gmail',
                    input_data=json.dumps({
                        'to_email': email_data.get('candidate_email'),
                        'subject': email_data.get('subject'),
                        'upload_link': upload_link
                    }),
                    output_data=json.dumps(send_result)
                )
                print(f"[DEBUG] log_result: {log_result}")
                
                return {
                    'success': True,
                    'candidate_id': candidate_id,
                    'email': email_data,
                    'send_result': send_result,
                    'db_update': db_update,
                    'log_result': log_result
                }
            
            return {
                'success': True,
                'candidate_id': candidate_id,
                'email': email_data,
                'send_result': send_result
            }
        else:
            # Fallback: return last message content
            if messages:
                last_message = messages[-1]
                content = str(last_message.content) if hasattr(last_message, 'content') else str(last_message)
                
                return {
                    'success': True,
                    'candidate_id': candidate_id,
                    'email': {
                        'candidate_name': candidate.get('name'),
                        'candidate_email': candidate.get('email'),
                        'subject': 'Document Verification Request',
                        'body': content,
                        'upload_link': upload_link
                    },
                    'send_result': send_result,
                    'warning': 'Fallback: structured_response was None'
                }
            return {
                'success': False,
                'error': 'No response received from email agent'
            }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error generating email: {str(e)}")
        
        return {
            'success': False,
            'error': str(e),
            'traceback': error_trace
        }
