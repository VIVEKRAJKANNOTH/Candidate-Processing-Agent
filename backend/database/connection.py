"""
Database connection utility for TraqCheck
Supports both local SQLite and Turso (libsql) for deployment
"""
import os
from typing import Any, List, Tuple, Optional

# Check if we're in production (Turso) or local (SQLite)
TURSO_DATABASE_URL = os.getenv('TURSO_DATABASE_URL')
TURSO_AUTH_TOKEN = os.getenv('TURSO_AUTH_TOKEN')

# Use Turso if environment variables are set
USE_TURSO = bool(TURSO_DATABASE_URL and TURSO_AUTH_TOKEN)


class TursoRowWrapper:
    """Wrapper to make Turso rows accessible by column name like sqlite3.Row"""
    def __init__(self, row, columns):
        self._data = dict(zip(columns, row)) if row else {}
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self._data.values())[key]
        return self._data.get(key)
    
    def keys(self):
        return self._data.keys()
    
    def values(self):
        return self._data.values()
    
    def items(self):
        return self._data.items()
    
    def get(self, key, default=None):
        return self._data.get(key, default)


class TursoCursorWrapper:
    """Wrapper to make Turso cursor behave like sqlite3 cursor"""
    def __init__(self, result, columns=None):
        self._result = result
        self._columns = columns or []
        self._rows = list(result) if result else []
        self._index = 0
        self.rowcount = len(self._rows)
    
    def fetchone(self):
        if self._index < len(self._rows):
            row = self._rows[self._index]
            self._index += 1
            return TursoRowWrapper(row, self._columns)
        return None
    
    def fetchall(self):
        remaining = self._rows[self._index:]
        self._index = len(self._rows)
        return [TursoRowWrapper(row, self._columns) for row in remaining]


class DatabaseConnection:
    """
    Unified database connection that works with both SQLite and Turso.
    Provides a common interface regardless of the backend.
    """
    
    def __init__(self):
        self.conn = None
        self.is_turso = USE_TURSO
        self._last_columns = []
    
    def cursor(self):
        """Return self as cursor for compatibility with sqlite3 patterns"""
        return self
    
    def execute(self, query: str, params: Tuple = ()) -> 'DatabaseConnection':
        """Execute a query with parameters"""
        if self.is_turso:
            # Turso uses libsql
            result = self.conn.execute(query, params)
            # Store column names from description
            self._last_columns = [desc[0] for desc in (result.description or [])]
            self._last_result = result
        else:
            self._cursor.execute(query, params)
            if self._cursor.description:
                self._last_columns = [desc[0] for desc in self._cursor.description]
        
        return self
    
    def fetchone(self) -> Optional[Any]:
        """Fetch one result"""
        if self.is_turso:
            rows = list(self._last_result)
            if rows:
                return TursoRowWrapper(rows[0], self._last_columns)
            return None
        return self._cursor.fetchone()
    
    def fetchall(self) -> List[Any]:
        """Fetch all results"""
        if self.is_turso:
            rows = list(self._last_result)
            return [TursoRowWrapper(row, self._last_columns) for row in rows]
        return self._cursor.fetchall()
    
    @property
    def rowcount(self):
        """Return number of affected rows"""
        if self.is_turso:
            return getattr(self._last_result, 'rowcount', 0)
        return self._cursor.rowcount
    
    def commit(self):
        """Commit the current transaction"""
        if self.conn:
            self.conn.commit()
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None


def get_db_connection() -> DatabaseConnection:
    """
    Get a database connection.
    Returns a DatabaseConnection that works with both SQLite and Turso.
    
    Usage:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidates WHERE id = ?", (id,))
        result = cursor.fetchone()
        conn.close()
    """
    db = DatabaseConnection()
    
    if USE_TURSO:
        import libsql_experimental as libsql
        db.conn = libsql.connect(
            TURSO_DATABASE_URL,
            auth_token=TURSO_AUTH_TOKEN
        )
    else:
        import sqlite3
        from pathlib import Path
        # Local SQLite fallback
        db_path = Path(__file__).parent / 'traqcheck.db'
        db.conn = sqlite3.connect(str(db_path))
        db.conn.row_factory = sqlite3.Row
        db.conn.execute("PRAGMA foreign_keys = ON")
        db._cursor = db.conn.cursor()
    
    return db
