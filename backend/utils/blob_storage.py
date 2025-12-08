"""
Vercel Blob Storage Utility
Handles file uploads and downloads using Vercel Blob storage.
"""

import os
from typing import Optional, Dict, Any


def upload_to_blob(file_bytes: bytes, filename: str, folder: str = "uploads") -> Dict[str, Any]:
    """
    Upload a file to Vercel Blob storage.
    
    Args:
        file_bytes: The file content as bytes
        filename: Name of the file
        folder: Folder path in blob storage (default: "uploads")
    
    Returns:
        Dict with 'success', 'url', 'pathname' or 'error'
    """
    try:
        from vercel_blob import put
        
        # Construct the blob path
        blob_path = f"{folder}/{filename}"
        
        # Upload to Vercel Blob
        result = put(
            pathname=blob_path,
            body=file_bytes,
            options={"access": "public"}  # Make files publicly accessible
        )
        
        return {
            "success": True,
            "url": result.get("url"),
            "pathname": result.get("pathname"),
            "size": len(file_bytes)
        }
        
    except ImportError:
        # Fallback for local development without vercel-blob
        return {
            "success": False,
            "error": "vercel-blob package not available (local development)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def delete_from_blob(url: str) -> Dict[str, Any]:
    """
    Delete a file from Vercel Blob storage.
    
    Args:
        url: The blob URL to delete
    
    Returns:
        Dict with 'success' or 'error'
    """
    try:
        from vercel_blob import delete
        
        delete(url)
        return {"success": True}
        
    except ImportError:
        return {
            "success": False,
            "error": "vercel-blob package not available"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def is_blob_enabled() -> bool:
    """Check if Vercel Blob is configured (has token)."""
    return bool(os.getenv("BLOB_READ_WRITE_TOKEN"))
