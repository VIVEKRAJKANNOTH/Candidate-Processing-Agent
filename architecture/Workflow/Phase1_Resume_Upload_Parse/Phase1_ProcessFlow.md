📋 PHASE 1: RESUME UPLOAD & PARSING

Step 1: HR Uploads Resume
    HR Dashboard (React)
    ↓
    User drags/drops resume file (PDF/DOCX)
    ↓
    Clicks "Upload Resume"
    ↓
    POST /candidates/upload
    ↓
    FormData: { file: resume.pdf }

Step 2: Backend Receives File
    Flask API receives request
    ↓
    Validates file type (PDF/DOCX only)
    ↓
    Validates file size (< 10MB)
    ↓
    Saves file temporarily: /tmp/resume_xyz.pdf
    ↓
    Generates candidate_id (UUID)
    ↓
    Triggers Agent Pipeline

Step 3: Agent Orchestration - Parsing
🤖 Agent Orchestrator (LangGraph) starts
  ↓
┌─────────────────────────────────────┐
│ Tool 1: PDF Text Extractor          │
│ - Uses PyPDF2/Pydantic              │
│ - Extracts raw text from PDF        │
│ - Returns: full_text                │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ Tool 2: Resume Parser (Gemini)      │
│ - Input: full_text                  │
│ - Uses structured output      │
│ - Extracts:                         │
│   * name (+ confidence 0-1)         │
│   * email (+ confidence)            │
│   * phone (+ confidence)            │
│   * company (+ confidence)          │
│   * designation (+ confidence)      │
│   * skills[] (+ confidence)│
│ - Returns: structured JSON          │
└─────────────────────────────────────┘
  ↓
Example Output:
{
  "name": {"value": "Rahul Sharma", "confidence": 0.95},
  "email": {"value": "rahul@gmail.com", "confidence": 0.90},
  "phone": {"value": "+91 9876543210", "confidence": 0.85},
  "company": {"value": "TCS", "confidence": 0.70},
  "designation": {"value": "Software Engineer", "confidence": 0.80},
  "skills": {"value": ["Python", "React", "AWS"], "confidence": 0.85},
}
Step 4: Data Validation
┌─────────────────────────────────────┐
│ Tool 3: Data Validator              │
│                                     │
│ Check 1: Mandatory Fields           │
│ - name: ✅ Present                  │
│ - email: ✅ Present                 │
│ - phone: ✅ Present                 │
│                                     │
│ Check 2: Format Validation          │
│ - email: Regex check                │
│ - phone: Indian format (+91/10-dig) │
│ - name: Min 2 words                 │
│                                     │
│ Check 3: Confidence Threshold       │
│ - Calculate avg confidence          │
│ - overall_confidence = 0.85         │
│                                     │
│ Decision Logic:                     │
│ IF confidence >= 0.80:              │
│   status = "VALIDATED"              │
│ ELIF 0.60 <= confidence < 0.80:     │
│   status = "NEEDS_REVIEW"           │
│ ELSE:                               │
│   status = "MANUAL_ENTRY_REQUIRED"  │
└─────────────────────────────────────┘
  ↓
Validation Result:
{
  "is_valid": true,
  "missing_fields": [],
  "invalid_fields": [],
  "overall_confidence": 0.85,
  "status": "VALIDATED"
}
Step 5: Store in Database
┌─────────────────────────────────────┐
│ Tool 4: Audit Logger                │
│ - Logs all extraction steps         │
│ - Logs validation results           │
│ - Logs confidence scores            │
└─────────────────────────────────────┘
  ↓
INSERT INTO candidates:
- id: uuid-123-456
- name: "Rahul Sharma"
- email: "rahul@gmail.com"
- phone: "+91 9876543210"
- company: "TCS"
- designation: "Software Engineer"
- skills: ["Python", "React", "AWS"]
- experience_years: 3
- resume_path: "/uploads/resume_xyz.pdf"
- confidence_scores: {...}
- status: "VALIDATED"
- document_status: "NOT_REQUESTED"
- created_at: NOW()

INSERT INTO agent_logs:
- candidate_id: uuid-123-456
- action: "RESUME_PARSED"
- tool_used: "Resume Parser Tool"
- input: {full_text: "..."}
- output: {extracted_data: {...}}
- timestamp: NOW()
Step 6: Return to Frontend
Flask API returns response:
{
  "success": true,
  "candidate_id": "uuid-123-456",
  "status": "VALIDATED",
  "data": {
    "name": "Rahul Sharma",
    "email": "rahul@gmail.com",
    "phone": "+91 9876543210",
    "company": "TCS",
    "designation": "Software Engineer",
    "confidence_scores": {
      "name": 0.95,
      "email": 0.90,
      "phone": 0.85,
      "overall": 0.85
    }
  }
}
  ↓
React Dashboard updates:
- Shows new candidate in table
- Displays confidence scores with color coding:
  🟢 Green (80-100%): High confidence
  🟡 Yellow (60-79%): Needs review
  🔴 Red (<60%): Manual verification
