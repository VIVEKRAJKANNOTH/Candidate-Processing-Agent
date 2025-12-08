"""
Database utility functions for TraqCheck
Re-exports from database.connection for backward compatibility
"""
from database.connection import get_db_connection, DatabaseConnection

__all__ = ['get_db_connection', 'DatabaseConnection']
