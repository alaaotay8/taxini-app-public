"""
Supabase client configuration and utilities.
"""

from supabase import create_client, Client
from src.core.settings import settings
from typing import Optional
import uuid
import mimetypes
import logging

logger = logging.getLogger(__name__)

# Global client instance - initialized on demand
supabase: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Get configured Supabase client with environment safety.
    
    Raises:
        RuntimeError: If required Supabase environment variables are missing
    """
    if not settings.supabase_url or not settings.supabase_api_key:
        raise RuntimeError(
            "Supabase configuration missing. Set TAXINI_SUPABASE_URL and "
            "TAXINI_SUPABASE_API_KEY environment variables before using Supabase features."
        )
    return create_client(settings.supabase_url, settings.supabase_api_key)


def ensure_supabase_client() -> Client:
    """Ensure global supabase client is initialized."""
    global supabase
    if supabase is None:
        supabase = get_supabase_client()
    return supabase


# Try to initialize global client safely
try:
    if settings.supabase_url and settings.supabase_api_key:
        supabase = get_supabase_client()
        logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.warning(f"Supabase client initialization deferred: {e}")
    supabase = None


def upload_file_to_bucket(bucket: str, file_bytes: bytes, filename: str, content_type: Optional[str] = None, make_public: bool = True) -> Optional[str]:
    """Upload raw bytes to a Supabase storage bucket and return a public URL (or signed URL).

    - bucket: target bucket name
    - file_bytes: file content as bytes
    - filename: original filename (used to build storage path)
    - content_type: optional MIME type; guessed if not provided
    - make_public: if True, returns the public URL using get_public_url
    Returns: public URL string on success, None on failure
    """
    # generate unique path to avoid collisions
    ext = ''
    if '.' in filename:
        ext = filename.split('.')[-1]
    unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    path = f"uploads/{unique_name}"

    # guess content type
    if not content_type:
        content_type, _ = mimetypes.guess_type(filename)

    try:
        # Ensure we have a working client
        client = ensure_supabase_client()
        storage = client.storage
        bucket_ref = storage.from_(bucket)
        # upload accepts file-like or bytes depending on client version
        res = bucket_ref.upload(path, file_bytes, {'content-type': content_type} if content_type else None)
        
        # check error - different supabase client versions handle errors differently
        if hasattr(res, 'error') and res.error:
            logger.error(f"Upload error: {res.error}")
            return None
        if res and getattr(res, 'status_code', None) and res.status_code >= 400:
            logger.error(f"Upload failed with status: {res.status_code}")
            return None

        if make_public:
            public = bucket_ref.get_public_url(path)
            # get_public_url returns a dict like { 'publicURL': '...' } or similar depending on client
            if isinstance(public, dict):
                return public.get('publicURL') or public.get('public_url')
            # some versions return a string directly
            if isinstance(public, str):
                return public
            return getattr(public, 'publicURL', None) or getattr(public, 'public_url', None)

        # fallback: create signed URL for short-lived access
        signed = bucket_ref.create_signed_url(path, 60 * 60)  # 1 hour
        if isinstance(signed, dict):
            return signed.get('signedURL') or signed.get('signed_url')
        return getattr(signed, 'signedURL', None) or getattr(signed, 'signed_url', None)
    except Exception as e:
        logger.error(f"Storage upload exception: {e}")
        return None
