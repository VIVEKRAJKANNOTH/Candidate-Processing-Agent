"""
Resume Parser Agent with Autonomous Tool Selection
Agent decides which tools to use from the provided tools_list
"""

from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from pydantic import BaseModel
import re
import json

from .tools import tools_list, CandidateInfo
from .config import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE
from .prompts import SYSTEM_PROMPT, RESUME_PARSING_PROMPT


# ============================================================================
# MAIN PARSING FUNCTION
# ============================================================================

def parse_resume_with_agent(file_path: str) -> Dict[str, Any]:
    """
    Parse resume using agent with autonomous tool selection.
    The agent decides which tools to call based on the file path and task.
    
    """
    try:
        print(f"\n{'='*60}")
        print(f"Running Resume Parser Agent on: {file_path}")
        print(f"{'='*60}")
        
        # Initialize LLM (without structured output - agent will use submit_final_response tool)
        llm = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=TEMPERATURE,
            model_kwargs={
            "response_mime_type": "application/json",  # Force JSON response
            "response_schema": CandidateInfo.model_json_schema()  # Provide schema
        }
        )
        
        # Create agent prompt with placeholders
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", RESUME_PARSING_PROMPT + "\n\nFile to process: {input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        # Create agent with all tools from tools_list
        # Agent will autonomously decide which tools to use
        agent = create_tool_calling_agent(llm, tools_list, prompt)
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools_list,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            return_intermediate_steps=True
        )
        
        # Run agent with the file path - agent decides which tools to call
        result = agent_executor.invoke({
            "input": f"Parse the resume at this file path and extract all candidate information: {file_path}"
        })

        output = result["output"]
        print(f"\nAgent Output: {output}")
        
        # Strip markdown code blocks and parse
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', output)
        if json_match:
            parsed_data = json.loads(json_match.group(1))
        else:
            parsed_data = json.loads(output)  # Try parsing as plain JSON

        return {
            'success': True,
            'data': parsed_data
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

