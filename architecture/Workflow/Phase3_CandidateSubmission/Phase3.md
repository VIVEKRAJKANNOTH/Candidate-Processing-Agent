📤 PHASE 3: CANDIDATE DOCUMENT SUBMISSION
Step 13: Candidate Receives Email
Candidate's Gmail Inbox
  ↓
Opens email
  ↓
Sees personalized message
  ↓
Clicks: "Upload Documents" link
  ↓
Browser opens:
https://yourapp.com/submit-docs?candidate_id=uuid-123-456
Step 14: React Upload Page Loads
React Router matches route: /submit-docs
  ↓
DocumentSubmission component loads
  ↓
useSearchParams() extracts: candidate_id = "uuid-123-456"
  ↓
Optional: Fetch candidate name for personalization
GET /api/candidates/uuid-123-456
  ↓
Returns: { name: "Rahul Sharma" }
  ↓
Page displays:
┌────────────────────────────────────────┐
│        Document Submission             │
│    Welcome, Rahul Sharma!              │
│                                        │
│  Upload PAN Card:   [Choose File]     │
│  Upload Aadhaar:    [Choose File]     │
│                                        │
│         [Submit Documents]             │
└────────────────────────────────────────┘
Step 15: Candidate Uploads Files
User selects files:
- pan_card.jpg
- aadhaar_card.pdf
  ↓
Clicks "Submit Documents"
  ↓
React creates FormData:
{
  pan_card: File(pan_card.jpg),
  aadhaar_card: File(aadhaar_card.pdf)
}
  ↓
POST /candidates/uuid-123-456/submit-documents
Content-Type: multipart/form-data
Step 16: Backend Receives & Validates
Flask API receives upload
  ↓
Validation checks:
1. Candidate exists?
   SELECT * FROM candidates WHERE id = 'uuid-123-456'
   ✅ Found
   
2. Documents already submitted?
   SELECT * FROM documents WHERE candidate_id = 'uuid-123-456'
   ✅ No existing records
   
3. Files present?
   ✅ pan_card: Yes
   ✅ aadhaar_card: Yes
   
4. File types valid?
   ✅ pan_card.jpg: Valid (image/jpeg)
   ✅ aadhaar_card.pdf: Valid (application/pdf)
   
5. File sizes OK?
   ✅ pan_card.jpg: 2.3 MB (< 5MB limit)
   ✅ aadhaar_card.pdf: 1.8 MB (< 5MB limit)
Step 17: Store Files
Save files to storage:
  ↓
Create secure filenames:
- uuid-123-456_PAN_20241206_153045_pan_card.jpg
- uuid-123-456_AADHAAR_20241206_153045_aadhaar_card.pdf
  ↓
Storage options:
Option A: Local filesystem
  path = /uploads/documents/uuid-123-456_PAN_...jpg
  
Option B: AWS S3 (recommended for production)
  s3://hr-documents-bucket/uuid-123-456_PAN_...jpg
  ↓
Files saved successfully
Step 18: Database Updates
INSERT INTO documents (2 records):
1. PAN Card:
   - id: doc-uuid-1
   - candidate_id: uuid-123-456
   - document_type: "PAN"
   - file_path: "/uploads/documents/uuid-123-456_PAN_..."
   - file_name: "pan_card.jpg"
   - file_size: 2400000
   - uploaded_at: NOW()
   - verification_status: "PENDING"

2. Aadhaar Card:
   - id: doc-uuid-2
   - candidate_id: uuid-123-456
   - document_type: "AADHAAR"
   - file_path: "/uploads/documents/uuid-123-456_AADHAAR_..."
   - file_name: "aadhaar_card.pdf"
   - file_size: 1900000
   - uploaded_at: NOW()
   - verification_status: "PENDING"
  ↓
UPDATE candidates:
- document_status = "SUBMITTED"
- documents_submitted_at = NOW()
  ↓
INSERT INTO agent_logs:
- candidate_id: uuid-123-456
- action: "DOCUMENTS_SUBMITTED"
- details: {
    "pan_file": "uuid-123-456_PAN_...",
    "aadhaar_file": "uuid-123-456_AADHAAR_..."
  }
- timestamp: NOW()
Step 19: Send Confirmation Email
Send confirmation to candidate:
─────────────────────────────────────
To: rahul@gmail.com
Subject: Documents Received - Confirmation

Dear Rahul Sharma,

Thank you! We have successfully received your 
documents:
✅ PAN Card
✅ Aadhaar Card

Our team will review them shortly. You'll be 
notified once verification is complete.

Best regards,
HR Team
─────────────────────────────────────
Step 20: Return Success Response
Flask API returns:
{
  "success": true,
  "message": "Documents submitted successfully",
  "candidate_id": "uuid-123-456",
  "documents": {
    "pan": "uuid-123-456_PAN_20241206_153045_pan_card.jpg",
    "aadhaar": "uuid-123-456_AADHAAR_20241206_153045_aadhaar_card.pdf"
  }
}
  ↓
React shows success message:
┌────────────────────────────────────────┐
│   ✅ Success!                          │
│                                        │
│   Documents submitted successfully!    │
│   You will receive a confirmation      │
│   email shortly.                       │
└────────────────────────────────────────┘

🎛️ BACKEND: HR VIEWS SUBMITTED DOCUMENTS
Step 21: HR Views Candidate Profile
HR Dashboard
  ↓
GET /candidates/uuid-123-456
  ↓
Returns full candidate profile:
{
  "id": "uuid-123-456",
  "name": "Rahul Sharma",
  "email": "rahul@gmail.com",
  "phone": "+91 9876543210",
  "company": "TCS",
  "designation": "Software Engineer",
  "confidence_scores": {...},
  "status": "VALIDATED",
  "document_status": "SUBMITTED",
  "documents": [
    {
      "type": "PAN",
      "file_name": "pan_card.jpg",
      "uploaded_at": "2024-12-06T15:30:45Z",
      "verification_status": "PENDING",
      "download_url": "/api/documents/doc-uuid-1/download"
    },
    {
      "type": "AADHAAR",
      "file_name": "aadhaar_card.pdf",
      "uploaded_at": "2024-12-06T15:30:45Z",
      "verification_status": "PENDING",
      "download_url": "/api/documents/doc-uuid-2/download"
    }
  ]
}
  ↓
React displays:
┌────────────────────────────────────────────────────┐
│ Candidate Profile: Rahul Sharma                    │
│ ─────────────────────────────────────────────────  │
│ Name:         Rahul Sharma              ✅ 95%    │
│ Email:        rahul@gmail.com           ✅ 90%    │
│ Phone:        +91 9876543210            ✅ 85%    │
│ Company:      TCS                       ⚠️ 70%    │
│ Designation:  Software Engineer         ✅ 80%    │
│                                                    │
│ Documents Submitted:                               │
│ ✅ PAN Card       [View] [Download]               │
│ ✅ Aadhaar Card   [View] [Download]               │
└────────────────────────────────────────────────────┘
