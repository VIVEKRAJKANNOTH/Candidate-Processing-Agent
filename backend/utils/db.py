"""
Database utility functions for TraqCheck
"""
import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATABASE = os.path.join(BASE_DIR, 'database', 'traqcheck.db')


def get_db_connection():
    """Create database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
