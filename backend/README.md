# Backend API

Simple Flask API for TraqCheck CandidateVerify system.

## Setup

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Initialize database** (if not already done):
```bash
python database/db_init.py
```

3. **Run the API:**
```bash
python app.py
```

The API will start on `http://localhost:5000`

## API Endpoints

### 1. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "message": "API is running"
}
```

### 2. Create Candidate
```
POST /candidates
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91-1234567890",
  "company": "Tech Corp",
  "designation": "Senior Developer",
  "skills": ["Python", "SQL", "Machine Learning"],
  "experience_years": 5,
  "resume_path": "/uploads/resume.pdf"
}
```

**Required Fields:**
- `name`
- `email`
- `phone`
- `resume_path`

**Response (201):**
```json
{
  "message": "Candidate created successfully",
  "candidate_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 3. Get Candidate
```
GET /candidates/<candidate_id>
```

**Response (200):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91-1234567890",
  "company": "Tech Corp",
  "designation": "Senior Developer",
  "skills": ["Python", "SQL", "Machine Learning"],
  "experience_years": 5,
  "resume_path": "/uploads/resume.pdf",
  "status": "PARSED",
  "document_status": "NOT_REQUESTED",
  "created_at": "2025-12-06 14:30:00"
}
```

**Response (404):**
```json
{
  "error": "Candidate not found"
}
```

## Testing with cURL

### Create a candidate:
```bash
curl -X POST http://localhost:5000/candidates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+91-9876543210",
    "company": "DevCorp",
    "designation": "Software Engineer",
    "skills": ["JavaScript", "React", "Node.js"],
    "experience_years": 3,
    "resume_path": "/uploads/jane_resume.pdf"
  }'
```

### Get a candidate:
```bash
curl http://localhost:5000/candidates/<candidate_id>
```

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── database/
│   ├── db_init.py        # Database initialization
│   ├── schema.sql        # Database schema
│   └── traqcheck.db      # SQLite database file
└── README.md             # This file
```
