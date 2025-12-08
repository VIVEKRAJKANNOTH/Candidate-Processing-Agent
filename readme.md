# TraqCheck

Candidate document verification system built with Flask + React.

## What it does

- Upload resumes → AI extracts candidate info
- Send document request emails to candidates
- Candidates submit their PAN/Aadhaar via unique link
- Track verification status

## Stack

- **Backend:** Flask, LangChain, Gemini AI
- **Frontend:** React + Vite
- **Database:** Turso (cloud SQLite)
- **Storage:** Vercel Blob

## Running locally

```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py

# Frontend
cd frontend
npm install
npm run dev
```

## Env vars

```
GEMINI_API_KEY=
TURSO_DATABASE_URL=
TURSO_AUTH_TOKEN=
GMAIL_ADDRESS=
GMAIL_APP_PASSWORD=
```

## Live

https://traqcheck-candidate-verify.vercel.app
