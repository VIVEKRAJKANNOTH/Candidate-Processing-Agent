#!/bin/bash

# API Test Script
# Run this to test the Flask API endpoints

BASE_URL="http://localhost:5000"

echo "================================"
echo "Testing TraqCheck Backend API"
echo "================================"
echo ""

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s $BASE_URL/health | python -m json.tool
echo ""
echo ""

# Test 2: Create Candidate
echo "2. Creating a new candidate..."
RESPONSE=$(curl -s -X POST $BASE_URL/candidates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "phone": "+91-1111111111",
    "company": "Test Company",
    "designation": "Test Engineer",
    "skills": ["Python", "Flask", "SQLite"],
    "experience_years": 4,
    "resume_path": "/uploads/test_resume.pdf"
  }')

echo $RESPONSE | python -m json.tool

# Extract candidate_id from response
CANDIDATE_ID=$(echo $RESPONSE | python -c "import sys, json; print(json.load(sys.stdin).get('candidate_id', ''))")

echo ""
echo "Created Candidate ID: $CANDIDATE_ID"
echo ""
echo ""

# Test 3: Get Candidate
if [ ! -z "$CANDIDATE_ID" ]; then
  echo "3. Fetching candidate details..."
  curl -s $BASE_URL/candidates/$CANDIDATE_ID | python -m json.tool
  echo ""
  echo ""
else
  echo "3. Skipping fetch test (no candidate_id)"
  echo ""
fi

# Test 4: Test 404 Error
echo "4. Testing 404 error (invalid ID)..."
curl -s $BASE_URL/candidates/invalid-id-123 | python -m json.tool
echo ""
echo ""

echo "================================"
echo "All tests completed!"
echo "================================"
