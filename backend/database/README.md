# Database Documentation

## Overview
This directory contains the SQLite database schema and initialization scripts for the TraqCheck CandidateVerify system.

## Database: SQLite

**Why SQLite?**
- ✅ Free and open-source
- ✅ No separate server required
- ✅ Built into Python (sqlite3 module)
- ✅ Single file database
- ✅ Perfect for development and small-to-medium applications

## Files

- **`schema.sql`** - Database schema definition
- **`db_init.py`** - Database initialization script
- **`traqcheck.db`** - The actual database file (created after initialization)
- **`migrations/`** - Database migration files
- **`models/`** - ORM models (if using SQLAlchemy or similar)
- **`seeds/`** - Sample data for testing

## Tables

### 1. `candidates`
Stores candidate information and verification status.

**Key Fields:**
- `id` - Unique identifier (UUID as TEXT)
- `name`, `email`, `phone` - Contact information
- `company`, `designation` - Current employment
- `skills` - JSON stored as TEXT
- `confidence_scores` - Parsing confidence scores (JSON)
- `status` - Current processing status
- `document_status` - Document collection status

### 2. `documents`
Stores uploaded documents for each candidate.

**Key Fields:**
- `candidate_id` - Foreign key to candidates table
- `document_type` - Type of document (e.g., "AADHAR", "PAN", "DEGREE")
- `file_path` - Storage location
- `verification_status` - Verification status

### 3. `agent_logs`
Tracks all agent actions for observability.

**Key Fields:**
- `candidate_id` - Related candidate
- `action` - Action performed
- `tool_used` - Tool/function used
- `input`/`output` - JSON data (stored as TEXT)

## Schema Differences: PostgreSQL → SQLite

| Feature | PostgreSQL | SQLite Equivalent |
|---------|-----------|-------------------|
| UUID | `UUID` type with `gen_random_uuid()` | `TEXT` + Python uuid4() |
| JSON | `JSONB` | `TEXT` + Python json module |
| Timestamp | `TIMESTAMP`, `NOW()` | `TEXT` + `datetime('now')` |
| BigInt | `BIGINT` | `INTEGER` |

## Quick Start

### Initialize the Database

```bash
# From project root
python backend/database/db_init.py
```

This will create `backend/database/traqcheck.db` with all tables and indexes.

### Using the Database in Your Code

```python
from backend.database.db_init import Database

# Create database instance
db = Database()
db.connect()

# Insert a candidate
cursor = db.connection.cursor()
cursor.execute("""
    INSERT INTO candidates (id, name, email, phone, resume_path)
    VALUES (?, ?, ?, ?, ?)
""", (db.generate_uuid(), "John Doe", "john@example.com", "1234567890", "/path/to/resume.pdf"))

db.connection.commit()
db.close()
```

## Migration Strategy

For future schema changes:
1. Create a new migration file in `migrations/` directory
2. Name it: `YYYYMMDD_HHMMSS_description.sql`
3. Apply migrations manually or create a migration runner script

## Performance Considerations

- **Indexes** are created for frequently queried fields
- **Foreign Keys** are enabled for data integrity
- **JSON fields** are stored as TEXT (use sparingly for search operations)
- For heavy JSON querying, consider PostgreSQL in production

## Future Considerations

If you outgrow SQLite:
- **PostgreSQL** - For production, complex queries, concurrent writes
- **MySQL** - Popular alternative with good tooling
- **MongoDB** - If you need flexible JSON documents

The schema is designed to be easily portable to PostgreSQL when needed.
