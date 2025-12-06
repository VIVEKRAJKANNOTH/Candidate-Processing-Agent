import sqlite3
import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class Database:
    """SQLite database manager for candidate verification system"""
    
    def __init__(self, db_path: str = "backend/database/traqcheck.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def connect(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Enable column access by name
        # Enable foreign key constraints
        self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_schema(self):
        """Create database tables from schema file"""
        schema_path = Path(__file__).parent / "schema.sql"
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        cursor = self.connection.cursor()
        cursor.executescript(schema_sql)
        self.connection.commit()
        print(f"✅ Database initialized successfully at {self.db_path}")
    
    def generate_uuid(self) -> str:
        """Generate UUID for primary keys"""
        return str(uuid.uuid4())
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp in ISO 8601 format"""
        return datetime.utcnow().isoformat()
    
    def json_to_text(self, data: Dict[Any, Any]) -> str:
        """Convert JSON dict to text for storage"""
        return json.dumps(data) if data else None
    
    def text_to_json(self, text: str) -> Dict[Any, Any]:
        """Convert stored text back to JSON dict"""
        return json.loads(text) if text else {}


def init_database(db_path: str = "backend/database/traqcheck.db"):
    """Initialize the database with schema"""
    db = Database(db_path)
    db.connect()
    db.initialize_schema()
    db.close()
    return db_path


if __name__ == "__main__":
    # Initialize database when run as script
    db_path = init_database()
    print(f"Database created at: {db_path}")
