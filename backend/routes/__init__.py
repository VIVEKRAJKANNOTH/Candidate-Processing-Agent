"""
Routes package for TraqCheck backend
"""
from .candidates import candidates_bp
from .documents import documents_bp
from .public import public_bp

__all__ = ['candidates_bp', 'documents_bp', 'public_bp']
