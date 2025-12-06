AGENT ARCHITECTURE SUMMARY

Single Agent: "Candidate Processing Agent"
Framework: LangGraph
LLM: Gemini 2.0 Flash

Tools Available:
┌────────────────────────────────────────┐
│ 1. PDF Text Extractor                  │
│    - Extracts text from PDF/DOCX       │
│    - Uses: PyPDF2, python-docx         │
└────────────────────────────────────────┘
┌────────────────────────────────────────┐
│ 2. Resume Parser Tool                  │
│    - Gemini 2.0 Flash structured output
│    - Returns: JSON + confidence scores │
└────────────────────────────────────────┘
┌────────────────────────────────────────┐
│ 3. Data Validator Tool                 │
│    - Checks mandatory fields           │
│    - Validates formats (email, phone)  │
│    - Calculates overall confidence     │
└────────────────────────────────────────┘
┌────────────────────────────────────────┐
│ 4. Audit Logger Tool                   │
│    - Logs all agent actions            │
│    - Stores in agent_logs table        │
└────────────────────────────────────────┘
┌────────────────────────────────────────┐
│ 5. Document Request Generator          │
│    - Generates personalized emails     │
│    - Uses Gemini 2.0 Flash for tone & content     │
└────────────────────────────────────────┘
┌────────────────────────────────────────┐
│ 6. Email Sender Tool                   │
│    - Sends via SendGrid/SMTP           │
│    - Returns delivery status           │
└────────────────────────────────────────┘