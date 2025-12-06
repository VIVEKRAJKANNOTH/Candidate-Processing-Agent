PHASE 2: DOCUMENT REQUEST & COLLECTION
Step 7: HR Triggers Document Request
HR Dashboard (React)
  ↓
Candidate list shows:
┌──────────────────────────────────────────────────────┐
│ Name          Email              Status    Actions   │
│ Rahul Sharma  rahul@gmail.com   VALIDATED [Request]  │
└──────────────────────────────────────────────────────┘
  ↓
HR clicks "Request Documents" button
  ↓
POST /candidates/uuid-123-456/request-documents
Step 8: Backend Triggers Agent
Flask API receives request
  ↓
Fetches candidate data from database:
SELECT * FROM candidates WHERE id = 'uuid-123-456'
  ↓
Triggers Agent with context:
{
  "candidate_id": "uuid-123-456",
  "name": "Rahul Sharma",
  "email": "rahul@gmail.com",
  "company": "TCS",
  "designation": "Software Engineer"
}
Step 9: Agent Generates Personalized Email
🤖 Agent Orchestrator starts
  ↓
┌─────────────────────────────────────┐
│ Tool 5: Document Request Generator  │
│                                     │
│ Input: Candidate context            │
│                                     │
│ Agent uses GPT-4 to generate:       │
│ - Personalized greeting             │
│ - Professional tone                 │
│ - Context-aware content             │
│ - Clear instructions                │
│ - Upload link with candidate_id     │
│ - Deadline (7 days)                 │
│                                     │
│ Prompt to GPT-4:                    │
│ "Generate professional email        │
│  requesting PAN & Aadhaar for       │
│  Rahul Sharma, Software Engineer    │
│  at TCS. Include upload link and    │
│  7-day deadline."                   │
└─────────────────────────────────────┘
  ↓
Generated Email:
─────────────────────────────────────
Subject: Document Submission Required - Background Verification

Dear Rahul Sharma,

We hope this email finds you well.

As part of the background verification process for your 
application to the Software Engineer position at TCS, 
we kindly request you to submit the following identity 
documents:

1. PAN Card (scanned copy or clear photo)
2. Aadhaar Card (scanned copy or clear photo)

Please upload your documents using this secure link:
👉 https://yourapp.com/submit-docs?candidate_id=uuid-123-456

This link is valid for 7 days. Please submit at your 
earliest convenience to avoid delays.

If you have questions, contact us at hr@company.com

Thank you for your cooperation.

Best regards,
HR Team
─────────────────────────────────────
Step 10: Send Email
┌─────────────────────────────────────┐
│ Tool 6: Email Sender (SendGrid)     │
│                                     │
│ - to: rahul@gmail.com               │
│ - subject: "Document Submission..." │
│ - body: [generated email]           │
│ - from: hr@company.com              │
│                                     │
│ SendGrid API call                   │
│ Returns: message_id, status         │
└─────────────────────────────────────┘
  ↓
Email sent successfully ✉️
Step 11: Update Database & Log
UPDATE candidates SET:
- document_status = "REQUESTED"
- documents_requested_at = NOW()

INSERT INTO agent_logs:
- candidate_id: uuid-123-456
- action: "DOCUMENT_REQUEST_SENT"
- details: {
    "email_sent": true,
    "sent_to": "rahul@gmail.com",
    "upload_link": "https://yourapp.com/submit-docs?candidate_id=uuid-123-456",
    "message_id": "sendgrid-msg-123"
  }
- timestamp: NOW()
Step 12: Return Response
Flask API returns:
{
  "success": true,
  "message": "Document request sent to rahul@gmail.com",
  "candidate_id": "uuid-123-456",
  "upload_link": "https://yourapp.com/submit-docs?candidate_id=uuid-123-456"
}
  ↓
React shows success notification:
"✅ Document request sent to Rahul Sharma"
