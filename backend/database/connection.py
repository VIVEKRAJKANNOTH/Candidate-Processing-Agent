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
    """
    Wrapper to make Turso rows accessible by column name like sqlite3.Row.
    Handles various row formats from libsql_experimental.
    """
    def __init__(self, row, columns=None):
        # Handle different row types from libsql
        if isinstance(row, dict):
            # Row is already a dictionary
            self._data = row
        elif hasattr(row, '_asdict'):
            # Row is a namedtuple
            self._data = row._asdict()
        elif hasattr(row, 'keys'):
            # Row has keys method
            self._data = dict(row)
        elif columns and hasattr(row, '__iter__'):
            # Row is a tuple/list, use provided columns
            row_list = list(row) if not isinstance(row, (list, tuple)) else row
            self._data = dict(zip(columns, row_list))
        else:
            # Fallback - try to convert to dict
            try:
                self._data = dict(row)
            except (TypeError, ValueError):
                self._data = {}
    
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


class DatabaseConnection:
    """
    Unified database connection that works with both SQLite and Turso.
    Provides a common interface regardless of the backend.
    """
    
    def __init__(self):
        self.conn = None
        self.is_turso = USE_TURSO
        self._last_columns = []
        self._last_rows = []
        self._fetch_index = 0
        self._rowcount = 0
    
    def cursor(self):
        """Return self as cursor for compatibility with sqlite3 patterns"""
        return self
    
    def execute(self, query: str, params: Tuple = ()) -> 'DatabaseConnection':
        """Execute a query with parameters"""
        if self.is_turso:
            # Turso uses libsql - execute and fetch all rows immediately
            result = self.conn.execute(query, params)
            
            # Try to get column names from description
            self._last_columns = []
            if result.description:
                self._last_columns = [desc[0] for desc in result.description]
            
            # Fetch all rows immediately
            raw_rows = result.fetchall()
            self._last_rows = raw_rows
            self._fetch_index = 0
            self._rowcount = len(raw_rows)
            
        else:
            self._cursor.execute(query, params)
            if self._cursor.description:
                self._last_columns = [desc[0] for desc in self._cursor.description]
        
        return self
    
    def fetchone(self) -> Optional[Any]:
        """Fetch one result"""
        if self.is_turso:
            if self._fetch_index < len(self._last_rows):
                row = self._last_rows[self._fetch_index]
                self._fetch_index += 1
                return TursoRowWrapper(row, self._last_columns)
            return None
        return self._cursor.fetchone()
    
    def fetchall(self) -> List[Any]:
        """Fetch all results"""
        if self.is_turso:
            remaining = self._last_rows[self._fetch_index:]
            self._fetch_index = len(self._last_rows)
            return [TursoRowWrapper(row, self._last_columns) for row in remaining]
        return self._cursor.fetchall()
    
    @property
    def rowcount(self):
        """Return number of affected rows"""
        if self.is_turso:
            return self._rowcount
        return self._cursor.rowcount
    
    def commit(self):
        """Commit the current transaction"""
        if self.conn:
            self.conn.commit()
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            # Turso libsql connections may not have close method
            if hasattr(self.conn, 'close'):
                try:
                    self.conn.close()
                except Exception:
                    pass
            self.conn = None


def get_db_connection() -> DatabaseConnection:
    """
    Get a database connection.
    Returns a DatabaseConnection that works with both SQLite and Turso.
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
        db_path = Path(__file__).parent / 'traqcheck.db'
        db.conn = sqlite3.connect(str(db_path))
        db.conn.row_factory = sqlite3.Row
        db.conn.execute("PRAGMA foreign_keys = ON")
        db._cursor = db.conn.cursor()
    
    return db
